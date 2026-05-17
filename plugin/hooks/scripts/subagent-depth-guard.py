#!/usr/bin/env python3
"""
ai-skills plugin hook: subagent-depth-guard
Event: SubagentStart
Exit code 0 = allow spawn; exit code 2 = block spawn (depth cap exceeded).

Phase 4 #4 (v0.1.7): defensive bounded-recursion guard.

Per subagent-isolation.md (v0.1):
> Recursion depth is therefore at most 2: main thread -> feature-design-lead
> -> spawned domain agents. No infinite loop risk.
> If future versions add Task to additional orchestrator agents, add a
> subagent-depth-guard.py hook that tracks depth via the trace_id chain in
> the G7 spawn payload and rejects spawn beyond depth 3.

This is that hook. It runs on SubagentStart (after subagent-start-budget) and:

  1. Reads spawn payload, extracts trace_id and parent_trace_id (None = top-level).
  2. Reads spawn-chain.jsonl from session dir (built from prior start events
     during this session).
  3. Computes depth by walking the parent chain:
       - depth = 1 if parent_trace_id is None or unknown
       - depth = parent_depth + 1 otherwise
  4. Reads MAX_DEPTH from env CLAUDE_USER_CONFIG_subagent_max_depth (default 3
     per subagent-isolation.md).
  5. If depth > MAX_DEPTH, blocks the spawn with a clear diagnostic + records
     the violation to errors.log.
  6. Otherwise appends a `start` event to spawn-chain.jsonl and exits 0.

The spawn-chain.jsonl format (one JSON line per event):
    {"event":"start","trace_id":"...","parent_trace_id":"...","depth":N,"ts":"..."}
    {"event":"stop","trace_id":"...","ts":"..."}  # appended by subagent-stop-learnings.py

Fail-open per failure-recovery rule: never block all spawns due to a buggy
depth-guard. Anthropic's runtime already enforces N=1 (subagents cannot
spawn subagents) — this hook is a defensive backstop in case that contract
ever changes or our orchestration accidentally violates it.
"""

from __future__ import annotations

import json
import os
import pathlib
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _lib  # noqa: E402


DEFAULT_MAX_DEPTH = 3
SPAWN_CHAIN_FILENAME = "spawn-chain.jsonl"


def _read_int_env(var: str, default: int) -> int:
    raw = os.environ.get(var)
    if raw is None or raw == "":
        return default
    try:
        return int(raw)
    except (ValueError, TypeError):
        return default


def _read_chain(chain_path: pathlib.Path) -> list[dict]:
    """Read spawn-chain.jsonl into a list of parsed events. Fail-open."""
    if not chain_path.exists():
        return []
    events: list[dict] = []
    try:
        with chain_path.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    # Skip malformed line, don't fail the whole read
                    continue
    except OSError:
        return []
    return events


def _compute_depth(
    trace_id: str | None,
    parent_trace_id: str | None,
    chain_events: list[dict],
) -> int:
    """Walk the parent chain from this spawn's parent. Returns depth.

    depth=1 if parent_trace_id is None or not found in the chain (top-level
    spawn from main thread). Otherwise depth = parent_depth + 1.

    The chain is keyed by trace_id so we can look up any prior spawn's
    recorded depth. Cycles (shouldn't happen but defensive) are bounded by
    a hard limit of MAX_DEPTH * 4 to prevent infinite loops.
    """
    if not parent_trace_id:
        return 1

    # Build {trace_id: (parent_trace_id, depth)} from the most recent start
    # event for each trace_id (later events overwrite earlier — though
    # trace_ids should be unique per the schema).
    by_trace: dict[str, tuple[str | None, int]] = {}
    for ev in chain_events:
        if ev.get("event") == "start":
            tid = ev.get("trace_id")
            if isinstance(tid, str):
                by_trace[tid] = (
                    ev.get("parent_trace_id"),
                    int(ev.get("depth", 1)),
                )

    if parent_trace_id in by_trace:
        parent_depth = by_trace[parent_trace_id][1]
        return parent_depth + 1

    # Parent trace_id specified but not found in chain. Treat as depth 2:
    # parent must have spawned somewhere upstream (perhaps main thread without
    # the chain log being captured — fail-safe to assume one level above
    # top, not zero).
    return 2


