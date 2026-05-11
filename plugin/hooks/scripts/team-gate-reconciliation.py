#!/usr/bin/env python3
"""
ai-assets plugin hook: team-gate-reconciliation
Events: TaskCompleted, TeammateIdle (when available)
Exit code 0 = always allow (advisory hook — never blocks).

Path B reliability hook. Runs read-only disk-state reconciliation at every
task transition so the Lead has ground-truth evidence even when a teammate
goes silent-but-complete (alpha.31 sub-case c). Writes a JSON envelope to
.ai-assets-memory/sessions/<sid>/team-envelopes/<task_id>-<ts>.json so the
Lead can stream it via Monitor without depending on the team-bus.

Closes feedback items F2 (silent-but-complete) + F9 (out-of-the-box
file-channel) + F10 (auto-reconciliation at gate transitions) from the
v0.3.10 field debrief.

Output envelope schema:

  {
    "event": "TaskCompleted" | "TeammateIdle",
    "ts": "2026-05-11T08:31:42Z",
    "session_id": "<sid>",
    "task_id": "<task-id>",
    "task_subject": "<subject>",
    "task_status": "<status>",
    "teammate_name": "<name>",
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


def main() -> None:
    data = _lib.read_stdin_json()
    sid = str(data.get("session_id") or data.get("sessionId") or "unknown")
    sid = sid.replace(":", "-").replace(".", "-")
    event = data.get("hook_event_name", "TaskEvent")

    task_id = data.get("task_id") or data.get("taskId") or "unknown"
    subject = data.get("subject") or data.get("task_subject") or ""
    status = data.get("status") or ""
    teammate = data.get("teammate_name") or data.get("teammate") or ""

    cwd = pathlib.Path.cwd()
    snapshot = _disk_snapshot(cwd)

    envelope = {
        "event": event,
        "ts": _lib.iso_now(),
        "session_id": sid,
        "task_id": str(task_id),
        "task_subject": subject,
        "task_status": status,
        "teammate_name": teammate,
        "disk_state": snapshot,
    }

    # Write to deterministic file-channel path that the Lead can Monitor
    out_dir = cwd / ".ai-assets-memory" / "sessions" / sid / "team-envelopes"
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
    _lib.log_to(f"sessions/{sid}/runs.jsonl", {
        "ts": envelope["ts"],
        "event": f"gate-reconciliation:{event}",
        "session_id": sid,
        "task_id": envelope["task_id"],
        "changed_files_count": len(snapshot["changed_files"]) if snapshot else 0,
    })

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
