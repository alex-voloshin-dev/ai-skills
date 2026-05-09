# Run Tests Rubric

## Overview

Evaluates `/run-tests` output — execute the test suite, classify failures, auto-fix the safe ones, escalate the rest. Six dimensions × five levels. Distinct from `/test-strategy` (design) and `/test-local` (local infra sweep).

## Dimensions

### Dimension 1: Stack Detection
Correctly identified the test runner (pytest / vitest / jest / maven / gradle / go test / cargo test).

- **Level 1:** Wrong runner invoked (e.g., `pytest` in a Node project)
- **Level 2:** Runner guessed; mis-flagged
- **Level 3:** Runner detected from manifest (package.json, pyproject.toml, pom.xml)
- **Level 4:** Runner + version + workspace shape (monorepo / single) detected
- **Level 5:** All of L4 + selected sub-runner per package when monorepo (e.g., nx vs vitest project)

### Dimension 2: Failure Analysis
Each failure classified as: code-bug / test-bug / flaky / contract-drift / environment.

- **Level 1:** Failures listed without classification
- **Level 2:** "Test failed" — no class
- **Level 3:** Each failure classified
- **Level 4:** Class + evidence (stack frame, log line, diff) per failure
- **Level 5:** All of L4 + class-frequency summary across the run (e.g., "3 flaky, 1 contract-drift")

### Dimension 3: Auto-Fix Discipline
Fixed obvious safe issues; escalated complex ones; cap of 3 fix attempts per failure (anti-thrash rule).

- **Level 1:** Re-runs failing test 8+ times without classifying or fixing
- **Level 2:** Edits production code on a flaky test
- **Level 3:** Fixes safe (snapshot rebaseline, stale fixture); escalates rest
- **Level 4:** Fix decision logged with rationale; respects 3-attempt cap
- **Level 5:** All of L4 + post-fix delta-run scoped to affected tests only

### Dimension 4: TIA Awareness
Used Test Impact Analysis (`nx affected`, `turbo --filter`, `pytest-testmon`, `jest --changedSince`, `go test ./<changed>`) when available.

- **Level 1:** Always runs full suite
- **Level 2:** Mentions TIA; doesn't use
- **Level 3:** Uses TIA when stack supports it
- **Level 4:** TIA + falls back to full suite at sensible boundaries (release branch, main)
- **Level 5:** All of L4 + reports % suite saved by TIA on this run

### Dimension 5: Coverage Gating
Respects thresholds set by `/test-strategy`; does not re-derive them.

- **Level 1:** Invents a threshold different from strategy
- **Level 2:** Ignores coverage entirely
- **Level 3:** Reads threshold from project config
- **Level 4:** Reads threshold + reports per-package compliance
- **Level 5:** All of L4 + flags drift from strategy ratchet (no regression policy)

### Dimension 6: Output Structure
Pass/fail summary + per-failure analysis + suggested next action.

- **Level 1:** Raw runner output dumped; no synthesis
- **Level 2:** Summary line only
- **Level 3:** Summary + per-failure block
- **Level 4:** Summary + per-failure with class + suggested next action per failure
- **Level 5:** All of L4 + machine-readable section for downstream automation (CI / lead orchestrator)

## Scoring Logic

- **Aggregate:** average of D1–D6
- **Pass threshold:** 4.0
- **Judge model:** Haiku default; Sonnet for non-trivial flake or contract-drift triage

## Anti-Patterns (Auto-Fail)

- Re-runs failing test indefinitely without classification (endless retry)
- Edits production code blindly to make a failing test green
- Wrong runner for the stack (pytest in Node, jest in Go, etc.)
- Invents coverage thresholds inconsistent with `/test-strategy`
- "All tests pass" without showing per-suite counts

## Calibration Reference

- **Known-good:** `plugin/eval/calibration/run-tests/good/*`
- **Known-bad:** `plugin/eval/calibration/run-tests/bad/*`
