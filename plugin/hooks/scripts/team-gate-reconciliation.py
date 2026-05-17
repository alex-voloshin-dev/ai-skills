#!/usr/bin/env python3
"""
ai-skills plugin hook: team-gate-reconciliation
Events: TaskCompleted, TeammateIdle, idle_notification (fall-through)
Exit code 0 = always allow (advisory hook — never blocks).

Path B reliability hook. Runs read-only disk-state reconciliation at every
task transition so the Lead has ground-truth evidence even when a teammate
goes silent-but-complete (alpha.31 sub-case c). Writes a JSON envelope to
.ai-skills-memory/sessions/<sid>/team-envelopes/<task_id>-<ts>.json so the
Lead can stream it via Monitor without depending on the team-bus.

Closes feedback items F2 (silent-but-complete) + F9 (out-of-the-box
file-channel) + F10 (auto-reconciliation at gate transitions) from the
v0.3.10 field debrief.

Retrospective hardening (v0.3.14 — findings A + H):
  Finding A: when bus-delivered task state is absent/empty the hook now
    reconciles gate state from the file-channel envelope dir (G7-*.json and
    findings-reviewer-*.json) as the authoritative gate signal, so the Lead
    has ground-truth evidence without relying on the team bus.
  Finding H: idle_notification is now accepted as a valid teammate-quiesced
    signal alongside shutdown_response and TeammateIdle so file-channel-
    exclusive teammates (e.g. reviewer) do not stall teardown reconciliation.

Output envelope schema (fields marked NEW added by v0.3.14 hardening):

  {
    "event": "TaskCompleted" | "TeammateIdle" | "idle_notification",
    "ts": "2026-05-11T08:31:42Z",
    "session_id": "<sid>",
    "task_id": "<task-id>",
    "task_subject": "<subject>",
    "task_status": "<status>",
    "teammate_name": "<name>",
    "teammate_quiesced": true | false,       # NEW (Finding H)
    "bus_state_absent": true | false,        # NEW (Finding A)
    "file_channel_reconciliation": { ... },  # NEW, present when bus_state_absent
    "disk_state": {
      "branch": "<git-branch>",
      "head": "<sha-short>",
      "status_short": ["M src/foo.py", "?? new.md"],
      "diff_stat": [" src/foo.py | 23 ++++++"],
      "changed_files": ["src/foo.py"]
    }
  }

If git is not available or this is not a git repo, disk_state is null and
the envelope still records the event for liveness tracking.
"""

from __future__ import annotations

import json
import os
import pathlib
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _lib  # noqa: E402


# ---------------------------------------------------------------------------
# Finding H: events that signal a teammate has quiesced.
# idle_notification is now accepted alongside shutdown_response and TeammateIdle
# so file-channel-exclusive teammates (e.g. reviewer — the reliably last role)
# do not stall teardown reconciliation when the bus never delivers their ack.
# ---------------------------------------------------------------------------
_QUIESCED_EVENTS: frozenset[str] = frozenset(
    {"TeammateIdle", "idle_notification", "shutdown_response"}
)

# Status values that also indicate quiesced, in case the event name differs
# but the payload's status field carries the signal.
_QUIESCED_STATUSES: frozenset[str] = frozenset(
    {"idle_notification", "shutdown_response", "idle", "quiesced"}
)


# ---------------------------------------------------------------------------
# Disk snapshot helpers (unchanged from original)
# ---------------------------------------------------------------------------


def _git(args: list[str], cwd: pathlib.Path) -> str:
    try:
        out = subprocess.run(
            ["git", *args],
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=5,
        )
        return out.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return ""


def _disk_snapshot(cwd: pathlib.Path) -> dict | None:
    if not (cwd / ".git").exists():
        return None
    branch = _git(["rev-parse", "--abbrev-ref", "HEAD"], cwd) or "unknown"
    head = _git(["rev-parse", "--short", "HEAD"], cwd) or "unknown"
    status_short = _git(["status", "--short"], cwd)
    diff_stat = _git(["diff", "--stat"], cwd)
    status_lines = [ln for ln in status_short.splitlines() if ln.strip()]
    diff_lines = [ln for ln in diff_stat.splitlines() if ln.strip()]
    changed = []
    for ln in status_lines:
        # status --short format: XY <path>
        parts = ln.split(maxsplit=1)
        if len(parts) == 2:
            changed.append(parts[1].strip().strip('"'))
    return {
        "branch": branch,
        "head": head,
        "status_short": status_lines[:50],
        "diff_stat": diff_lines[:50],
        "changed_files": changed[:50],
    }


