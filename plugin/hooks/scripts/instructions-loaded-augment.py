#!/usr/bin/env python3
"""
ai-assets plugin hook: instructions-loaded-augment
Event: InstructionsLoaded
Exit code 0 = always allow.

When CLAUDE.md or any rule file loads into context, supplement with relevant
excerpt from .ai-assets-memory/.committed/conventions.md (if present). Wraps
the supplement in <untrusted_content> envelope (G1) before injection.

No-ops if .committed/conventions.md missing.
"""

from __future__ import annotations

import os
import pathlib
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _lib  # noqa: E402


def main() -> None:
    _ = _lib.read_stdin_json()
    cwd = pathlib.Path.cwd()
    conv_path = cwd / ".ai-assets-memory" / ".committed" / "conventions.md"
    if not conv_path.exists():
        _lib.allow()

    try:
        content = conv_path.read_text(encoding="utf-8")
    except OSError:
        _lib.allow()

    if not content.strip():
        _lib.allow()

    redacted, n_redactions = _lib.apply_pii_filter(content)
    wrapped = _lib.wrap_untrusted(redacted, source="L4:.committed/conventions.md")
    print("# Team-confirmed conventions (from .committed/conventions.md)")
    print("")
    print(wrapped)

    if n_redactions:
        _lib.log_to(
            "redactions.log",
            {
                "ts": _lib.iso_now(),
                "source": "instructions-loaded-augment",
                "redactions_count": n_redactions,
            },
        )

    _lib.allow()


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        _lib.log_to(
            "hook-errors.log",
            {"ts": _lib.iso_now(), "hook": "instructions-loaded-augment", "error": str(exc)},
        )
        sys.exit(0)
