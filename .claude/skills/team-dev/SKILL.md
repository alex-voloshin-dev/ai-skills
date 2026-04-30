---
name: team-dev
description: Develop a feature using a coordinated multi-agent team — developer(s), reviewer, QA, lead orchestrator with mandatory DEVELOP → REVIEW → QA pipeline. Multi-agent version of feature-dev.
context: fork
argument-hint: [PRD path or feature description]
---

# Multi-Agent Feature Development

Develop a feature from documentation using a coordinated agent team with mandatory pipeline enforcement.

Read and apply all protocols from `@team-protocols`:
- Execution model (mandatory subagent spawning)
- Agent and file conflict prevention
- Developer protocol (from `developer-protocol.md`)
- Reviewer protocol (from `reviewer-protocol.md`)
- Lead orchestration protocol (from `lead-protocol.md`)
- Role selection table (from `role-selection-table.md`)

## Gather Context

1. Read `CLAUDE.md` (or `AGENTS.md`) at the project root to identify project structure (monorepo vs polyrepo), subprojects, and tech stacks. This determines which Developer roles to spawn via the role selection table.
2. Read `ARCHITECTURE.md` if present — understand module boundaries, data flow, and deployment topology.

## Input

Gather all input documentation provided by the user:

- **Accepted formats**: PRD, ARD, design doc, implementation plan, ticket/issue, or any structured feature specification
- Read every provided document thoroughly
- Extract and organize:
  - **Goal**: what the feature does (1–2 sentences)
  - **Requirements**: functional and non-functional
  - **Acceptance criteria**: how to verify the feature works
  - **Constraints**: performance, security, compatibility, dependencies
  - **Out of scope**: what this feature explicitly does NOT cover

## Resolve Implementation Plan

<plan_policy>
An implementation plan is MANDATORY. Never start the pipeline without an approved plan.

**If a plan already exists** (from documentation, PRD, ARD, or `/plan` output):
- Use it as-is. Do NOT rewrite, reorder, or simplify it
- Present the loaded plan to the user for confirmation before proceeding

**If no plan exists:**
- Create one from scratch based on parsed requirements and codebase analysis
- Break the feature into ordered, atomic work packages
- Each work package = one logical unit of work assigned to a specific Developer role
- Order by dependency — foundations before consumers
- Interleave test steps with implementation
</plan_policy>

Present the plan to the user:

```
Feature: [name]
Subprojects: [detected from CLAUDE.md]
Developers: [roles to spawn per role-selection-table]
Plan source: [loaded from <file> | created from scratch]
Work packages:
  1. [description] → [subproject] → [developer role] → [file(s)]
  2. [description] → [subproject] → [developer role] → [file(s)]
  ...
```

Wait for user approval before proceeding. The user may reorder, add, remove, or modify work packages.

## Mandatory Pipeline

Every work package from the approved plan MUST pass through ALL three stages in this exact order:

```
DEVELOP → REVIEW → QA
```

### Gate Rules

1. A work package CANNOT enter REVIEW until the Developer sends a complete HANDOFF to the Reviewer
2. A work package CANNOT enter QA until the Reviewer explicitly approves (says "approved")
3. A work package is NOT COMPLETE until QA passes — if QA finds issues, it goes back to DEVELOP
4. If the Developer reports "no changes needed" — the Reviewer STILL must confirm this independently
5. If any agent attempts to skip a stage or declares a work package complete without all three stages — the Lead blocks and forces the correct flow

The Lead MUST reject any attempt to batch, combine, or skip stages.

## Agent Roles

### Agent 1 — Developer(s)

Spawned per affected subproject using the role selection table. Each Developer:

- Takes work packages assigned by the Lead one by one from the approved plan
- Implements the feature code following project conventions and the active role's guidelines
- Writes unit tests for each work package
- Follows the developer protocol for self-verification and handoff
- After Reviewer approval, notifies the Lead, then takes the next work package

**Implementation rules:**
- Follow the plan in the EXACT order approved by the user
- Complete each work package fully before moving to the next
- Do not add work that is not in the plan
- Do not skip work packages considered unnecessary
- Production-quality code — no TODOs, no placeholders, no stubs
- If a work package is blocked or the plan needs correction — escalate to Lead immediately

### Agent 2 — Reviewer

`name: "reviewer"`, `subagent_type: "software-engineer"` with code-review skill.

- Reviews each work package completed by a Developer, including unit tests
- Follows the reviewer protocol for independent verification
- Verifies code follows project patterns, conventions, and the feature's acceptance criteria
- If approved — responds "Task approved, proceed to the next task"
- If issues found — returns to Developer with file paths, severity, and fix instructions

### Agent 3 — QA

`name: "qa"`, `subagent_type: "qa-engineer"`.

- Receives a work package AFTER Developer and Reviewer have finished (implementation + review approved)
- Developer sends QA a HANDOFF containing: work package name, list of changed files, what behavior changed, acceptance criteria for this package
- Does NOT run or write unit tests — that is the Developer's responsibility
- Owns higher-level testing: smoke, API, integration, functional, E2E
- Reviews existing higher-level tests for validity — code changes may make them outdated
- Adds new higher-level tests if new behavior is untested at those levels
- Fixes broken higher-level tests caused by the code changes
- Reports test failures or coverage gaps back to the Developer

### Agent 4 — Lead / Orchestrator

Runs in the main thread. Follows the lead protocol for orchestration, progress tracking, and escalation.

- Reads the approved plan, determines affected subprojects, assigns work packages to the right Developer(s)
- Enforces the DEVELOP → REVIEW → QA pipeline — no stage skipped
- **Plan adherence**: if a Developer needs to deviate from the plan, the Lead pauses the pipeline, presents the deviation to the user, and waits for approval before resuming
- Progress table includes: #, Work Package, Developer, Dev, Review, Review rounds, QA, Status
- Final summary includes: total work packages, review iterations, developers involved, unresolved issues, all changed files grouped by subproject, acceptance criteria status

## Verification

After all work packages complete the pipeline, the Lead runs a final verification:

1. **Build/compile** — project builds without errors or warnings
2. **Lint** — run the project's linter if configured
3. **Test** — run the full test suite (new + existing) to catch regressions
4. **Acceptance check** — review implementation against documentation's acceptance criteria

## Summary

Present the completed work:

- **Feature**: what was implemented
- **Subprojects**: affected areas and Developer roles used
- **Work packages**: total completed, total review iterations
- **Files changed**: list of created and modified files grouped by subproject
- **Tests**: number of tests added (unit + higher-level), pass status
- **Acceptance criteria**: status of each criterion (met / partially met / not met)
- **Notes**: deviations from plan, trade-offs, follow-up items

## Integration

- **Planning**: `/plan` (produces the implementation plan this workflow executes)
- **Precedes**: `/run-tests`, `/pre-commit`, `/create-pr`
- **Protocols**: `@team-protocols` (execution model, agent coordination)
- **Skills**: `test-strategy` skill, `code-review` skill, `context-engineering` skill, `worktree-isolation` skill
