#!/usr/bin/env python3
"""
ai-assets plugin hook: subagent-start-budget
Event: SubagentStart
Exit code 0 = allow spawn; exit code 2 = block spawn (budget exceeded).

Per R8 spawn-payload schema (G7) and ralph-budget rule:
1. Validate G7 spawn payload schema (best-effort; warn if malformed but don't block).
2. Read session token meter; check against userConfig session_token_soft_cap +
   session_token_hard_cap.
3. If estimated input + meter exceeds hard cap → block spawn with diagnostic.
4. If exceeds soft cap → log warning to errors.log, allow.

Per failure-recovery rule: fail-open on internal hook errors (don't block all
spawns due to buggy hook).
"""

from __future__ import annotations

import os
import pathlib
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _lib  # noqa: E402


# Defaults if userConfig unavailable from hook input
DEFAULT_SOFT_CAP = 1_000_000
DEFAULT_HARD_CAP = 1_500_000


def main() -> None:
    data = _lib.read_stdin_json()
    sid = str(data.get("session_id") or "unknown").replace(":", "-").replace(".", "-")

    # Spawn payload may be in data["payload"] or data["spawn_payload"]
    payload = data.get("spawn_payload") or data.get("payload") or {}
    estimated_input = 0
    if isinstance(payload, dict):
        budget = payload.get("budget") or {}
        estimated_input = int(budget.get("max_input_tokens", 0) or 0)

    # User config caps (fall back to defaults if unset)
    user_config = data.get("user_config") or data.get("userConfig") or {}
    soft_cap = int(user_config.get("session_token_soft_cap", DEFAULT_SOFT_CAP))
    hard_cap = int(user_config.get("session_token_hard_cap", DEFAULT_HARD_CAP))

    # Read meter
    cwd = pathlib.Path.cwd()
    session_dir = cwd / ".ai-assets-memory" / "sessions" / sid
    meter = _lib.read_token_meter(session_dir)
    current_in = int(meter.get("tokens_in_total", 0))
    projected = current_in + estimated_input

    # G7 schema sanity check (best-effort)
    if isinstance(payload, dict):
        required = ["trace_id", "subagent_role", "goal", "constraints", "allowed_tools", "budget"]
        missing = [k for k in required if k not in payload]
        if missing:
            _lib.log_to(
                "errors.log",
                {
                    "ts": _lib.iso_now(),
                    "severity": "WARNING",
                    "hook": "subagent-start-budget",
                    "issue": "spawn_payload_schema_violation",
                    "missing_fields": missing,
                    "session_id": sid,
                },
            )
            # Don't block — just warn. Orchestrator may correct.

    # Budget check
    if projected > hard_cap:
        msg = (
            f"BLOCKED: subagent spawn would exceed session token hard cap.\n"
            f"  Current session input tokens: {current_in:,}\n"
            f"  Spawn estimated input tokens: {estimated_input:,}\n"
            f"  Projected total:              {projected:,}\n"
            f"  Hard cap:                     {hard_cap:,}\n"
            f"\n"
            f"To proceed, raise userConfig.session_token_hard_cap or wait for "
            f"context compaction to reduce session usage."
        )
        _lib.log_to(
            "errors.log",
            {
                "ts": _lib.iso_now(),
                "severity": "ERROR",
                "hook": "subagent-start-budget",
                "issue": "session_token_hard_cap_exceeded",
                "current_in": current_in,
                "estimated_input": estimated_input,
                "hard_cap": hard_cap,
                "session_id": sid,
            },
        )
        _lib.block(msg)

    if projected > soft_cap:
        _lib.log_to(
            "errors.log",
            {
                "ts": _lib.iso_now(),
                "severity": "WARNING",
                "hook": "subagent-start-budget",
                "issue": "session_token_soft_cap_warning",
                "projected": projected,
                "soft_cap": soft_cap,
                "session_id": sid,
            },
        )

    _lib.allow()


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        _lib.log_to(
            "hook-errors.log",
            {"ts": _lib.iso_now(), "hook": "subagent-start-budget", "error": str(exc)},
        )
        sys.exit(0)
