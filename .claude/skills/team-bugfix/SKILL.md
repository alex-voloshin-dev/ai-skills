---
name: team-bugfix
description: Fix issues from a code review or deep audit document using a coordinated multi-agent team — developer(s), reviewer, QA, lead orchestrator with mandatory DEVELOP → REVIEW → QA pipeline
context: fork
argument-hint: [path to audit/code-review document]
---

# Multi-Agent Bugfix from Audit

Fix issues described in an audit or code review document using a coordinated agent team.

Read and apply all protocols from `@team-protocols`:
- Execution model (mandatory subagent spawning)
- Agent and file conflict prevention
- Developer protocol (from `developer-protocol.md`)
- Reviewer protocol (from `reviewer-protocol.md`)
- Lead orchestration protocol (from `lead-protocol.md`)
- Role selection table (from `role-selection-table.md`)

## Gather Context

Read `CLAUDE.md` (or `AGENTS.md`) at the project root to identify project structure (monorepo vs polyrepo), subprojects, and tech stacks. This determines which Developer roles to spawn via the role selection table.

## Optional: Local Environment Analysis

If the bug involves local development environment issues (container crashes, networking, Docker problems, service health), or if the user explicitly requests environment analysis — spawn an environment analyzer before starting the fix pipeline:

`name: "env-analyzer"`, `subagent_type: "sre-engineer"`.

The env-analyzer:
- Runs the `@analyze-local` skill procedure: collects Docker container status, logs, networking, resource usage
- Produces a structured diagnosis with root cause analysis and affected services
- Sends findings to the Lead as context for task assignment

**When to activate:**
- User mentions Docker, containers, local env, or service health issues
- Audit document references environment-level failures (not just code bugs)
- User explicitly asks for environment analysis (e.g., "check the local env first")

**When to skip:**
- Pure code-level bugs with no environment component
- User explicitly says to skip environment analysis

The Lead incorporates env-analyzer findings into the task list before starting the DEVELOP → REVIEW → QA pipeline. The env-analyzer does NOT participate in the pipeline itself — it runs once at the start and provides context only.

## Input

Read the audit document provided as the argument. Extract the list of tasks/issues to fix. If the env-analyzer produced findings, merge them into the task list. Each task will go through the full pipeline below.

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
