---
name: team-protocols
description: Shared protocols for multi-agent team coordination — execution model, named subagent spawning via the Agent tool, file conflict prevention, developer/reviewer/lead protocols, role selection table, G7 spawn payload + return contract schemas. Referenced by multi-agent workflow skills (`/develop`, `/team-bugfix`, `/feature-design`). Not directly user-invoked. Use when authoring or auditing a multi-agent skill that spawns named subagents.
---

# Multi-Agent Orchestration

Base protocols for coordinating a team of named subagents in Claude Code. This skill is not invoked directly — it is referenced by workflow skills via `@team-protocols`.

## CRITICAL — orchestration skills MUST NOT use `context: fork`

Per Anthropic Claude Code docs:

> "Subagents cannot spawn other subagents."

When a workflow skill has `context: fork` in its frontmatter, Claude Code runs the entire skill body inside a **forked subagent** (typically `general-purpose`). Inside that subagent, the `Agent` tool is unavailable — and the orchestration pipeline this protocol defines cannot execute. The skill will detect the missing primitive and either HALT or fall back to inline single-agent work, leaving the user wondering why the multi-agent pipeline never ran.

**Rule**: any skill that follows this protocol (spawns Developer / Reviewer / QA via the `Agent` tool) MUST NOT have `context: fork` in its frontmatter. The skill must run in the main conversation thread to retain access to the `Agent` tool.

Confirmed alpha.25 failure mode: `develop` / `team-bugfix` / `feature-design` initially shipped with `context: fork` (intent: isolate skill body from main context). User ran `/ai-assets:develop`, Claude Code forked into a `general-purpose` subagent, the subagent had no `Agent` tool, the skill correctly identified this and refused to do the work inline. Fix: removed `context: fork` from all three orchestration skills. They now run in the main thread where `Agent` is available.

`feature-dev` (single-agent fallback that does the work itself, no spawning) keeps `context: fork` — that's correct, it doesn't need to orchestrate.

## Execution Model