# ---------------------------------------------------------------------------
# Finding A: bus-dead detection + file-channel reconciliation
# ---------------------------------------------------------------------------


def _bus_state_absent(data: dict) -> bool:
    """Return True when the stdin payload has no meaningful task state.

    This is the canonical indicator that the team→lead bus is dead (Finding A).

    - A completely empty payload ({}) is always treated as bus-dead.
    - A payload where all task-state fields (task_id, status, teammate_name,
      subject) are absent or empty is treated as bus-dead even if the event
      name itself was delivered (partial delivery).

    Existing callers with a full bus payload are unaffected: as long as at
    least one task-state field carries a non-empty value the bus is considered
    alive and reconciliation is skipped.
    """
    if not data:
        return True
    task_id = str(data.get("task_id") or data.get("taskId") or "").strip()
    status = str(data.get("status") or "").strip()
    teammate = str(data.get("teammate_name") or data.get("teammate") or "").strip()
    subject = str(data.get("subject") or data.get("task_subject") or "").strip()
    return not any([task_id, status, teammate, subject])


def _extract_role_from_filename(name: str) -> str:
    """Extract a role hint from a file-channel envelope filename.

    Handles:
      G7-developer-WP-7.json    → "developer"
      findings-reviewer-*.json  → "reviewer"
    """
    if name.startswith("G7-"):
        parts = name[3:].split("-")
        if parts:
            return parts[0]
    if "reviewer" in name:
        return "reviewer"
    return "unknown"


def _reconcile_from_file_channel(cwd: pathlib.Path, sid: str) -> dict:
    """Scan file-channel envelope dirs for G7-*.json + findings-reviewer-*.json.

    Called when the bus payload is absent/empty (Finding A). Returns a summary
    dict included in the output envelope as ``file_channel_reconciliation``.

    Always returns a well-formed dict (never raises) — strict fail-open per
    constraint 3: any internal error is logged to stderr and the function
    continues, returning whatever it collected before the error.

    Precedence:
      1. If ``sid`` is known, search that specific session dir first.
      2. Fallback: scan ALL session dirs under .ai-skills-memory/sessions/
         (covers the case where sid itself was not delivered by the bus).
    """
    result: dict = {
        "reconciled": False,
        "session_searched": sid,
        "envelopes_found": [],
        "errors": [],
    }
    try:
        memory_root = cwd / ".ai-skills-memory" / "sessions"
        if not memory_root.exists():
            return result

        # Build the ordered list of envelope dirs to scan.
        search_dirs: list[pathlib.Path] = []
        if sid and sid not in ("unknown", ""):
            sid_dir = memory_root / sid / "team-envelopes"
            if sid_dir.is_dir():
                search_dirs.append(sid_dir)

        # Fallback: scan all session dirs (handles unknown/missing sid).
        if not search_dirs:
            try:
                for session_dir in sorted(memory_root.iterdir()):
                    env_dir = session_dir / "team-envelopes"
                    if env_dir.is_dir():
                        search_dirs.append(env_dir)
            except OSError as exc:
                result["errors"].append(f"session-scan: {exc}")
                print(
                    f"[team-gate-reconciliation] session scan error: {exc}",
                    file=sys.stderr,
                )

        envelopes: list[dict] = []
        for env_dir in search_dirs:
            try:
                for glob_pattern in ("G7-*.json", "findings-reviewer-*.json"):
                    for fpath in sorted(env_dir.glob(glob_pattern)):
                        try:
                            raw = fpath.read_text(encoding="utf-8")
                            content: dict = json.loads(raw)
                            entry: dict = {
                                "file": fpath.name,
                                "status": content.get("status"),
                                "trace_id": content.get("trace_id"),
                                "role": (
                                    content.get("result", {}).get("role")
                                    or _extract_role_from_filename(fpath.name)
                                ),
                                "files_changed": content.get("result", {}).get(
                                    "files_changed", []
                                ),
                            }
                            envelopes.append(entry)
                        except (OSError, json.JSONDecodeError, ValueError) as exc:
                            msg = f"{fpath.name}: {exc}"
                            result["errors"].append(msg)
                            print(
                                f"[team-gate-reconciliation] envelope parse error: {msg}",
                                file=sys.stderr,
                            )
            except OSError as exc:
                msg = f"glob {env_dir}: {exc}"
                result["errors"].append(msg)
                print(
                    f"[team-gate-reconciliation] dir scan error: {msg}",
                    file=sys.stderr,
                )

        result["envelopes_found"] = envelopes[:100]  # cap to avoid oversized output
        result["reconciled"] = len(envelopes) > 0

    except Exception as exc:  # noqa: BLE001 — strict fail-open
        msg = f"reconcile: {exc}"
        result["errors"].append(msg)
        print(
            f"[team-gate-reconciliation] file-channel reconcile error: {exc}",
            file=sys.stderr,
        )

    return result


