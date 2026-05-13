#!/usr/bin/env python3
"""
ai-assets plugin hook: session-end-finalize
Event: SessionEnd
Exit code 0 = always allow.

Per memory-discipline retention rules:
1. Read sessions/<id>/runs.jsonl (L3); compute summary.
2. Aggregate token usage from G7 return envelopes in
   sessions/<id>/{team-envelopes,subagent-reports}/ (audit §3.1) — the meter
   itself is rarely updated by upstream hooks, so the old summary always
   reported zeros.
3. Cross-check event count against repo-wide agent-actions.log filtered by
   session_id.
4. Append session summary line to L4 runs.jsonl (cross-session aggregate).
5. Release any dangling RALF locks (.ai-assets-memory/ralph/<run-id>/active.lock).
6. Optionally delete L3 sessions/<id>/ after summary write (per retention rule
   "session lifetime; archived to L4 then sessions/<id> deleted"). v0.1: keep
   sessions/<id>/ for 7 days; deletion handled separately to avoid data loss.
"""

from __future__ import annotations

import json
import os
import pathlib
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _lib  # noqa: E402


def _aggregate_g7_envelopes(session_dir: pathlib.Path) -> dict:
    """Walk team-envelopes/ and subagent-reports/ under the session dir, parse
    JSON files matching the G7 return-contract shape, and sum `tokens_used`.

    Returns aggregate keys: g7_envelope_count, g7_tokens_input_total,
    g7_tokens_output_total. Returns zeros on any IO / parse failure (fail-open).
    """
    totals = {
        "g7_envelope_count": 0,
        "g7_tokens_input_total": 0,
        "g7_tokens_output_total": 0,
    }
    candidates: list[pathlib.Path] = []
    for sub in ("team-envelopes", "subagent-reports"):
        d = session_dir / sub
        if not d.is_dir():
            continue
        try:
            candidates.extend(p for p in d.iterdir() if p.suffix == ".json")
        except OSError:
            continue
    for path in candidates:
        try:
            obj = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(obj, dict):
            continue
        # Only G7 return envelopes have all of trace_id + status + tokens_used.
        # TaskCompleted reconciliation envelopes have event/disk_state and are
        # skipped to avoid double-counting events as token spend.
        tokens = obj.get("tokens_used")
        if not (isinstance(tokens, dict) and "trace_id" in obj and "status" in obj):
            continue
        totals["g7_envelope_count"] += 1
        try:
            totals["g7_tokens_input_total"] += int(tokens.get("input", 0) or 0)
            totals["g7_tokens_output_total"] += int(tokens.get("output", 0) or 0)
        except (TypeError, ValueError):
            continue
    return totals


def _agent_actions_count_for_session(memory_root: pathlib.Path, sid: str) -> int:
    """Count rows in agent-actions.log whose `session=<sid>` segment matches.

    Returns 0 on any failure (fail-open). Capped at MAX_SCAN_BYTES so a
    multi-megabyte log does not stall session shutdown.
    """
    log_path = memory_root / "agent-actions.log"
    if not log_path.is_file():
        return 0
    MAX_SCAN_BYTES = 16 * 1024 * 1024  # 16 MB
    needle = f"session={sid}"
    count = 0
    try:
        with log_path.open("rb") as f:
            try:
                size = log_path.stat().st_size
                if size > MAX_SCAN_BYTES:
                    f.seek(size - MAX_SCAN_BYTES)
                    f.readline()  # drop partial line
            except OSError:
                pass
            for raw in f:
                if needle.encode() in raw:
                    count += 1
    except OSError:
        return 0
    return count


def main() -> None:
    data = _lib.read_stdin_json()
    sid = str(data.get("session_id") or "unknown").replace(":", "-").replace(".", "-")

    cwd = pathlib.Path.cwd()
    memory_root = cwd / ".ai-assets-memory"
    session_dir = memory_root / "sessions" / sid

    if not session_dir.exists():
        _lib.allow()

    # Read meter for summary
    meter = _lib.read_token_meter(session_dir)

    # Count events in L3 runs.jsonl
    runs_path = session_dir / "runs.jsonl"
    event_count = 0
    if runs_path.exists():
        try:
            with runs_path.open(encoding="utf-8") as f:
                event_count = sum(1 for _ in f)
        except OSError:
            pass

    g7_totals = _aggregate_g7_envelopes(session_dir)
    agent_actions_count = _agent_actions_count_for_session(memory_root, sid)

    # Append session summary to L4 runs.jsonl. The aggregated fields close the
    # audit §3.1 zeroes — when the meter never receives updates the G7 envelope
    # totals carry the actual token spend.
    summary = {
        "ts": _lib.iso_now(),
        "event": "SessionEnd",
        "session_id": sid,
        "tokens_in_total": meter.get("tokens_in_total", 0),
        "tokens_out_total": meter.get("tokens_out_total", 0),
        "ralf_iter_total": meter.get("ralf_iter_total", 0),
        "ralf_tokens_total": meter.get("ralf_tokens_total", 0),
        "session_event_count": event_count,
        "session_started_at": meter.get("session_started_at"),
        "cwd_at_start": meter.get("cwd_at_start"),
        "g7_envelope_count": g7_totals["g7_envelope_count"],
        "g7_tokens_input_total": g7_totals["g7_tokens_input_total"],
        "g7_tokens_output_total": g7_totals["g7_tokens_output_total"],
        "agent_actions_count": agent_actions_count,
        "g7_violation_count": meter.get("g7_violation_count", 0),
    }
    _lib.log_to("runs.jsonl", summary)

    # Release dangling RALF locks
    ralph_root = memory_root / "ralph"
    if ralph_root.exists():
        try:
            for run_dir in ralph_root.iterdir():
                if not run_dir.is_dir():
                    continue
                lock_path = run_dir / "active.lock"
                if lock_path.exists():
                    # Mark as orphan (session ended without RALF terminal state)
                    orphan_marker = run_dir / "orphan-by-session-end.txt"
                    try:
                        orphan_marker.write_text(
                            f"Session {sid} ended {_lib.iso_now()} with active RALF lock. Lock released by session-end-finalize hook.",
                            encoding="utf-8",
                        )
                        lock_path.unlink()
                    except OSError:
                        pass
        except OSError:
            pass

    _lib.allow()


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        _lib.log_to(
            "hook-errors.log",
            {"ts": _lib.iso_now(), "hook": "session-end-finalize", "error": str(exc)},
        )
        sys.exit(0)
