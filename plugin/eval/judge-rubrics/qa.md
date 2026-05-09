# QA Rubric

## Overview

Evaluates `/qa` output — verification, bug reports, exploratory tests, coverage audits. Six dimensions × five levels. Anchored to context-driven testing (Bach/Kaner) heuristics: SFDPOT, CIDTESTD, P×I risk matrix, SBTM (session-based test management).

## Dimensions

### Dimension 1: Task Classification
Correctly identified the QA mode: verification / bug-report / test-creation / coverage / exploratory.

- **Level 1:** Mode misread (e.g., wrote tests when asked to verify)
- **Level 2:** Mode unstated; output ambiguous
- **Level 3:** Mode named; output matches
- **Level 4:** Mode named + scope boundaries set + handoff to sibling skill noted
- **Level 5:** All of L4 + acknowledges when a request straddles modes (e.g., "verification + opportunistic exploratory")

### Dimension 2: Bug-Report Completeness
For bug-report tasks: STR (Steps to Reproduce) + Expected + Actual + Environment + Severity + Priority + Reproduction rate.

- **Level 1:** Title + sentence ("Login broken")
- **Level 2:** STR present; Expected/Actual missing
- **Level 3:** STR + Expected + Actual + Environment
- **Level 4:** All of L3 + Severity + Priority (separated, not conflated) + Reproduction rate
- **Level 5:** All of L4 + first-failure data preserved (logs / screenshots / IDs) + workaround noted

### Dimension 3: Heuristic Application
Applied Bach/Kaner SFDPOT (Structure / Function / Data / Platform / Operations / Time) or CIDTESTD where appropriate.

- **Level 1:** Generic "test happy path"; no heuristic
- **Level 2:** One heuristic mentioned; not applied
- **Level 3:** Heuristic named + a few axes covered
- **Level 4:** Heuristic systematically applied across axes; gaps acknowledged
- **Level 5:** All of L4 + multiple heuristics combined (e.g., SFDPOT for coverage + CIDTESTD for product elements)

### Dimension 4: Risk-Based Prioritization
Used P × I (Probability × Impact) matrix for non-trivial assessments; high-risk areas tested first.

- **Level 1:** Tests sequenced arbitrarily; no risk reasoning
- **Level 2:** Risk language present without rating
- **Level 3:** P × I rating per area
- **Level 4:** P × I matrix drives test sequencing; rationale shown
- **Level 5:** All of L4 + matrix re-evaluated as new info surfaces (living risk model)

### Dimension 5: SBTM Discipline
For exploratory tasks: charter / session report / debrief structure.

- **Level 1:** Free-form notes; no structure
- **Level 2:** Some structure; charter or report missing
- **Level 3:** Charter + session log
- **Level 4:** Charter + session log with TBS (test/bug/setup) time split + debrief
- **Level 5:** All of L4 + follow-up sessions queued from open questions (chartered, not lost)

### Dimension 6: Boundary Discipline
Clear handoff to `/test-strategy` (design) and `/test-local` / `/run-tests` (execution).

- **Level 1:** Designs full pyramid + runs CI suite inside qa output
- **Level 2:** Boundary blurred; some test-strategy work duplicated
- **Level 3:** Stays in QA mode; defers others ad-hoc
- **Level 4:** Explicit deferrals named (e.g., "coverage targets → /test-strategy")
- **Level 5:** All of L4 + sibling-skill references with intended payload

## Scoring Logic

- **Aggregate:** average of D1–D6
- **Pass threshold:** 4.0
- **Judge model:** Haiku default; Sonnet for safety-critical / regulated domain reports

## Anti-Patterns (Auto-Fail)

- Bug report without STR (cannot reproduce)
- Severity and Priority conflated into a single rating
- "Test the happy path" with no heuristic-driven coverage
- Exploratory session without a charter (SBTM violation — pure ad-hoc)
- QA output that re-derives test pyramid (belongs in `/test-strategy`)

## Calibration Reference

- **Known-good:** `plugin/eval/calibration/qa/good/*`
- **Known-bad:** `plugin/eval/calibration/qa/bad/*`