# ---------------------------------------------------------------------------
# Main entrypoint
# ---------------------------------------------------------------------------


def main() -> None:
    data = _lib.read_stdin_json()
    sid = str(data.get("session_id") or data.get("sessionId") or "unknown")
    sid = sid.replace(":", "-").replace(".", "-")
    event = data.get("hook_event_name", "TaskEvent")

    task_id = data.get("task_id") or data.get("taskId") or "unknown"
    subject = data.get("subject") or data.get("task_subject") or ""
    status = data.get("status") or ""
    teammate = data.get("teammate_name") or data.get("teammate") or ""

    # Finding H: idle_notification and shutdown_response are now valid quiesced
    # signals alongside TeammateIdle. Check both event name and status field so
    # the signal is detected regardless of which field carries it.
    teammate_quiesced: bool = (
        event in _QUIESCED_EVENTS
        or str(status).lower() in _QUIESCED_STATUSES
    )

    # Finding A: detect absent/empty bus state; used to decide whether to run
    # file-channel reconciliation.
    bus_absent: bool = _bus_state_absent(data)

    cwd = pathlib.Path.cwd()
    snapshot = _disk_snapshot(cwd)

    envelope: dict = {
        "event": event,
        "ts": _lib.iso_now(),
        "session_id": sid,
        "task_id": str(task_id),
        "task_subject": subject,
        "task_status": status,
        "teammate_name": teammate,
        "teammate_quiesced": teammate_quiesced,
        "bus_state_absent": bus_absent,
        "disk_state": snapshot,
    }

    # Finding A: when bus payload is absent/empty, reconcile from the file
    # channel so the Lead has ground-truth gate evidence without the team bus.
    if bus_absent:
        try:
            recon = _reconcile_from_file_channel(cwd, sid)
            envelope["file_channel_reconciliation"] = recon
        except Exception as exc:  # noqa: BLE001 — strict fail-open
            print(
                f"[team-gate-reconciliation] reconcile outer error: {exc}",
                file=sys.stderr,
            )
            envelope["file_channel_reconciliation"] = {
                "reconciled": False,
                "error": str(exc),
                "envelopes_found": [],
                "errors": [],
            }

    # Write to deterministic file-channel path that the Lead can Monitor
    out_dir = cwd / ".ai-skills-memory" / "sessions" / sid / "team-envelopes"
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        safe_task = str(task_id).replace("/", "_").replace(":", "-")
        ts_compact = _lib.iso_now().replace(":", "").replace("-", "")
        out_path = out_dir / f"{event}-{safe_task}-{ts_compact}.json"
        # Atomic write — tmp then rename so Monitor never sees partial JSON
        tmp_path = out_path.with_suffix(".json.tmp")
        tmp_path.write_text(
            json.dumps(envelope, separators=(",", ":"), ensure_ascii=False),
            encoding="utf-8",
        )
        os.replace(str(tmp_path), str(out_path))
    except OSError as exc:
        _lib.log_to(
            "hook-errors.log",
            {"ts": _lib.iso_now(), "hook": "team-gate-reconciliation", "error": str(exc)},
        )

    # Also append a compact line to runs.jsonl for the L3 audit trail
    _lib.log_to(
        f"sessions/{sid}/runs.jsonl",
        {
            "ts": envelope["ts"],
            "event": f"gate-reconciliation:{event}",
            "session_id": sid,
            "task_id": envelope["task_id"],
            "teammate_quiesced": teammate_quiesced,
            "bus_state_absent": bus_absent,
            "changed_files_count": len(snapshot["changed_files"]) if snapshot else 0,
        },
    )

    _lib.allow()


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        _lib.log_to(
            "hook-errors.log",
            {"ts": _lib.iso_now(), "hook": "team-gate-reconciliation", "error": str(exc)},
        )
        sys.exit(0)
