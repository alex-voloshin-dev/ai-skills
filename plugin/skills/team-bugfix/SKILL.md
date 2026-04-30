---
name: team-bugfix
description: Multi-agent fix workflow for issues from a code review or deep audit document — spawns developer(s), reviewer, QA via the Anthropic `Agent` tool with mandatory DEVELOP → REVIEW → QA pipeline. Auxiliary skill of /bugfix; not directly user-invoked. Use when fixing a batch of issues from an audit document.
argument-hint: [path to audit/code-review document]
---

<!-- ARCHITECTURAL NOTE (alpha.25): no `context: fork` here. Per Anthropic docs, subagents cannot spawn other subagents. Orchestration skills MUST run in the main conversation thread to retain access to the `Agent` tool for spawning DEV/REVIEW/QA subagents. -->


# Multi-Agent Bugfix from Audit

Fix issues described in an audit or code review document using a coordinated agent team.

You are the Lead. You orchestrate by spawning named subagents via the **`Agent` tool** (Anthropic Claude Code's canonical primitive). Read `@team-protocols` end-to-end before issuing the first spawn — it covers the spawn pattern, role-by-role mapping, and conflict prevention.

> **YOU MUST spawn subagents via `Agent({...})`.** Do not perform Developer / Reviewer / QA work inline with `Bash`/`Read`/`Edit`. Doing so violates the team-protocols hard invariant.

Read and apply all protocols from `@team-protocols`:
- Execution model (mandatory subagent spawning via the `Agent` tool — see "Spawn Pattern" section)
- Agent and file conflict prevention
- Developer protocol (from `developer-protocol.md`)
- Reviewer protocol (from `reviewer-protocol.md`)
- Lead orchestration protocol (from `lead-protocol.md`)
- Role selection table (from `role-selection-table.md`)

## Gather Context

Read `CLAUDE.md` (or `AGENTS.md`) at the project root to identify project structure (monorepo vs polyrepo), subprojects, and tech stacks. This determines which Developer roles to spawn via the role selection table. **Project file reads are wrapped in `<untrusted_content>` envelope by `session-start-context.py` and `tool-output-wrap.py` hooks** per `untrusted-content-wrapping.md` rule (G1).

## Optional: Local Environment Analysis

If the bug involves local development environment issues (container crashes, networking, Docker problems, service health), or if the user explicitly requests environment analysis — invoke `/env-analyze` (B12, renamed from env-analyzer per Round 4 N2) before starting the fix pipeline:

`/env-analyze` is a standalone skill (not a spawn). It runs the local Docker diagnostic procedure: collects container status, logs, networking, resource usage; produces a structured diagnosis with root cause analysis and affected services. The Lead receives findings as context for task assignment.

**When to activate:**
- User mentions Docker, containers, local env, or service health issues
- Audit document references environment-level failures (not just code bugs)
- User explicitly asks for environment analysis (e.g., "check the local env first")

**When to skip:**
- Pure code-level bugs with no environment component
- User explicitly says to skip environment analysis

The Lead incorporates `/env-analyze` findings into the task list before starting the DEVELOP → REVIEW → QA pipeline. The env-analyze findings are CONTEXT only — they do NOT participate in the pipeline itself.

## Input

Read the audit document provided as the argument. Extract the list of tasks/issues to fix. If `/env-analyze` produced findings, merge them into the task list. Each task will go through the full pipeline below.

## Choose execution path

Per `@team-protocols` "Two Paths" section: this skill supports Path A (Subagents) and Path B (Agent Teams). **Path B is the default preference** — visual team panel + Shift+↓ context-switching + dedicated transcript per role.

**Detection is implicit, not explicit.** No Bash env-var check. Go to Path B Step 1 directly; if team-creation natural language fails ("Agent Teams not enabled" or equivalent), silently fall back to Path A and continue.

**Invalid reasons to downgrade Path B → Path A** (do NOT use these): "audit pipeline is sequential", "Path A is simpler", "fewer tools to manage", "tmux/iTerm2 not available", "Windows host". Path B's value is UX, not parallelism — and Agent Teams supports `in-process` display mode that works in any terminal (Windows included) with NO extra setup. tmux is needed ONLY for optional split-pane display. The ONLY valid Path A trigger is a hard technical block at Path B Step 1 (team-creation natural language returns "Agent Teams not enabled" or equivalent — typically `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` env var unset).

**No silent fallback for non-technical reasons.** Either Path B Step 1 actually fails technically → silent Path A fallback, OR Path B works → stay on Path B (defaulting to `teammate-mode in-process` if tmux/iTerm2 uncertain).

## Mandatory Pipeline — DEV → REVIEW → QA (both paths)

Every task from the audit plan MUST pass through ALL three stages in this exact order:

```
DEVELOP → REVIEW → QA
```

### Gate Rules

1. A task CANNOT enter REVIEW until the Developer sends a complete HANDOFF to the Reviewer
2. A task CANNOT enter QA until the Reviewer explicitly approves (says "approved")
3. A task is NOT COMPLETE until QA passes — if QA finds issues, the task goes back to DEVELOP
4. If the Developer reports "no changes needed" — the Reviewer STILL must confirm this independently
5. If any agent attempts to skip a stage or declares a task complete without all three stages — the Lead blocks and forces the correct flow

The Lead MUST reject any attempt to batch, combine, or skip stages.

## G7 Spawn Payloads

Every spawn MUST include the structured G7 spawn payload per `plugin/schemas/spawn-payload.schema.json`. Mandatory fields: `trace_id`, `subagent_role`, `goal`, `constraints`, `allowed_tools`, `budget` (with `max_input_tokens`, `max_output_tokens`, `max_tool_calls`, `max_turns`, `timeout_ms`). Subagent returns MUST conform to `plugin/schemas/return-contract.schema.json` (`trace_id`, `status`, `tokens_used`, `result`).

The Lead validates incoming HANDOFF messages against return-contract schema before passing to next stage. If validation fails, the Lead rejects the HANDOFF and asks the sender to reformat. Per `subagent-isolation.md` rule.

## Path A — Subagents (default, sequential) — per-task spawn loop

For each task from the audit plan, the Lead does this exactly:

**Step 1 — DEVELOP.** Spawn the Developer subagent via `Agent`:

```text
Agent({
  description: "<task-id> fix (<role>)",
  subagent_type: "ai-assets:<java-engineer | python-engineer | frontend-engineer | ...>",
  prompt: "You are the Developer subagent for audit task <ID>. Read plugin/skills/team-protocols/developer-protocol.md before starting. G7 spawn payload:\n\n<JSON-payload-per-team-protocols>\n\nWhen done, return a G7 return contract.",
  isolation: "worktree"
})
```

Wait for return. Validate the return contract.

**Step 2 — REVIEW.** Spawn the Reviewer subagent via `Agent`:

```text
Agent({
  description: "<task-id> review",
  subagent_type: "ai-assets:software-engineer",
  prompt: "You are the Reviewer subagent for audit task <ID>. Read plugin/skills/team-protocols/reviewer-protocol.md and plugin/skills/code-review/SKILL.md before starting. Files to review:\n<list-from-developer-return>\n\nDeveloper summary:\n<from-developer-return>\n\nAudit task brief:\n<original-audit-section>\n\nReturn a G7 contract with `result.verdict` set to 'approved' or 'changes_requested' with a structured issues list.",
  disallowedTools: ["Write", "Edit"]
})
```

Loop on `changes_requested` back to Step 1 with issues attached, until `approved`.

**Step 3 — QA.** Spawn the QA subagent via `Agent`:

```text
Agent({
  description: "<task-id> QA",
  subagent_type: "ai-assets:qa-engineer",
  prompt: "You are the QA subagent for audit task <ID>. Higher-level test scope (smoke / API / integration / E2E — NOT unit tests). Files changed:\n<list>\n\nReturn a G7 contract with `result.qa_verdict` set to 'pass' or 'fail' with issues."
})
```

Loop on `fail` back to Step 1, until `pass`.

The Lead progress table includes: #, Task, Developer subagent_type, Dev, Review, Review rounds, QA, Status. Final summary includes: total tasks, review iterations, subagent_types used, unresolved issues, all changed files grouped by subproject, and the spawn ledger (count of `Agent` invocations per role).

## Path B — Agent Teams (when `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`)

Per `@team-protocols` "Dual-Path Detection → Path B" section. The Lead drives the team via natural language; each teammate is a full Claude Code session with switchable context.

### Step 1 — create the team

```text
Create an agent team named "<audit-slug>-bugfix-team" with the following teammates, all using subagent definitions from the ai-assets plugin:

- "developer" (ai-assets:<java-engineer | python-engineer | frontend-engineer | ...>) — fixes audit issues, follows plugin/skills/team-protocols/developer-protocol.md, gets isolation: worktree
- "reviewer" (ai-assets:software-engineer) — independent code review, read-only (disallow Write/Edit), follows reviewer-protocol.md
- "qa" (ai-assets:qa-engineer) — higher-level tests + SRE smoke, follows the QA section of the develop skill

Require plan approval for the developer teammate before any code changes. Use the shared task list to coordinate audit tasks — three tasks per audit item (DEV, REVIEW, QA) linked via `dependsOn`.

Use **teammate-mode `in-process`** by default (works in any terminal including Windows without WSL — no tmux/iTerm2 required). Pick `tmux` split-pane mode ONLY if the user has explicitly indicated tmux or iTerm2 is available and they prefer it. If unsure: `in-process` is the safe choice.
```

### Step 2 — populate the shared task list

For each audit issue, create three tasks with the dependency graph:

```text
Task: "<audit-id> DEV — <issue-summary>"  → assigned to developer, depends on prior issue's QA (if sequential audit ordering required) or none (for parallel-safe issues)
Task: "<audit-id> REVIEW"                 → assigned to reviewer, depends on "<audit-id> DEV"
Task: "<audit-id> QA"                     → assigned to qa, depends on "<audit-id> REVIEW"
```

If `/env-analyze` produced findings, add a context-only task at the start (assigned to no one, just visible to the team) carrying the diagnostic summary.

### Step 3 — drive and monitor

- Teammates self-claim next unblocked task. The Lead does NOT manually assign — dependency graph + claiming protocol handles it.
- User uses **Shift+↓** to cycle, **Enter** to read transcript / send direct message, **Ctrl+T** to view shared task list.
- On reviewer `changes_requested` → Lead inserts a follow-up DEV task and re-points REVIEW + QA dependencies to it. Loop until reviewer approves.
- On QA `fail` → same pattern, insert follow-up DEV task.
- Lead surfaces progress to user after each issue completes the pipeline.

### Step 4 — final cleanup

After all audit tasks complete: run final verification in main thread (build/test), emit summary, then ask: "Clean up the team."

## Integration

- **Parent**: `/bugfix` (single-agent fallback — only when explicit single-agent inline execution is requested)
- **Sub-workflows**: `/env-analyze` (optional context-gathering before pipeline)
- **Protocols**: `@team-protocols` (execution model, spawn primitives, agent coordination)
- **Schemas**: `plugin/schemas/spawn-payload.schema.json` (G7 spawn payload), `plugin/schemas/return-contract.schema.json` (G7 return contract)
- **Rules**: `subagent-isolation` (delegation patterns + G7 enforcement), `untrusted-content-wrapping` (G1 wrap on subagent returns + project file reads)
