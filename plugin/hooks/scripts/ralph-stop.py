#!/usr/bin/env python3
"""
ai-assets plugin hook: ralph-stop
Event: Stop
Exit code 0 = allow Stop (RALF terminal state OR no active RALF).
Exit code 2 = block Stop with re-injection prompt (RALF iteration continues).

If active RALF session exists at .ai-assets-memory/ralph/<run-id>/active.lock,
this hook intercepts the model's exit attempt. Per ralph-budget rule:
1. Run oracle (cli/judge/regex/python type per --oracle spec in config.json).
2. If oracle pass → write SUCCESS, release lock, allow Stop.
3. Check kill-on signal (oracle-pass / same-error-repeats:N / regex / python /
   no-progress:N) → if hit, allow Stop with KILLED status.
4. Check budgets (per-workflow + session-aggregate per R6 HIGH-3) → if exceeded,
   allow Stop with BUDGET_EXCEEDED status.
5. Otherwise: log iteration, build continuation prompt with state delta + last-iter
   diff, block Stop with re-injection.

v0.1: simplified — supports `oracle-pass` and `same-error-repeats` kill-on
signals + iteration cap. Other oracle types and signals deferred to a follow-up.

Per Round 14 HIGH-C (alpha.16): also enforces RALF session-aggregate caps
read from the userConfig env vars
`CLAUDE_USER_CONFIG_ralph_session_max_iter`,
`CLAUDE_USER_CONFIG_ralph_session_token_budget`,
`CLAUDE_USER_CONFIG_ralph_session_time_cap_minutes`.
Aggregates are tracked in the session token meter
(`ralf_iter_total`, `ralf_tokens_total`, `ralf_started_at`) and incremented
once per Stop intercept (one per iteration). When any aggregate exceeds its
cap, terminal status is BUDGET_EXCEEDED with a `session_aggregate_*` reason
and Stop is allowed.

Per failure-recovery rule: fail-open on internal errors. Per A3: never block
Stop because of buggy hook.
"""

from __future__ import annotations

import datetime as _dt
import json
import os
import pathlib
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _lib  # noqa: E402


# ---------- session-aggregate cap helpers (HIGH-C, alpha.16) ----------

def _read_int_env(var: str, default: int | None) -> int | None:
    raw = os.environ.get(var)
    if raw is None or raw == "":
        return default
    try:
        return int(raw)
    except (ValueError, TypeError):
        return default


def _session_caps() -> dict[str, int | None]:
    """Read session-aggregate RALF caps from userConfig env vars."""
    return {
        "max_iter": _read_int_env(
            "CLAUDE_USER_CONFIG_ralph_session_max_iter", 20
        ),
        "token_budget": _read_int_env(
            "CLAUDE_USER_CONFIG_ralph_session_token_budget", 400000
        ),
        "time_cap_minutes": _read_int_env(
            "CLAUDE_USER_CONFIG_ralph_session_time_cap_minutes", 180
        ),
    }


