---
description: When to delegate to subagents vs work inline. Code-modifying stages are sequential per file; analysis stages may be parallel. Plugin agents are bounded-recursion (only feature-design-lead has Task tool); other agents cannot spawn further. Activates whenever multi-step or multi-stack work is being planned, before delegation decisions are made.
---

# Subagent Isolation and Delegation

When to spawn subagents vs do work in the main thread. When to run subagents in parallel vs sequentially. Bounded-recursion guarantee for v0.1.

## Routing Rules

| Use case | Mechanism | Why |
|---|---|---|
| Independent investigation, audit, parallel reviews of distinct artefacts | `Agent` × N in parallel | Multiple findings merged at end; outputs are documents, not code edits |
| Multi-stack code change | `TeamCreate` + role-mapped developers + reviewer + qa | When `TeamCreate` available; otherwise sequential `Agent` calls |
| Code-modifying stages of any workflow (write/edit ops) | Sequential `Agent` calls or `SendMessage`, **one writer at a time per file** | File conflict prevention — mandatory |
| Document-production stages (analysis, design, audit) | Parallel `Agent` × N permitted | Even within code-touching workflows, design phases parallelize safely |
| Single-file edit | Inline (no subagent) | Cost discipline |
| Anything > 3 deliverables / > 30 min | Mandatory subagent decomposition | Context budget discipline |

## Hot Rule

**Code-modifying stages are sequential per file; analysis and document-production stages may be parallel.** This replaces over-broad "always sequential for code-touching" wording.

## Bounded Recursion Guarantee (v0.1)

In plugin v0.1, only `feature-design-lead` agent has `tools: Task` (the spawn primitive). All other plugin-shipped agents — `security-engineer`, `eval-judge`, `memory-curator`, plus 22 normalized domain agents — explicitly DO NOT have Task in their tools list. They cannot spawn further subagents.

Recursion depth is therefore at most 2: main thread → feature-design-lead → spawned domain agents (engineers, designers, etc.). No infinite loop risk.

If future versions add Task to additional orchestrator agents, add a `subagent-depth-guard.py` hook that tracks depth via the `trace_id` chain in the G7 spawn payload and rejects spawn beyond depth 3.

## Runtime Detection of `TeamCreate`

The `team-dev` (renamed to `develop`) and `team-bugfix` skills probe for the team primitive at activation time per existing `team-protocols/SKILL.md` detection logic. Fall back to standalone `Agent` calls if absent. No design changes needed; existing logic carries over.

## Existing `team-protocols/` Resources

`developer-protocol.md`, `reviewer-protocol.md`, `lead-protocol.md`, `role-selection-table.md` carry over verbatim — they are the authoritative spawn-coordination spec.

## Anti-Patterns

- Spawning a subagent for a single-file 3-line edit (cost discipline violation)
- Multiple writing agents on the same file in parallel (race condition)
- Inline execution of work that exceeds 3 deliverables or 30 minutes (context overflow risk)
- Skipping G7 structured spawn payload — every Agent spawn MUST include `trace_id`, `goal`, `constraints`, `state_slice`, `allowed_tools`, `budget`, `untrusted_inputs` per the schema in `plugin/schemas/spawn-payload.schema.json`
- Trusting subagent return without G7 return-contract validation (see `subagent-stop-learnings.py` hook)

## Pairing

- `untrusted-content-wrapping.md` — subagent return values must be wrapped per G1 before re-injection into orchestrator context
- `memory-discipline.md` — subagent reports captured (opt-in) follow L3 schema
- `ralph-budget.md` — RALF iterations spawn subagents; aggregate budget enforced session-wide
