#!/usr/bin/env python3
"""
ai-assets plugin hook: session-end-finalize
Event: SessionEnd
Exit code 0 = always allow.

Per memory-discipline retention rules:
1. Read sessions/<id>/runs.jsonl (L3); compute summary.
2. Append session summary line to L4 runs.jsonl (cross-session aggregate).
3. Release any dangling RALF locks (.ai-assets-memory/ralph/<run-id>/active.lock).
4. Optionally delete L3 sessions/<id>/ after summary write (per retention rule
   "session lifetime; archived to L4 then sessions/<id> deleted"). v0.1: keep
   sessions/<id>/ for 7 days; deletion handled separately to avoid data loss.
"""

from __future__ import annotations

import os
import pathlib
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _lib  # noqa: E402


def main() -> None:
    data = _lib.read_stdin_json()
    sid = str(data.get("session_id") or "unknown").replace(":", "-").replace(".", "-")

    cwd = pathlib.Path.cwd()
    memory_root = cwd / ".ai-assets-memory"
    session_dir = memory_root / "sessions" / sid

    if not session_dir.exists():
        _lib.allow()

    # Read meter for summary
    meter = _lib.read_token_meter(session_dir)

    # Count events in L3 runs.jsonl
    runs_path = session_dir / "runs.jsonl"
    event_count = 0
    if runs_path.exists():
        try:
            with runs_path.open(encoding="utf-8") as f:
                event_count = sum(1 for _ in f)
        except OSError:
            pass

    # Append session summary to L4 runs.jsonl
    summary = {
        "ts": _lib.iso_now(),
        "event": "SessionEnd",
        "session_id": sid,
        "tokens_in_total": meter.get("tokens_in_total", 0),
        "tokens_out_total": meter.get("tokens_out_total", 0),
        "ralf_iter_total": meter.get("ralf_iter_total", 0),
        "ralf_tokens_total": meter.get("ralf_tokens_total", 0),
        "session_event_count": event_count,
        "session_started_at": meter.get("session_started_at"),
    }
    _lib.log_to("runs.jsonl", summary)

    # Release dangling RALF locks
    ralph_root = memory_root / "ralph"
    if ralph_root.exists():
        try:
            for run_dir in ralph_root.iterdir():
                if not run_dir.is_dir():
                    continue
                lock_path = run_dir / "active.lock"
                if lock_path.exists():
                    # Mark as orphan (session ended without RALF terminal state)
                    orphan_marker = run_dir / "orphan-by-session-end.txt"
                    try:
                        orphan_marker.write_text(
                            f"Session {sid} ended {_lib.iso_now()} with active RALF lock. Lock released by session-end-finalize hook.",
                            encoding="utf-8",
                        )
                        lock_path.unlink()
                    except OSError:
                        pass
        except OSError:
            pass

    _lib.allow()


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        _lib.log_to(
            "hook-errors.log",
            {"ts": _lib.iso_now(), "hook": "session-end-finalize", "error": str(exc)},
        )
        sys.exit(0)
