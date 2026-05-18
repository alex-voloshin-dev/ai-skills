#!/usr/bin/env python3
"""
ai-skills plugin hook: subagent-stop-learnings
Event: SubagentStop
Exit code 0 = always allow.

Two responsibilities:
1. Validate G7 return contract (per plugin/schemas/return-contract.schema.json).
   Per R6 HIGH-4: on validation failure, log to errors.log, fail-open, surface
   diagnostic to orchestrator via stderr. NEVER block parent workflow.
   A SubagentStop with NO return-contract key at all is the normal case for
   non-G7 / ad-hoc subagent tasks and is NOT a validation failure — only an
   actually-supplied (present) return payload is validated. This distinguishes
   "no contract" (silent) from "malformed contract" (logged ERROR + stderr).
2. If userConfig.subagent_learnings_enabled = true, capture non-trivial
   subagent outputs to .ai-skills-memory/sessions/<id>/subagent-reports/<name>-<id>.md
   for memory-curator to review later.
"""

from __future__ import annotations

import json
import os
import pathlib
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _lib  # noqa: E402


REQUIRED_RETURN_FIELDS = ["trace_id", "status", "tokens_used", "result"]
VALID_STATUS_VALUES = {"ok", "needs_clarification", "failed", "partial"}


def validate_return_contract(payload: dict) -> list[str]:
    """Return list of validation issues (empty = valid)."""
    issues: list[str] = []
    for field in REQUIRED_RETURN_FIELDS:
        if field not in payload:
            issues.append(f"missing_field:{field}")

    status = payload.get("status")
    if status and status not in VALID_STATUS_VALUES:
        issues.append(f"invalid_status:{status}")

    if status == "needs_clarification":
        if not payload.get("needs_clarification"):
            issues.append("needs_clarification_status_without_question")

    tu = payload.get("tokens_used")
    if tu is not None and not isinstance(tu, dict):
        issues.append("tokens_used_not_object")

    return issues


def main() -> None:
    data = _lib.read_stdin_json()
    sid = str(data.get("session_id") or "unknown").replace(":", "-").replace(".", "-")

    # Distinguish "no return-contract key supplied at all" (normal case for
    # non-G7 / ad-hoc subagent stops — must NOT be flagged) from "a contract
    # was supplied but is malformed" (a real validation failure worth ERROR +
    # stderr). FINDING-1: the old `... or {}` default made an absent contract
    # indistinguishable from an empty one, so validate_return_contract({}) ran
    # on every plain SubagentStop and spammed errors.log.
    contract_present = (
        "return_contract" in data or "returnContract" in data
    )
    return_payload = data.get("return_contract") or data.get("returnContract") or {}
    user_config = data.get("user_config") or data.get("userConfig") or {}
    learnings_enabled = bool(user_config.get("subagent_learnings_enabled", False))

    # Validate (R6 HIGH-4) — only when a return contract was actually supplied.
    # An empty / absent payload means "this subagent did not return a G7
    # contract", which is allowed; we fail-open silently.
    if contract_present and isinstance(return_payload, dict) and return_payload:
        issues = validate_return_contract(return_payload)
        if issues:
            diagnostic = {
                "ts": _lib.iso_now(),
                "severity": "ERROR",
                "hook": "subagent-stop-learnings",
                "issue": "return_contract_validation_failed",
                "trace_id": return_payload.get("trace_id"),
                "issues": issues,
                "session_id": sid,
            }
            _lib.log_to("errors.log", diagnostic)
            # Surface to stderr per R6 HIGH-4
            print(
                f"[subagent-stop-learnings] G7 return contract validation failed: "
                f"{', '.join(issues)} (trace_id={return_payload.get('trace_id')})",
                file=sys.stderr,
            )
            # Fail-open per failure-recovery rule

    # Phase 4 #4 (v0.1.7): record stop event in spawn-chain.jsonl so the
    # depth-guard hook (subagent-depth-guard.py) sees a complete chain
    # including closure timestamps. The chain log persists across the session.
    if isinstance(return_payload, dict) and return_payload.get("trace_id"):
        try:
            session_dir = pathlib.Path.cwd() / ".ai-skills-memory" / "sessions" / sid
            session_dir.mkdir(parents=True, exist_ok=True)
            chain_path = session_dir / "spawn-chain.jsonl"
            with chain_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps({
                    "event": "stop",
                    "trace_id": return_payload.get("trace_id"),
                    "status": return_payload.get("status"),
                    "ts": _lib.iso_now(),
                }, separators=(",", ":")) + "\n")
        except OSError:
            pass  # Fail open

    # Update session token meter from tokens_used
    if isinstance(return_payload, dict):
        tu = return_payload.get("tokens_used") or {}
        if isinstance(tu, dict):
            cwd = pathlib.Path.cwd()
            session_dir = cwd / ".ai-skills-memory" / "sessions" / sid
            try:
                _lib.update_token_meter(
                    session_dir,
                    {
                        "tokens_in_total": int(tu.get("input", 0) or 0),
                        "tokens_out_total": int(tu.get("output", 0) or 0),
                    },
                )
            except Exception:
                pass

    # Optional: capture for memory-curator review
    if learnings_enabled and isinstance(return_payload, dict):
        result = return_payload.get("result") or {}
        summary = result.get("summary", "") if isinstance(result, dict) else ""
        if summary and len(summary) > 50:  # non-trivial threshold
            agent_name = data.get("subagent_role") or data.get("agent_name") or "unknown"
            spawn_id = return_payload.get("trace_id", "noid").replace("/", "_")
            report_path = (
                f"sessions/{sid}/subagent-reports/{agent_name}-{spawn_id}.md"
            )
            content = (
                f"# Subagent report: {agent_name}\n\n"
                f"**Trace ID:** {return_payload.get('trace_id')}\n"
                f"**Status:** {return_payload.get('status')}\n"
                f"**Captured:** {_lib.iso_now()}\n\n"
                f"## Summary\n\n{summary}\n\n"
                f"## Full result\n\n```json\n{json.dumps(result, indent=2)[:2000]}\n```\n"
            )
            redacted, _ = _lib.apply_pii_filter(content)
            try:
                full_path = pathlib.Path.cwd() / ".ai-skills-memory" / report_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text(redacted, encoding="utf-8")
            except OSError:
                pass

    _lib.allow()


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        _lib.log_to(
            "hook-errors.log",
            {"ts": _lib.iso_now(), "hook": "subagent-stop-learnings", "error": str(exc)},
        )
        sys.exit(0)
