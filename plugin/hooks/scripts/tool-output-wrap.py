#!/usr/bin/env python3
"""
ai-skills plugin hook: tool-output-wrap (G1)
Event: PostToolUse (matcher: Read|Bash for memory dirs and project files)
Exit code 0 = always allow.

Per untrusted-content-wrapping rule + R3 G1: wraps tool outputs >200 tokens
in <untrusted_content> envelope BEFORE injection back into LLM context.

Defends against indirect prompt injection from CLAUDE.md, env-analyze logs,
learnings.md content, etc.

Emits wrap marker (R5 S6) for tool-output-normalize.py to verify ordering.

Note: Claude Code's hook execution model determines how stdout from this hook
modifies the tool response visible to the model. v0.1 implementation: print
the wrapped content to stdout + emit marker to stderr. Real-world behavior
verification deferred to Phase 4 hardening.
"""

from __future__ import annotations

import os
import pathlib
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _lib  # noqa: E402


# Approximate token count: chars / 4 (Anthropic rough heuristic)
TOKEN_THRESHOLD = 200
CHAR_THRESHOLD = TOKEN_THRESHOLD * 4


def main() -> None:
    data = _lib.read_stdin_json()
    data = _lib.normalize_hook_input(data)

    tool_name = data.get("tool_name", "")
    tool_response = data.get("tool_response")
    tool_input = data.get("tool_input", {}) or {}

    # Extract output text
    output_text = ""
    if isinstance(tool_response, str):
        output_text = tool_response
    elif isinstance(tool_response, dict):
        # Common response shapes
        for k in ("output", "stdout", "content", "text", "result"):
            v = tool_response.get(k)
            if isinstance(v, str):
                output_text = v
                break

    if not output_text:
        # Still emit marker so tool-output-normalize.py does not flag a false
        # "wrap_marker_missing" handshake error. The wrap pass ran; it just had
        # nothing to wrap. Per v0.3.12 hardening (closes audits/2026-05-13 §2.1).
        _lib.emit_wrap_marker()
        _lib.allow()

    # Skip if under threshold (per untrusted-content-wrapping rule "≤200 tokens skip wrap")
    if len(output_text) <= CHAR_THRESHOLD:
        # Emit marker on the skip-path too. The downstream normalize hook needs
        # to know "wrap ran and decided not to wrap" vs. "wrap never ran". Per
        # v0.3.12 hardening (closes audits/2026-05-13 §2.1 — 724 false WARNINGs
        # per 2 days from skip-path missing marker handshake).
        _lib.emit_wrap_marker()
        _lib.allow()

    # Determine source label
    if tool_name == "Bash":
        cmd = tool_input.get("command", "")[:80]
        source = f"tool:Bash:{cmd or 'unknown'}"
    elif tool_name == "Read":
        path = tool_input.get("file_path", "")
        # Memory dir reads → L4; project file reads → L2 if matches
        if ".ai-skills-memory" in path:
            source = f"L4:{path}"
        elif path.endswith(("CLAUDE.md", "AGENTS.md", "ARCHITECTURE.md")):
            source = f"L2:{path}"
        else:
            source = f"tool:Read:{path}"
    else:
        source = f"tool:{tool_name}"

    # PII-filter then wrap
    redacted, n_redactions = _lib.apply_pii_filter(output_text)
    wrapped = _lib.wrap_untrusted(redacted, source=source)

    print(wrapped)
    _lib.emit_wrap_marker()

    if n_redactions:
        _lib.log_to(
            "redactions.log",
            {
                "ts": _lib.iso_now(),
                "source": "tool-output-wrap",
                "tool_source": source,
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
            {"ts": _lib.iso_now(), "hook": "tool-output-wrap", "error": str(exc)},
        )
        sys.exit(0)
