#!/usr/bin/env python3
"""
ai-skills plugin hook: session-start-context
Event: SessionStart
Exit code 0 = always allow.

On every session start:
1. Detect target repo (cwd).
2. Read up to 8KB of CLAUDE.md / AGENTS.md / ARCHITECTURE.md / marketing/MARKETING.md.
3. Apply PII filter to each slice.
4. Wrap each slice in <untrusted_content> envelope (G1).
5. Inject combined context into Claude's session.
6. Initialize session token meter at .ai-skills-memory/sessions/<run-id>/token-meter.json.
7. Detect locale from prior turns' unicode block (Cyrillic/CJK/Arabic) — write to locale.txt.
8. No-op gracefully if no project files are present.

Per 03-MEMORY-ARCHITECTURE.md L2 read + R8 CRIT-1 untrusted-content-wrapping rule.
Fail-open per failure-recovery rule.
"""

from __future__ import annotations

import os
import pathlib
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _lib  # noqa: E402


L2_FILES = ["CLAUDE.md", "AGENTS.md", "ARCHITECTURE.md", "marketing/MARKETING.md"]
MAX_BYTES = 8 * 1024  # 8 KB per file


def slice_file(path: pathlib.Path) -> tuple[str, bool]:
    """Read up to MAX_BYTES. Returns (content, was_truncated)."""
    try:
        raw = path.read_bytes()
    except OSError:
        return "", False
    if len(raw) <= MAX_BYTES:
        return raw.decode("utf-8", errors="replace"), False
    head = raw[: MAX_BYTES // 2]
    tail = raw[-(MAX_BYTES // 4):]
    truncation_marker = (
        f"\n\n[TRUNCATED: {len(raw) - len(head) - len(tail)} bytes omitted]\n\n"
    )
    return (
        head.decode("utf-8", errors="replace")
        + truncation_marker
        + tail.decode("utf-8", errors="replace"),
        True,
    )


def session_id_from_input(data: dict) -> str:
    """Use Claude Code-provided session ID; fall back to timestamp."""
    sid = data.get("session_id") or data.get("sessionId") or _lib.iso_now()
    return str(sid).replace(":", "-").replace(".", "-")


def main() -> None:
    data = _lib.read_stdin_json()
    cwd = pathlib.Path.cwd()
    sid = session_id_from_input(data)
    session_dir = cwd / ".ai-skills-memory" / "sessions" / sid

    # Initialize session token meter. `cwd_at_start` lets post-context-compact
    # teammates compare current `pwd` against the session anchor and detect the
    # cwd-drift sub-flake (audit §2.8) before issuing relative paths.
    try:
        _lib.update_token_meter(
            session_dir,
            {
                "session_started_at": _lib.iso_now(),
                "session_id": sid,
                "cwd_at_start": str(cwd),
            },
        )
    except Exception:
        pass  # Fail open

    # Read L2 files, PII-filter, wrap, build context payload
    wrapped_blocks: list[str] = []
    truncations: list[str] = []
    redactions_total = 0

    for relpath in L2_FILES:
        path = cwd / relpath
        if not path.exists():
            continue
        content, truncated = slice_file(path)
        if not content:
            continue
        if truncated:
            truncations.append(relpath)
        redacted, n = _lib.apply_pii_filter(content)
        redactions_total += n
        wrapped = _lib.wrap_untrusted(redacted, source=f"L2:{relpath}")
        wrapped_blocks.append(wrapped)

    if wrapped_blocks:
        # Per Claude Code SessionStart hook protocol: print to stdout to inject
        # additional context into the session. Combine all wrapped blocks.
        print("# Project context (auto-loaded from L2 files)")
        print("")
        for block in wrapped_blocks:
            print(block)
            print("")

    # Log truncations + redactions to L3
    if truncations:
        _lib.log_to(
            f"sessions/{sid}/truncation.log",
            {"ts": _lib.iso_now(), "truncated_files": truncations},
        )
    if redactions_total > 0:
        _lib.log_to(
            "redactions.log",
            {
                "ts": _lib.iso_now(),
                "source": "session-start-context",
                "session_id": sid,
                "redactions_count": redactions_total,
            },
        )

    _lib.allow()


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        # Fail open per failure-recovery rule
        _lib.log_to(
            "hook-errors.log",
            {
                "ts": _lib.iso_now(),
                "hook": "session-start-context",
                "error": str(exc),
            },
        )
        sys.exit(0)
