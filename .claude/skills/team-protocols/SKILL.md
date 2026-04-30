---
name: team-protocols
description: Shared protocols for multi-agent team coordination — execution model, named subagent spawning, file conflict prevention, developer/reviewer/lead protocols, role selection table. Referenced by multi-agent workflow skills.
---

# Multi-Agent Orchestration

Base protocols for coordinating a team of named subagents. This skill is not invoked directly — it is referenced by workflow skills via `@team-protocols`.

## Execution Model

You are the Lead. You run in the main conversation thread and coordinate the team.

**Invariant**: every agent role MUST run as a NAMED subagent with its own isolated context. The Lead (main thread) never executes agent work inline. Isolated contexts let the user inspect each agent independently and enforce the pipeline gates structurally, not only procedurally.

### Spawn Primitives

Named subagents are spawned via the `Agent` tool. `Agent` is the required primitive — it creates the isolated named context. `TeamCreate` / `SendMessage` / `TaskOutput` / `TaskStop` / `TeamDelete` are an optional persistence layer around `Agent`; when present, they provide a shared task list and a cheaper multi-turn message channel. When absent, `Agent` alone with `run_in_background: true` still satisfies the named-context invariant.

**Detection logic** — run before spawning anything:

1. If `Agent` is unavailable → HALT. Tell the user the harness is missing the sub-agent primitive and name `/feature-dev` (or `/bugfix`) as the single-agent alternative. Do NOT fall back to inline sequential execution — inline execution breaks the named-context invariant and the gate enforcement this skill relies on, even when stage order is preserved on paper.
2. If `Agent` is available and `TeamCreate` + `SendMessage` are also available → use the **Persistent Team** path below.
3. If `Agent` is available but team tools are not → use the **Standalone Agents** path below.

**Persistent Team path** (preferred — cheaper multi-turn iterations, shared task list):

1. Call `TeamCreate({team_name, description})` once. This creates the empty team container; it does NOT accept a members list
2. For each required role, spawn the member via `Agent({team_name: <team>, name: <role>, subagent_type: <type from role-selection-table.md>, run_in_background: true, prompt: <role brief>})`. Typical roles: `developer-<stack>`, `reviewer`, `qa`
3. Drive every agent hop via `SendMessage({to: <name>, ...})`. Messages arrive back automatically
4. Use `TaskOutput` / `TaskStop` to monitor or stop members. Use `TeamDelete` when the workflow ends

**Standalone Agents path** (fallback when team tools missing):

1. For each role, spawn via `Agent({name: <role>, subagent_type: <type>, run_in_background: true, prompt: <role brief>})` — NO `team_name`
2. Reach each agent via `SendMessage({to: <name>, ...})` (this tool usually still works peer-to-peer)
3. If `SendMessage` is also unavailable — fall back to re-spawning the role per hop via foreground `Agent` calls, and carry forward the prior context explicitly in the prompt each time

### Communication Rules

- Every agent reply must come from the actual named subagent (via `SendMessage` return or `Agent` tool result). Never simulate an agent's response in the main thread
- The Lead only orchestrates, tracks progress, prints status tables, and enforces gates
- If a HANDOFF message is missing fields required by the receiving agent's protocol — reject it and request the correctly formatted HANDOFF before the receiver starts work

**If you skip named subagents and execute the work inline — that is a violation of this protocol.**

## Agent and File Conflict Prevention

**Single instance per role** — except Developers, where one instance per affected subproject stack is allowed (see `role-selection-table.md`). Do NOT spawn multiple Reviewers or multiple QA agents. Tasks within a role are processed strictly one at a time, sequentially.

**Only ONE agent may edit files at any time.** Agents take turns — never work on files in parallel.

- **Writing agents**: Developer(s) and QA (if the workflow includes QA). Reviewer is always read-only
- **If multiple Developers are spawned**: they take turns editing, never in parallel. Each Developer only edits files within its assigned subproject
- **Workflow per task is strictly sequential**: Developer works → Developer stops editing → Reviewer reads → (QA works if applicable) → next task
- **No overlap**: Developer MUST NOT start the next task while another writing agent is still active on the current task
- **Shared files** (test helpers, configs, shared utilities): if a writing agent needs to modify a file that another agent also changed in the same task — notify Lead, Lead ensures the other agent is idle before edits proceed
- **Lead enforces**: if two writing agents are active simultaneously or a read-only agent attempts edits — Lead blocks immediately and alerts the user

## Protocols

Apply these protocols to all agents in the team:

- **Developer protocol**: `developer-protocol.md` — task implementation, self-verification, handoff format, review iterations
- **Reviewer protocol**: `reviewer-protocol.md` — independent verification, ghost change detection, issue reporting
- **Lead protocol**: `lead-protocol.md` — orchestration, progress tracking, escalation, final summary
- **Role selection**: `role-selection-table.md` — subproject-to-developer mapping and spawning rules