You are the Lead. You run in the main conversation thread and coordinate the team by spawning named subagents via the **`Agent` tool** (Claude Code's canonical primitive for delegating work to an isolated context).

**Hard invariant**: every agent role MUST run as a NAMED subagent spawned via `Agent`, with its own isolated context. The Lead (main thread) NEVER executes Developer / Reviewer / QA work inline with `Bash`/`Read`/`Edit`. If you skip the spawn and do the work directly in the main thread, you have violated this protocol — the user loses the ability to inspect each role independently and the pipeline gates collapse to procedural-only enforcement.

> **Common failure mode (observed alpha.23):** the skill body describes roles ("Agent 1 — Developer", "Agent 2 — Reviewer") but never issues a literal `Agent(...)` call. The model treats the description as documentation and proceeds inline with `Bash`/`Read`/`Edit`. The fix: every role-spawn step in this protocol contains an explicit `Agent({...})` invocation example that the workflow MUST execute, not paraphrase.

> The literal `Agent({...})` invocation template, the JSON G7 spawn-payload example, the validate-and-pass-through pattern, and the role-by-role spawn map (which `subagent_type` per role) live in [`spawn-pattern.md`](./spawn-pattern.md). Load it when authoring a workflow skill that needs to spawn DEV/REVIEW/QA — it carries the executable templates.

## Two Paths — Subagents OR Agent Teams

Two execution paths are supported. Both preserve the DEV → REVIEW → QA gate semantics — only the execution mechanism differs.

**MANDATORY default: Path B (Agent Teams).** Path B MUST be selected for every multi-agent workflow. It gives the user a visual team panel, Shift+↓ to switch context into any teammate, dedicated transcript per role, and a shared task list with `dependsOn`. Path A is **fallback-only** and may be selected ONLY when Path B Step 1 returns a hard technical block (defined below). Any other downgrade is a protocol violation — there is **no silent fallback** for non-technical reasons.

**Hard technical block** = the natural-language team creation in Path B Step 1 actually fails (Anthropic Agent Teams API not exposed in the current Claude Code session, typically because `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` is not set, or the Lead is itself running inside a subagent that has no access to team primitives). In that case — and ONLY in that case — silently fall back to Path A and continue without re-asking the user.

**Invalid reasons to downgrade Path B → Path A** (these are protocol violations — never use them):
- "the pipeline is sequential, parallelism doesn't help" — Path B's value is UX, not parallelism
- "Path A is simpler / cleaner / fewer tools" — Path B's panel gives strictly more visibility
- "tmux / iTerm2 not available" — Path B has `in-process` display mode that works on every terminal
- "Windows host" / "no Unix tools" / "no WSL" — Agent Teams is platform-independent in `in-process` mode
- "small / simple feature" — size is irrelevant to path selection
- "single-stack project" — stack count is irrelevant to path selection

The full anti-rationalization checklist with observed failure modes (alpha.26 / alpha.27 / alpha.30) lives in [`path-selection-rules.md`](./path-selection-rules.md).

**Detection is implicit, not explicit.** Do NOT run an explicit env-var check (no `echo $CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` Bash call) — that triggers a tool-permission prompt for the user without adding value. Just attempt Path B Step 1 directly. If it succeeds you're in Teams mode. If it returns "Agent Teams not enabled" or similar, fall back to Path A immediately and proceed.

### Path B — Agent Teams (MANDATORY default — try this FIRST)

Lead drives via natural language. Each teammate is a full Claude Code session with switchable context. User can Shift+↓ to switch teammates, Enter for transcripts, and Ctrl+T for the shared task list. This is the path the workflow MUST use unless a hard technical block at Step 1 forces Path A.

### Path A — Subagents (technical-block fallback only, sequential)

Fallback path used ONLY when Path B Step 1 returns a hard technical block. Per role, the Lead invokes `Agent({...})` and waits for return. Sequential by default; lower token cost; works in every Claude Code environment. Never selected as a primary choice — only on documented technical failure of Path B.

> The full Path A / Path B body (team-create natural-language template, task-list dependency graph, gate enforcement, the `in-process` vs `tmux` display-mode rules, and the comprehensive "no silent fallback" anti-rationalization checklist with all invalid Path A triggers) lives in [`path-selection-rules.md`](./path-selection-rules.md). Load it when authoring a workflow skill that supports both paths or auditing one for compliance with the dual-path rules.

### Hard rule for both paths

Whichever path is active, the Lead NEVER does Developer/Reviewer/QA work inline with `Bash`/`Read`/`Edit`. The role-isolation invariant applies in both modes — only the spawn mechanism differs.

## Communication Rules

- Every agent reply is the literal return value of an `Agent` tool call. **Never paraphrase or simulate an agent's response.**
- The Lead orchestrates, tracks progress, prints status tables, enforces gates. The Lead does NOT do Developer / Reviewer / QA work itself.
- If a return contract is missing fields required by the next role's protocol — reject it and re-spawn the originating role with a corrected prompt before the next role starts.
- All HANDOFF data flows through the return contract's `result` field as structured JSON, not as free-form prose.

## G7 Contracts and File Conflict Prevention

Every spawn embeds a JSON payload conforming to `plugin/schemas/spawn-payload.schema.json`. Every return embeds a JSON contract conforming to `plugin/schemas/return-contract.schema.json`. The `subagent-start-budget.py` hook validates the spawn payload + enforces budget; the `subagent-stop-learnings.py` hook validates the return.

**Single instance per role** — except Developers, where one instance per affected subproject stack is allowed. Do NOT spawn multiple Reviewers or multiple QA agents.

**Only ONE agent may edit files at any time.** Multiple Developers get `isolation: "worktree"`. Reviewer is always read-only (`disallowedTools: ["Write", "Edit"]`).

> The full G7 spawn-payload + return-contract JSON examples, the `needs_clarification` halting protocol, and the file-conflict prevention rules (writing-agent queueing, Lead enforcement, multi-Developer worktree merge order) live in [`g7-contracts.md`](./g7-contracts.md). Load it when authoring a workflow that needs the literal contract shapes or the conflict-prevention sequencing rules.

## Protocols

Apply these protocols to all agents in the team:

- **Developer protocol**: [`developer-protocol.md`](./developer-protocol.md) — task implementation, self-verification, handoff format, review iterations
- **Reviewer protocol**: [`reviewer-protocol.md`](./reviewer-protocol.md) — independent verification, ghost change detection, issue reporting
- **Lead protocol**: [`lead-protocol.md`](./lead-protocol.md) — orchestration, progress tracking, escalation, final summary
- **Role selection**: [`role-selection-table.md`](./role-selection-table.md) — subproject-to-developer mapping and spawning rules

## Integration

- **Used by**: `/develop`, `/team-bugfix`, `/feature-design` (multi-agent workflows)
- **Schemas**: `plugin/schemas/spawn-payload.schema.json`, `plugin/schemas/return-contract.schema.json` (G7 contracts)
- **Hooks**: `subagent-start-budget.py` (validates spawn payload + enforces budget), `subagent-stop-learnings.py` (validates return contract + opt-in learnings capture)
- **Rules**: `subagent-isolation` (delegation patterns + bounded recursion), `untrusted-content-wrapping` (G1 wrap on subagent returns)
- **Reference**: [Anthropic Claude Code subagents documentation](https://docs.claude.com/en/docs/claude-code/sub-agents)
