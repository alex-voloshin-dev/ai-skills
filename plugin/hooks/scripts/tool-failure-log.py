#!/usr/bin/env python3
"""
ai-assets plugin hook: tool-failure-log
Events: PostToolUseFailure, StopFailure
Exit code 0 = always allow.

Logs tool/turn failures to .ai-assets-memory/errors.log (separate from success
audit log). Captures duration_ms when present (Round 2 H3 + R5 Appendix A1
Anthropic April 2026 update).
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _lib  # noqa: E402


def main() -> None:
    data = _lib.read_stdin_json()
    data = _lib.normalize_hook_input(data)

    entry = {
        "ts": _lib.iso_now(),
        "severity": "ERROR",
        "event": data.get("hook_event_name", "Unknown"),
        "session_id": data.get("session_id"),
        "tool_name": data.get("tool_name"),
        "duration_ms": data.get("duration_ms"),
        "error": data.get("error") or data.get("tool_response", {}).get("error") if isinstance(data.get("tool_response"), dict) else None,
    }
    entry = {k: v for k, v in entry.items() if v is not None}

    _lib.log_to("errors.log", entry)
    _lib.allow()


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        _lib.log_to(
            "hook-errors.log",
            {"ts": _lib.iso_now(), "hook": "tool-failure-log", "error": str(exc)},
        )
        sys.exit(0)
