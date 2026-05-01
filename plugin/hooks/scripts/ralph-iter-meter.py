#!/usr/bin/env python3
"""
ai-assets plugin hook: ralph-iter-meter
Event: PostToolUse (matcher: .* — runs after every tool call)
Exit code 0 = always allow.

Phase 4 #3 (v0.1.6): per-iteration RALF token measurement.

Closes the v0.1 limitation noted in `ralph-stop.py::_check_session_caps`:
> the per-workflow token delta is read from meter['ralf_workflow_tokens_last'],
> which is currently only populated by the Tier 3 eval runner... For interactive
> RALF (user runs `/ralph` directly), workflow_tokens is 0 and the
> session-aggregate token cap will only trip once an upstream mechanism
> (e.g., a future PostToolUse hook that estimates input/output tokens per turn)
> is wired to populate `ralf_workflow_tokens_last` between iterations.

This is that hook. After every tool call, while a RALF run is active:

  1. Detect active RALF via _lib.find_active_ralph().
  2. If none, exit 0 (no-op — most tool calls are not in a RALF loop).
  3. Estimate tokens for this tool call: chars(tool_input) +
     chars(tool_response_str) divided by 4 (Anthropic's published average for
     English text). Best-effort proxy, not exact API token count.
  4. Increment session token meter:
       - `ralf_iter_tokens_partial` += estimate (consumed + reset by ralph-stop)
       - `ralf_iter_tokens_running` += estimate (cumulative within the workflow,
         for forensics; also reset by ralph-stop on iteration boundary)
       - `tokens_in_total`, `tokens_out_total` += per-direction breakdown
         (separate from RALF — accumulates across the whole session)
  5. Exit 0 unconditionally.

ralph-stop.py reads `ralf_iter_tokens_partial` as the workflow_tokens delta on
Stop intercept, then resets it to 0 — so each RALF iteration sees its own
per-iteration token spend, and session-aggregate caps now actually fire for
interactive RALF (not only inside eval-runner cases).

Per failure-recovery rule: fail-open on internal errors. Per A3: never block
tool use because of buggy hook. This is a meter, not a guard.
"""

from __future__ import annotations

import os
import pathlib
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _lib  # noqa: E402


def _stringify_tool_io(value) -> str:
    """Coerce arbitrary tool_input/tool_response value to a string for sizing.

    Tool payloads can be dict, list, str, or None. We serialize complex shapes
    to their JSON repr (compactly) so chars correlate with what the model
    actually saw / produced.
    """
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    try:
        import json
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    except (TypeError, ValueError):
        try:
            return str(value)
        except Exception:
            return ""


def main() -> None:
    data = _lib.read_stdin_json()
    data = _lib.normalize_hook_input(data)

    cwd = pathlib.Path.cwd()
    memory_root = cwd / ".ai-assets-memory"

    # Cheap precondition: skip everything if no RALF run is active.
    run_dir = _lib.find_active_ralph(memory_root)
    if run_dir is None:
        _lib.allow()

    # Estimate tokens from this tool call. We separate input vs output so the
    # cumulative session counters can distinguish prompt-side from response-side
    # spend. RALF-specific accumulators sum both — a runaway iteration burns
    # tokens regardless of direction.
    tool_input_str = _stringify_tool_io(data.get("tool_input"))
    tool_response_str = _stringify_tool_io(data.get("tool_response"))

    tokens_in = _lib.estimate_tokens_from_chars(tool_input_str)
    tokens_out = _lib.estimate_tokens_from_chars(tool_response_str)
    tokens_total = tokens_in + tokens_out

    if tokens_total <= 0:
        # Nothing to record (e.g., empty payload). Still fall through to allow().
        _lib.allow()

    # Best-effort write to the session-current meter. _lib.update_token_meter
    # creates the dir if missing and is fail-open.
    session_dir = memory_root / "sessions" / "current"
    delta = {
        "ralf_iter_tokens_partial": tokens_total,
        "ralf_iter_tokens_running": tokens_total,
        "tokens_in_total": tokens_in,
        "tokens_out_total": tokens_out,
    }
    _lib.update_token_meter(session_dir, delta)

    _lib.allow()


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        # _lib.allow() raises SystemExit(0) — pass through.
        raise
    except Exception as exc:
        # Per failure-recovery rule + A3: never block tool use because of a
        # buggy meter hook. Log and exit 0.
        _lib.log_to(
            "hook-errors.log",
            {"ts": _lib.iso_now(), "hook": "ralph-iter-meter", "error": str(exc)},
        )
        sys.exit(0)
