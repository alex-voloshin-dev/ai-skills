#!/usr/bin/env python3
"""
ai-assets plugin hook: task-event-log
Events: TaskCreated, TaskCompleted
Exit code 0 = always allow.

Logs TodoList events to .ai-assets-memory/sessions/<id>/runs.jsonl per
03-MEMORY-ARCHITECTURE.md L3 schema.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _lib  # noqa: E402


def main() -> None:
    data = _lib.read_stdin_json()
    sid = data.get("session_id") or data.get("sessionId") or "unknown"
    sid = str(sid).replace(":", "-").replace(".", "-")
    event = data.get("hook_event_name", "TaskEvent")

    entry = {
        "ts": _lib.iso_now(),
        "event": event,
        "session_id": sid,
        "task_id": data.get("task_id") or data.get("taskId"),
        "task_subject": data.get("subject") or data.get("task_subject"),
        "task_status": data.get("status"),
    }
    # Strip None values
    entry = {k: v for k, v in entry.items() if v is not None}

    _lib.log_to(f"sessions/{sid}/runs.jsonl", entry)
    _lib.allow()


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        _lib.log_to(
            "hook-errors.log",
            {"ts": _lib.iso_now(), "hook": "task-event-log", "error": str(exc)},
        )
        sys.exit(0)
