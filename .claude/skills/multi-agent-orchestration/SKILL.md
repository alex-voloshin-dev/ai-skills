---
name: multi-agent-orchestration
description: Shared protocols for multi-agent team coordination — execution model, named subagent spawning, file conflict prevention, developer/reviewer/lead protocols, role selection table. Referenced by multi-agent workflow skills.
---

# Multi-Agent Orchestration

Base protocols for coordinating a team of named subagents. This skill is not invoked directly — it is referenced by workflow skills via `@multi-agent-orchestration`.

## Execution Model

You are the Lead. You run in the main conversation thread and coordinate the team.

**You MUST spawn each agent role as a NAMED subagent using the Agent tool.** Do NOT execute agent work inline in the main thread. Each agent must be a separate, named subagent instance so the user can inspect each agent's context independently.

- Spawn agents with explicit `name` parameter: e.g. `name: "developer-java"`, `name: "reviewer"`, `name: "qa"`
- Use the `subagent_type` parameter matching the skill from the role selection table
- Use `SendMessage` to communicate between agents — never simulate agent responses in the main thread
- The main thread (you, the Lead) only orchestrates, tracks progress, and prints status tables

**If you skip creating named subagents and instead do the work inline — that is a violation of this protocol.**

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
