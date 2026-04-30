#!/usr/bin/env python3
"""
ai-assets plugin hook: tool-output-normalize (G2)
Event: PostToolUse (matcher: same as wrap, fires AFTER)
Exit code 0 = always allow.

Per R3 G2: for tool outputs >2000 tokens, extract top-k items + summarize via
Haiku (deferred — see note) + annotate metadata. Tracks `injected_tokens` against
session token meter.

Self-enforcing order (R5 S6): asserts wrap marker from tool-output-wrap is
present; logs warning + proceeds if marker absent (don't block — fail open).

v0.1 implementation: structural normalization only (extract envelope from
preceding wrap, attach metadata). Haiku-summarize step deferred until eval-judge
agent infrastructure is wired in B12 — currently we annotate but don't reduce.
This is a known incomplete: full extract→summarize→annotate pipeline ships in
Phase 4 hardening alongside G1/G2 attack-surface validation.
"""

from __future__ import annotations

import json
import os
import pathlib
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _lib  # noqa: E402


CHAR_THRESHOLD_BIG = 2000 * 4  # ~2000 tokens


def main() -> None:
    data = _lib.read_stdin_json()
    data = _lib.normalize_hook_input(data)

    # Check wrap marker (R5 S6 ordering enforcement)
    wrap_present = _lib.read_wrap_marker()
    if not wrap_present:
        # Log warning but don't block (fail open per failure-recovery rule)
        _lib.log_to(
            "errors.log",
            {
                "ts": _lib.iso_now(),
                "severity": "WARNING",
                "hook": "tool-output-normalize",
                "issue": "wrap_marker_missing_before_normalize",
                "advice": (
                    "tool-output-wrap.py must run before tool-output-normalize.py. "
                    "Check hooks.json array order."
                ),
            },
        )

    tool_response = data.get("tool_response")
    output_text = ""
    if isinstance(tool_response, str):
        output_text = tool_response
    elif isinstance(tool_response, dict):
        for k in ("output", "stdout", "content", "text", "result"):
            v = tool_response.get(k)
            if isinstance(v, str):
                output_text = v
                break

    # Estimate tokens (approx chars/4)
    estimated_tokens = len(output_text) // 4

    # Update session token meter with injected tokens
    sid = str(data.get("session_id") or "unknown").replace(":", "-").replace(".", "-")
    cwd = pathlib.Path.cwd()
    session_dir = cwd / ".ai-assets-memory" / "sessions" / sid
    try:
        _lib.update_token_meter(
            session_dir,
            {"injected_tokens_from_tools": estimated_tokens},
        )
    except Exception:
        pass

    # If under big threshold, no further action (wrap is sufficient)
    if len(output_text) <= CHAR_THRESHOLD_BIG:
        _lib.allow()

    # Big output: emit normalized envelope metadata
    # v0.1 stops at metadata; full Haiku-summarize ships in Phase 4
    envelope = {
        "tool": data.get("tool_name"),
        "call_id": data.get("call_id") or data.get("tool_call_id"),
        "ts": _lib.iso_now(),
        "original_size_tokens_estimated": estimated_tokens,
        "injected_tokens": estimated_tokens,  # Until Haiku-summarize lands
        "truncated": False,  # Will be True after Haiku-summarize
        "summary_model_used": None,  # "haiku" after Phase 4
        "wrap_applied": wrap_present,
        "v0_1_note": "structural normalization only; Haiku-summarize deferred to Phase 4 hardening",
    }

    print("\n<!-- normalize-envelope -->")
    print(json.dumps(envelope, indent=2))
    print("<!-- /normalize-envelope -->")

    _lib.allow()


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        _lib.log_to(
            "hook-errors.log",
            {"ts": _lib.iso_now(), "hook": "tool-output-normalize", "error": str(exc)},
        )
        sys.exit(0)
