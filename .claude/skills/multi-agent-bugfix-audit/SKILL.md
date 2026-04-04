---
name: multi-agent-bugfix-audit
description: Fix issues from a code review or deep audit document using a coordinated multi-agent team — developer(s), reviewer, QA, lead orchestrator with mandatory DEVELOP → REVIEW → QA pipeline
context: fork
argument-hint: [path to audit/code-review document]
---

# Multi-Agent Bugfix from Audit

Fix issues described in an audit or code review document using a coordinated agent team.

Read and apply all protocols from `@multi-agent-orchestration`:
- Execution model (mandatory subagent spawning)
- Agent and file conflict prevention
- Developer protocol (from `developer-protocol.md`)
- Reviewer protocol (from `reviewer-protocol.md`)
- Lead orchestration protocol (from `lead-protocol.md`)
- Role selection table (from `role-selection-table.md`)

## Input

Read the audit document provided as the argument. Extract the list of tasks/issues to fix. Each task will go through the full pipeline below.

## Mandatory Pipeline

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

## Agent Roles

### Agent 1 — Developer(s)

Spawned per affected subproject using the role selection table. Each Developer:

- Takes tasks assigned by the Lead one by one from the audit plan
- Implements the fix for each task
- Follows the developer protocol for self-verification and handoff
- After Reviewer approval, notifies the Lead, then takes the next task

### Agent 2 — Reviewer

`name: "reviewer"`, `subagent_type: "software-engineer"` with code-review skill.

- Reviews each fix completed by a Developer, including unit tests
- Follows the reviewer protocol for independent verification
- If approved — responds "Task approved, proceed to the next task"
- If issues found — returns to Developer with file paths, severity, and fix instructions

### Agent 3 — QA

`name: "qa"`, `subagent_type: "qa-engineer"`.

- Receives a task AFTER Developer and Reviewer have finished (fix + review approved)
- Developer sends QA a HANDOFF containing: task name, list of changed files, what behavior changed
- Does NOT run or write unit tests — that is the Developer's responsibility
- Owns higher-level testing: smoke, API, integration, functional, E2E
- Reviews existing higher-level tests for validity — code changes may make them outdated
- Adds new higher-level tests if new behavior is untested at those levels
- Fixes broken higher-level tests caused by the code changes
- Reports test failures or coverage gaps back to the Developer

### Agent 4 — Lead / Orchestrator

Runs in the main thread. Follows the lead protocol for orchestration, progress tracking, and escalation.

- Reads the audit plan, determines affected subprojects, assigns tasks to the right Developer(s)
- Enforces the DEVELOP → REVIEW → QA pipeline — no stage skipped
- Progress table includes: #, Task, Developer, Dev, Review, Review rounds, QA, Status
- Final summary includes: total tasks, review iterations, developers involved, unresolved issues, all changed files grouped by subproject
