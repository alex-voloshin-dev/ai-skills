#!/usr/bin/env python3
"""
ai-assets plugin hook: pre-compact-memory-flush
Event: PreCompact
Exit code 0 = always allow compaction.

CRITICAL hook for memory architecture. Per 03-MEMORY-ARCHITECTURE.md §11 +
R3 G1 + R4 O3 isolated-context guarantee:

Just BEFORE Claude Code compacts session context, write a flush marker that
memory-curator agent will pick up at next opportunity. v0.1 implementation:
write a "pending flush" marker to L4. Future v0.2+ migration: this hook
becomes `agent:memory-curator` type per R5 H4 (eliminates Python wrapper),
invoking memory-curator natively.

Per A3 explicit non-blocking contract: NEVER blocks compaction. Compaction
always proceeds. fail-open per failure-recovery rule.
"""

from __future__ import annotations

import json
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
    flush_marker_path = memory_root / "pending-flush" / f"{sid}.json"

    try:
        flush_marker_path.parent.mkdir(parents=True, exist_ok=True)
        marker = {
            "ts": _lib.iso_now(),
            "session_id": sid,
            "trigger": "PreCompact",
            "session_dir": f".ai-assets-memory/sessions/{sid}/",
            "instructions": (
                "memory-curator agent should read this marker on next spawn, "
                "review session state files, extract durable learnings to L4 "
                "learnings.md per learnings-schema.md, then delete this marker. "
                "Per R4 O3: memory-curator runs in isolated subagent context — "
                "reads from disk, not parent context."
            ),
        }
        flush_marker_path.write_text(
            json.dumps(marker, indent=2), encoding="utf-8"
        )
    except OSError:
        pass  # Fail open — compaction proceeds even if flush marker write fails

    _lib.log_to(
        "runs.jsonl",
        {
            "ts": _lib.iso_now(),
            "event": "PreCompact",
            "session_id": sid,
            "flush_marker_written": flush_marker_path.exists(),
        },
    )

    # Always allow compaction (R8 A3 non-blocking contract)
    _lib.allow()


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        _lib.log_to(
            "hook-errors.log",
            {"ts": _lib.iso_now(), "hook": "pre-compact-memory-flush", "error": str(exc)},
        )
        sys.exit(0)
