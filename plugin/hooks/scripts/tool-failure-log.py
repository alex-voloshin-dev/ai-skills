#!/usr/bin/env python3
"""
ai-assets plugin hook: tool-failure-log
Events: PostToolUseFailure, StopFailure
Exit code 0 = always allow.

Logs tool/turn failures to .ai-assets-memory/errors.log (separate from success
audit log). Captures duration_ms when present (Round 2 H3 + R5 Appendix A1
Anthropic April 2026 update).

v0.3.12 (audit §WP-4.1) enrichment: also captures the hook chain that COULD
have run for this event (parsed from hooks.json on the spot) and a 500-char
stderr tail. Both fields make post-mortem root-cause analysis of cascading
failures (one hook killing the rest of the chain) directly inspectable in
errors.log without re-running the workflow.
"""

from __future__ import annotations

import json
import os
import pathlib
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _lib  # noqa: E402


STDERR_TAIL_BYTES = 500


def _hook_chain_for(event: str, tool_name: str | None) -> list[str]:
    """Return the ordered list of hook script basenames registered for this
    event in plugin/hooks/hooks.json, filtered by matcher when the failure
    event carries a tool_name. Fail-open: returns [] on any IO / parse error.
    """
    plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT")
    if not plugin_root:
        # Best-effort: assume the script lives at <plugin>/hooks/scripts/
        plugin_root = str(pathlib.Path(__file__).resolve().parents[2])
    hooks_path = pathlib.Path(plugin_root) / "hooks" / "hooks.json"
    if not hooks_path.is_file():
        return []
    # Failure event names (PostToolUseFailure, StopFailure) are NOT registered
    # in hooks.json themselves — what failed is one of the upstream chains.
    parent_event = event[: -len("Failure")] if event and event.endswith("Failure") else event
    try:
        with hooks_path.open(encoding="utf-8") as f:
            cfg = json.load(f)
    except (OSError, json.JSONDecodeError):
        return []
    chain: list[str] = []
    for entry in cfg.get("hooks", {}).get(parent_event, []):
        matcher = entry.get("matcher")
        if matcher and tool_name:
            try:
                if not re.match(matcher, tool_name):
                    continue
            except re.error:
                continue
        for h in entry.get("hooks", []):
            cmd = h.get("command", "")
            for part in str(cmd).split():
                if part.endswith(".py"):
                    chain.append(pathlib.Path(part).name)
                    break
    return chain


def _stderr_tail(data: dict) -> str | None:
    """Pull the last STDERR_TAIL_BYTES chars of stderr from the failure event.
    Looks in `stderr`, `tool_response.stderr`, then `tool_response.output`."""
    candidates = [data.get("stderr")]
    tr = data.get("tool_response")
    if isinstance(tr, dict):
        candidates.append(tr.get("stderr"))
        candidates.append(tr.get("output"))
    for c in candidates:
        if c:
            s = str(c)
            if len(s) <= STDERR_TAIL_BYTES:
                return s
            return s[-STDERR_TAIL_BYTES:]
    return None


def main() -> None:
    data = _lib.read_stdin_json()
    data = _lib.normalize_hook_input(data)

    event = data.get("hook_event_name", "Unknown")
    tool_name = data.get("tool_name")

    error_field = data.get("error")
    if error_field is None and isinstance(data.get("tool_response"), dict):
        error_field = data["tool_response"].get("error")

    entry = {
        "ts": _lib.iso_now(),
        "severity": "ERROR",
        "event": event,
        "session_id": data.get("session_id"),
        "tool_name": tool_name,
        "duration_ms": data.get("duration_ms"),
        "error": error_field,
        "failed_hook": data.get("failed_hook") or data.get("hook_name"),
        "hook_chain": _hook_chain_for(event, tool_name) or None,
        "stderr_tail": _stderr_tail(data),
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
