---
name: qa
description: Use when the user asks to validate a feature, write or improve tests, report a bug, or audit acceptance criteria coverage. /qa = QA-task workflows (verification, test creation, bug reports, exploratory). /test-strategy = test design principles + pyramid + coverage targets (knowledge). /test-local = test execution workflow.
context: fork
argument-hint: [feature description, bug report, or test target]
---

# QA

Use this workflow for verification and test quality work.

## Domain Expertise

Three industry-canonical frameworks shape every QA task in this skill.

### Heuristic Test Strategy Model (Bach / Kaner)

Questioning lenses for test design. Walk through each mnemonic for any new feature to surface test conditions before writing tests.

| Mnemonic | Lenses | Use for |
|---|---|---|
| **SFDPOT** ("San Francisco Depot") | Structure, Function, Data, Platform, Operations, Time | Product coverage — what to test |
| **CIDTESTD** | Capability, Inputs, Data, Tests, Errors, Stress, Time, Design | Test technique selection — how to test |

Reference: James Bach, [Rapid Testing Methodology](https://www.satisfice.com/rapid-testing-methodology) and the HTSM one-page reference.

### Session-Based Test Management (Bach 2000)

Structure for exploratory testing.

| Element | Length | Contents |
|---|---|---|
| **Charter** | 30–120 min | Focused mission, e.g., "Investigate file upload handling under network failure" |
| **Session report** | Written during session | Time, charter, areas covered, bugs, issues, todo, % time on test design vs investigation vs setup |
| **Debrief** | 5–15 min | Review with team lead — surfaces patterns, refines future charters |

Reference: Jonathan Bach, [SBTM 2000 paper](https://www.satisfice.com/download/session-based-test-management).

### Risk-Based Testing (ISO/IEC/IEEE 29119-1)

Test depth scales with risk score = **Probability × Impact** (3×3 matrix, H/M/L per axis, 9 cells).

| Probability factors | Impact factors |
|---|---|
| Code complexity | Business criticality |
| Change frequency | User-base size |
| Dev team experience | Regulatory exposure |
| Third-party dependency churn | Financial loss potential |

High P × High I → exhaustive testing + automation. Low P × Low I → smoke only.

## 1. Determine the QA Task

Classify the request as one of:

- Feature verification
- Bug report
- Test creation
- Test improvement
- Exploratory testing
- Coverage review

## 2. Gather Context

Read:

1. `TESTING.md` if present
2. Root `AGENTS.md`
3. Relevant scoped `AGENTS.md`
4. Feature brief, bug report, or changed code in scope
5. Existing tests for the target area

## 3. Execute the Task

### Feature Verification

- Map acceptance criteria to observable behavior
- Check happy path, edge cases, and error paths
- Record pass, fail, or partial status with evidence

### Bug Report

- Reproduce the issue
- Capture logs, errors, and minimal repro
- Write a structured report using the template below

**Bug report template** (all fields required unless marked optional):

| Field | Format / values |
|---|---|
| Title | One line, includes severity hint, e.g., `[BUG] Login button unresponsive after 2 failed attempts` |
| Severity | `S1 Critical` / `S2 Major` / `S3 Minor` / `S4 Cosmetic` (impact on system) |
| Priority | `P1` / `P2` / `P3` / `P4` (urgency to fix — separate from severity) |
| Steps to reproduce (STR) | Numbered, deterministic |
| Expected behavior | What should happen |
| Actual behavior | What happens instead |
| Environment | OS / browser / app version / build / device / region |
| First seen | Timestamp + commit / release / build |
| Repro rate | `1/1`, `1/10`, intermittent, etc. |
| Attachments | Screenshots / video / logs (attached or linked) |
| Workaround | If known (optional) |

### Test Creation or Improvement

- Identify coverage gaps
- Write or improve tests using the project's existing patterns
- Prefer deterministic tests and narrow scope first

### Exploratory Testing

- Identify risky or recently changed areas
- Explore happy path, invalid input, state transitions, and regressions
- Record issues with severity and reproduction steps

### Coverage Review

- Review current coverage signals
- Identify important untested logic
- Recommend the next highest-value tests

## 4. Apply the Quality Gate

Check:

- Existing tests still pass
- New tests are deterministic
- Acceptance criteria are covered where relevant
- Bug reports include evidence and reproduction steps

## 5. Report

Summarize:

- What was tested
- Issues found
- Tests added or improved
- Coverage impact if relevant
- Recommended next steps

## Integration

- Companion skills: `test-strategy`, `run-tests`, `test-local`
- Common follow-up: `bugfix`, `feature-dev`, `pre-commit`