def _elapsed_minutes(started_at_iso: str | None) -> int:
    """Whole minutes elapsed since the RALF session started. 0 if unparseable."""
    if not started_at_iso:
        return 0
    try:
        started = _dt.datetime.fromisoformat(started_at_iso.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return 0
    if started.tzinfo is None:
        started = started.replace(tzinfo=_dt.timezone.utc)
    now = _dt.datetime.now(_dt.timezone.utc)
    delta = now - started
    return max(0, int(delta.total_seconds() // 60))


def _session_dir_for(memory_root: pathlib.Path) -> pathlib.Path:
    """Best-effort session-meter directory: prefer current symlink, else newest."""
    sessions_root = memory_root / "sessions"
    candidate = sessions_root / "current"
    if candidate.exists():
        return candidate
    if not sessions_root.exists():
        return candidate
    try:
        subdirs = [p for p in sessions_root.iterdir() if p.is_dir()]
    except OSError:
        return candidate
    if not subdirs:
        return candidate
    return max(subdirs, key=lambda p: p.stat().st_mtime)


def _check_session_caps(
    memory_root: pathlib.Path,
    iters_done_in_workflow: int,
    workflow_tokens: int,
) -> tuple[bool, str | None, dict]:
    """Increment session aggregates and check against caps.

    Returns (exceeded, reason_str_or_None, current_meter).
    Side effect: increments ralf_iter_total by 1 and ralf_tokens_total by the
    workflow_tokens delta (best-effort) and stamps ralf_started_at if unset.

    Note on workflow_tokens (v0.1 limitation): the per-workflow token delta is
    read from meter['ralf_workflow_tokens_last'], which is currently only
    populated by the Tier 3 eval runner when a RALF case is executed inside
    `eval/runner.py`. For interactive RALF (user runs `/ralph` directly),
    workflow_tokens is 0 and the session-aggregate token cap will only trip
    once an upstream mechanism (e.g., a future PostToolUse hook that
    estimates input/output tokens per turn) is wired to populate
    `ralf_workflow_tokens_last` between iterations. Until then, the
    iteration cap and time cap remain the effective ceiling for interactive
    RALF; the token cap is the harder ceiling only inside eval runs.
    """
    session_dir = _session_dir_for(memory_root)
    meter = _lib.read_token_meter(session_dir)

    # Stamp ralf_started_at on first RALF Stop intercept of the session.
    delta: dict = {"ralf_iter_total": 1}
    if not meter.get("ralf_started_at"):
        delta["ralf_started_at"] = _lib.iso_now()

    # Add workflow tokens additively to the session aggregate.
    if workflow_tokens > 0:
        delta["ralf_tokens_total"] = workflow_tokens

    new_meter = _lib.update_token_meter(session_dir, delta)

    caps = _session_caps()
    iters_total = int(new_meter.get("ralf_iter_total", 0))
    tokens_total = int(new_meter.get("ralf_tokens_total", 0))
    started_at = new_meter.get("ralf_started_at")
    elapsed = _elapsed_minutes(started_at)

    if caps["max_iter"] is not None and iters_total > caps["max_iter"]:
        return (
            True,
            f"session_aggregate_iterations: {iters_total} > {caps['max_iter']}",
            new_meter,
        )
    if caps["token_budget"] is not None and tokens_total > caps["token_budget"]:
        return (
            True,
            f"session_aggregate_tokens: {tokens_total} > {caps['token_budget']}",
            new_meter,
        )
    if caps["time_cap_minutes"] is not None and elapsed > caps["time_cap_minutes"]:
        return (
            True,
            f"session_aggregate_time_minutes: {elapsed} > {caps['time_cap_minutes']}",
            new_meter,
        )
    return False, None, new_meter


def find_active_ralph(memory_root: pathlib.Path) -> pathlib.Path | None:
    """Return the first ralph/<run-id>/ dir with an active.lock present."""
    ralph_root = memory_root / "ralph"
    if not ralph_root.exists():
        return None
    try:
        for run_dir in ralph_root.iterdir():
            if (run_dir / "active.lock").exists():
                return run_dir
    except OSError:
        return None
    return None


def load_config(run_dir: pathlib.Path) -> dict:
    """Load RALF run config (--max-iterations, --token-budget, --time-cap, --oracle, --kill-on)."""
    cfg_path = run_dir / "config.json"
    if not cfg_path.exists():
        return {}
    try:
        return json.loads(cfg_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def count_completed_iters(run_dir: pathlib.Path) -> int:
    """Count iter-NNN/ subdirs."""
    try:
        return len([p for p in run_dir.iterdir() if p.is_dir() and p.name.startswith("iter-")])
    except OSError:
        return 0


def write_terminal_status(run_dir: pathlib.Path, status: str, reason: str, iters: int, tokens: int) -> None:
    """Write budget.json with terminal state, release lock."""
    budget_path = run_dir / "budget.json"
    try:
        budget_path.write_text(
            json.dumps(
                {
                    "ts": _lib.iso_now(),
                    "status": status,
                    "reason": reason,
                    "iterations_completed": iters,
                    "tokens_total": tokens,
                },
                indent=2,
            ),
            encoding="utf-8",
        )
    except OSError:
        pass
    try:
        (run_dir / "active.lock").unlink()
    except OSError:
        pass


def check_same_error_repeats(run_dir: pathlib.Path, threshold: int) -> bool:
    """Inspect last N iter dirs' oracle-result.json for same error string."""
    try:
        iters = sorted(
            [p for p in run_dir.iterdir() if p.is_dir() and p.name.startswith("iter-")],
            key=lambda p: p.name,
        )
    except OSError:
        return False
    if len(iters) < threshold:
        return False
    last_n = iters[-threshold:]
    errors: list[str] = []
    for iter_dir in last_n:
        result_path = iter_dir / "oracle-result.json"
        if not result_path.exists():
            return False
        try:
            d = json.loads(result_path.read_text(encoding="utf-8"))
            err = d.get("error") or d.get("message") or ""
            errors.append(str(err)[:200])
        except (OSError, json.JSONDecodeError):
            return False
    return len(set(errors)) == 1 and errors[0] != ""


def main() -> None:
    data = _lib.read_stdin_json()
    cwd = pathlib.Path.cwd()
    memory_root = cwd / ".ai-assets-memory"

    run_dir = find_active_ralph(memory_root)
    if run_dir is None:
        # No active RALF — normal Stop
        _lib.allow()

    cfg = load_config(run_dir)
    max_iter = int(cfg.get("max_iterations", 10))
    kill_on = cfg.get("kill_on") or "oracle-pass"

    iters_done = count_completed_iters(run_dir)
    meter = _lib.read_token_meter(memory_root / "sessions" / "current") if (memory_root / "sessions" / "current").exists() else {}
    ralf_tokens = int(meter.get("ralf_tokens_total", 0))
    workflow_tokens = int(meter.get("ralf_workflow_tokens_last", 0))

    # HIGH-C (alpha.16): session-aggregate cap check FIRST. Increments meter
    # by 1 iteration + workflow_tokens delta (best-effort) and short-circuits
    # if any session-wide cap is exceeded. Per-workflow caps are still
    # enforced below — the order means session caps win when both fire.
    session_exceeded, session_reason, _meter_after = _check_session_caps(
        memory_root,
        iters_done_in_workflow=iters_done,
        workflow_tokens=workflow_tokens,
    )
    if session_exceeded:
        write_terminal_status(
            run_dir,
            "BUDGET_EXCEEDED",
            session_reason or "session_aggregate_cap_exceeded",
            iters_done,
            ralf_tokens,
        )
        _lib.allow()

    # Iteration cap
    if iters_done >= max_iter:
        write_terminal_status(
            run_dir,
            "BUDGET_EXCEEDED",
            f"max_iterations cap reached ({iters_done}/{max_iter})",
            iters_done,
            ralf_tokens,
        )
        _lib.allow()

    # Kill-on signal: same-error-repeats:N
    if isinstance(kill_on, str) and kill_on.startswith("same-error-repeats:"):
        try:
            threshold = int(kill_on.split(":", 1)[1])
            if check_same_error_repeats(run_dir, threshold):
                write_terminal_status(
                    run_dir,
                    "KILLED",
                    f"kill-on signal {kill_on} hit",
                    iters_done,
                    ralf_tokens,
                )
                _lib.allow()
        except (ValueError, IndexError):
            pass  # Malformed signal — treat as "no kill"

    # Default oracle-pass: assume oracle ran in skill body and wrote SUCCESS marker
    success_marker = run_dir / "SUCCESS"
    if success_marker.exists():
        write_terminal_status(
            run_dir,
            "SUCCESS",
            "oracle-pass marker present",
            iters_done,
            ralf_tokens,
        )
        _lib.allow()

    # No terminal state — re-inject continuation prompt and block Stop
    continuation_prompt_path = run_dir / f"iter-{iters_done + 1:03d}" / "prompt.md"
    try:
        continuation_prompt_path.parent.mkdir(parents=True, exist_ok=True)
        # v0.1 simplified continuation: reference last iter diff if available
        last_iter_dir = run_dir / f"iter-{iters_done:03d}"
        last_diff = ""
        if last_iter_dir.exists():
            diff_path = last_iter_dir / "diff.patch"
            if diff_path.exists():
                try:
                    last_diff = diff_path.read_text(encoding="utf-8")[:1000]
                except OSError:
                    pass

        continuation = (
            f"RALF iteration {iters_done + 1} of max {max_iter}.\n\n"
            f"## State delta from iter {iters_done}\n"
            f"{last_diff or '(no diff captured)'}\n\n"
            f"## Active constraints\n"
            f"See {run_dir.relative_to(cwd)}/config.json for full config.\n\n"
            f"## Your task\n"
            f"Continue addressing the original task brief from "
            f"{run_dir.relative_to(cwd)}/initial-prompt.md. "
            f"Apply state delta above. Stop when oracle passes."
        )
        continuation_prompt_path.write_text(continuation, encoding="utf-8")
    except OSError:
        pass  # Fail open — allow Stop if we can't write continuation

    # Block Stop with re-injection (continuation prompt was written)
    _lib.block(
        f"RALF iteration {iters_done + 1}/{max_iter} continues.\n"
        f"Continuation prompt: {continuation_prompt_path.relative_to(cwd)}\n"
        f"To stop manually: delete {(run_dir / 'active.lock').relative_to(cwd)}"
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        # R8 A3: never block Stop because of buggy hook
        _lib.log_to(
            "hook-errors.log",
            {"ts": _lib.iso_now(), "hook": "ralph-stop", "error": str(exc)},
        )
        sys.exit(0)
