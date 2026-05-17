#!/usr/bin/env python3
"""
ai-skills plugin hook: subagent-start-budget
Event: SubagentStart
Exit code 0 = allow spawn; exit code 2 = block spawn (budget exceeded or G7
schema repeatedly violated).

Per R8 spawn-payload schema (G7) and ralph-budget rule:
1. Validate G7 spawn payload schema. First 2 violations per session = WARNING.
   3rd+ violation = ERROR + block with a pasteable JSON example. Counter lives
   in the session token meter (`g7_violation_count`). Closes audit §2.3 — Lead
   was producing free-form spawn prompts indefinitely without escalation.
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

# How many spawn_payload_schema_violations to tolerate before blocking. Gives
# the Lead two grace warnings to correct course; the 3rd violation blocks.
G7_VIOLATION_GRACE = 2

G7_PAYLOAD_EXAMPLE = """{
  "trace_id": "wf-20260513-develop-wp01-spawn-001",
  "subagent_role": "java-engineer",
  "goal": "Implement WP-1.1 per design.md §4.2 — preserve visibility_score on retry.",
  "constraints": [
    "envelope_dir: /absolute/path/.ai-skills-memory/sessions/<sid>/team-envelopes",
    "<VERBATIM source-section block from design.md>"
  ],
  "state_slice": {
    "active_files": ["src/main/java/com/example/ReportService.java"],
    "related_artefacts": ["docs/features/foo/design.md"]
  },
  "allowed_tools": ["Read", "Grep", "Glob", "Bash", "Write", "Edit"],
  "budget": {
    "max_input_tokens": 30000,
    "max_output_tokens": 2000,
    "max_tool_calls": 25,
    "max_turns": 5,
    "timeout_ms": 600000,
    "retry_budget": 1
  }
}"""


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
    session_dir = cwd / ".ai-skills-memory" / "sessions" / sid
    meter = _lib.read_token_meter(session_dir)
    current_in = int(meter.get("tokens_in_total", 0))
    projected = current_in + estimated_input

    # G7 schema sanity check. First G7_VIOLATION_GRACE violations per session
    # produce a WARNING; the next one blocks with a pasteable example payload.
    if isinstance(payload, dict):
        required = ["trace_id", "subagent_role", "goal", "constraints", "allowed_tools", "budget"]
        missing = [k for k in required if k not in payload]
        if missing:
            prior_count = int(meter.get("g7_violation_count", 0) or 0)
            new_count = prior_count + 1
            _lib.update_token_meter(session_dir, {"g7_violation_count": 1})
            if new_count > G7_VIOLATION_GRACE:
                _lib.log_to(
                    "errors.log",
                    {
                        "ts": _lib.iso_now(),
                        "severity": "ERROR",
                        "hook": "subagent-start-budget",
                        "issue": "spawn_payload_schema_violation_blocked",
                        "missing_fields": missing,
                        "violation_count": new_count,
                        "grace": G7_VIOLATION_GRACE,
                        "session_id": sid,
                    },
                )
                _lib.block(
                    "BLOCKED: spawn payload missing required G7 fields "
                    f"{missing} (violation #{new_count}; grace was "
                    f"{G7_VIOLATION_GRACE}).\n\n"
                    "Per `plugin/schemas/spawn-payload.schema.json`, every "
                    "Agent spawn MUST embed a JSON payload as the `prompt` "
                    "argument (not a free-form string). Minimal valid shape:\n\n"
                    f"{G7_PAYLOAD_EXAMPLE}\n\n"
                    "See `plugin/skills/team-protocols/spawn-pattern.md` for the "
                    "full schema and `plugin/skills/develop/SKILL.md` Lead "
                    "section for a worked Agent(...) example. To clear the "
                    "violation counter, the Lead must complete one valid "
                    "spawn (the counter resets on the next session)."
                )
            _lib.log_to(
                "errors.log",
                {
                    "ts": _lib.iso_now(),
                    "severity": "WARNING",
                    "hook": "subagent-start-budget",
                    "issue": "spawn_payload_schema_violation",
                    "missing_fields": missing,
                    "violation_count": new_count,
                    "grace_remaining": G7_VIOLATION_GRACE - new_count,
                    "session_id": sid,
                },
            )
            # Below grace ceiling — warn, allow, and let the Lead correct.

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