def main() -> None:
    data = _lib.read_stdin_json()
    sid = str(data.get("session_id") or "unknown").replace(":", "-").replace(".", "-")

    payload = data.get("spawn_payload") or data.get("payload") or {}
    if not isinstance(payload, dict):
        # Malformed payload — fail-open, let subagent-start-budget handle it
        _lib.allow()

    trace_id = payload.get("trace_id")
    parent_trace_id = payload.get("parent_trace_id")
    if not isinstance(trace_id, str):
        # No trace_id at all — can't track. Let other hooks complain about schema.
        _lib.allow()

    cwd = pathlib.Path.cwd()
    session_dir = cwd / ".ai-skills-memory" / "sessions" / sid
    chain_path = session_dir / SPAWN_CHAIN_FILENAME

    chain_events = _read_chain(chain_path)
    depth = _compute_depth(trace_id, parent_trace_id, chain_events)

    max_depth = _read_int_env(
        "CLAUDE_USER_CONFIG_subagent_max_depth",
        DEFAULT_MAX_DEPTH,
    )

    if depth > max_depth:
        msg = (
            f"BLOCKED: subagent spawn would exceed max recursion depth.\n"
            f"  Spawn trace_id:        {trace_id}\n"
            f"  Parent trace_id:       {parent_trace_id}\n"
            f"  Computed depth:        {depth}\n"
            f"  Max allowed depth:     {max_depth}\n"
            f"\n"
            f"Per subagent-isolation.md, only feature-design-lead has Task in\n"
            f"v0.1 plugin (depth 1 -> 2 spawn allowed). Anthropic's runtime\n"
            f"normally enforces depth=1 max. To proceed if intentional:\n"
            f"raise userConfig.subagent_max_depth (default 3)."
        )
        _lib.log_to(
            "errors.log",
            {
                "ts": _lib.iso_now(),
                "severity": "ERROR",
                "hook": "subagent-depth-guard",
                "issue": "subagent_max_depth_exceeded",
                "trace_id": trace_id,
                "parent_trace_id": parent_trace_id,
                "depth": depth,
                "max_depth": max_depth,
                "session_id": sid,
            },
        )
        # Record the rejected attempt in the chain for forensics, even though
        # we are blocking — useful for debugging "why did my orchestration get
        # rejected?".
        try:
            session_dir.mkdir(parents=True, exist_ok=True)
            with chain_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps({
                    "event": "rejected",
                    "trace_id": trace_id,
                    "parent_trace_id": parent_trace_id,
                    "depth": depth,
                    "max_depth": max_depth,
                    "ts": _lib.iso_now(),
                }, separators=(",", ":")) + "\n")
        except OSError:
            pass
        _lib.block(msg)

    # Record the start event in the chain so future spawns can compute depth.
    try:
        session_dir.mkdir(parents=True, exist_ok=True)
        with chain_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps({
                "event": "start",
                "trace_id": trace_id,
                "parent_trace_id": parent_trace_id,
                "depth": depth,
                "ts": _lib.iso_now(),
            }, separators=(",", ":")) + "\n")
    except OSError:
        pass  # Fail open — the next hook in the chain still allows the spawn

    _lib.allow()


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        # _lib.allow() / block() raise SystemExit — pass through
        raise
    except Exception as exc:
        # Per failure-recovery + A3: never block subagent spawn because of a
        # buggy depth-guard. Log and exit 0.
        _lib.log_to(
            "hook-errors.log",
            {"ts": _lib.iso_now(), "hook": "subagent-depth-guard", "error": str(exc)},
        )
        sys.exit(0)
