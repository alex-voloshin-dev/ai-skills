---
description: When to delegate to subagents vs work inline. Code-modifying stages are sequential per file; analysis stages may be parallel. Plugin agents are bounded-recursion (only feature-design-lead has Task tool); other agents cannot spawn further. Activates whenever multi-step or multi-stack work is being planned, before delegation decisions are made.
---

# Subagent Isolation and Delegation

When to spawn subagents vs do work in the main thread. When to run subagents in parallel vs sequentially. Bounded-recursion guarantee for v0.1.

## Routing Rules

| Use case | Mechanism | Why |
|---|---|---|
| Independent investigation, audit, parallel reviews of distinct artefacts | `Agent` × N in parallel | Multiple findings merged at end; outputs are documents, not code edits |
| Multi-stack code change | **Path B (Agent Teams) — MANDATORY default** via `TeamCreate`. Path A (sequential `Agent` calls) is fallback ONLY when Path B Step 1 returns a hard technical block | Per `team-protocols`: Path B is the user-facing UX default (panel, switchable transcripts, dependency graph). Sequential `Agent` calls are reserved for technical-block fallback — never selected for "simpler" / "sequential anyway" reasons |
| Code-modifying stages of any workflow (write/edit ops) | Sequential per file (whichever path), **one writer at a time per file** | File conflict prevention — mandatory in both Path A and Path B |
| Document-production stages (analysis, design, audit) | Parallel `Agent` × N permitted | Even within code-touching workflows, design phases parallelize safely |
| Single-file edit | Inline (no subagent) | Cost discipline |
| Anything > 3 deliverables / > 30 min | Mandatory subagent decomposition | Context budget discipline |

## Hot Rule

**Code-modifying stages are sequential per file; analysis and document-production stages may be parallel.** This replaces over-broad "always sequential for code-touching" wording.

## Bounded Recursion Guarantee (v0.1)

In plugin v0.1, only `feature-design-lead` agent has `tools: Task` (the spawn primitive). All other plugin-shipped agents — `security-engineer`, `eval-judge`, `memory-curator`, plus 22 normalized domain agents — explicitly DO NOT have Task in their tools list. They cannot spawn further subagents.

Recursion depth is therefore at most 2: main thread → feature-design-lead → spawned domain agents (engineers, designers, etc.). No infinite loop risk.

### Defensive depth guard (Phase 4 #4, v0.1.7)

`subagent-depth-guard.py` (SubagentStart hook) enforces a max-depth cap on every spawn, regardless of which agent has Task. Every G7 spawn payload may declare a `parent_trace_id` pointing at the spawn that initiated it (omit/null for top-level spawns from the main thread). The guard:

1. Reads `.ai-assets-memory/sessions/<sid>/spawn-chain.jsonl` (one line per `start`/`stop`/`rejected` event).
2. Computes depth by walking the parent chain from the current spawn.
3. Blocks the spawn (exit 2 + diagnostic) when `depth > userConfig.subagent_max_depth` (default 3).
4. Records both successful spawns and rejected attempts to the chain log for forensics.

Depth=1 is a top-level spawn from main; depth=2 is one nested level; depth=3 is the documented maximum (`main → feature-design-lead → domain agent → nested`). Anthropic's runtime normally enforces depth=1 max anyway — the guard is a defensive backstop in case orchestration accidentally bypasses that or a future version adds Task to additional agents. Fail-open per `failure-recovery.md`: a buggy guard never blocks all spawns.

## Runtime Detection of `TeamCreate`

The `develop`, `team-bugfix`, `bugfix`, and `feature-design` skills MUST attempt Path B (Agent Teams) at activation time per `team-protocols/SKILL.md` and `team-protocols/path-selection-rules.md`. Detection is implicit — the workflow attempts Path B Step 1 (natural-language team-create) directly; if that fails with "Agent Teams not enabled" or equivalent, it silently falls back to Path A (standalone `Agent` calls). **Path A selection for any non-technical reason** (sequential pipeline, single stack, small feature, Windows host, no tmux) is a protocol violation.

## Existing `team-protocols/` Resources

`developer-protocol.md`, `reviewer-protocol.md`, `lead-protocol.md`, `role-selection-table.md` carry over verbatim — they are the authoritative spawn-coordination spec.

## Anti-Patterns

- Spawning a subagent for a single-file 3-line edit (cost discipline violation)
- Multiple writing agents on the same file in parallel (race condition)
- Inline execution of work that exceeds 3 deliverables or 30 minutes (context overflow risk)
- Skipping G7 structured spawn payload — every Agent spawn MUST include `trace_id`, `goal`, `constraints`, `state_slice`, `allowed_tools`, `budget`, `untrusted_inputs` per the schema in `plugin/schemas/spawn-payload.schema.json`
- Trusting subagent return without G7 return-contract validation (see `subagent-stop-learnings.py` hook)
- Subagent that itself has Task spawning without setting `parent_trace_id` in the child payload — defeats `subagent-depth-guard.py` chain tracking (Phase 4 #4)

## Pairing

- `untrusted-content-wrapping.md` — subagent return values must be wrapped per G1 before re-injection into orchestrator context
- `memory-discipline.md` — subagent reports captured (opt-in) follow L3 schema
- `ralph-budget.md` — RALF iterations spawn subagents; aggregate budget enforced session-wide
