# Develop Rubric

## Overview

Evaluates the output of `/develop` workflow — implementation quality of work packages from a design pack or PRD. Five dimensions × five levels.

## Dimensions

### Dimension 1: Code Quality
Naming, structure, idiom adherence, complexity per project conventions.

- **Level 1:** Violates basic style; unreadable; nonsense names
- **Level 2:** Inconsistent style; unclear names; unjustified complexity
- **Level 3:** Adheres to style; names acceptable; complexity reasonable
- **Level 4:** Idiomatic for the stack; clear names; complexity justified
- **Level 5:** Idiomatic + minimal + DRY; readable as documentation

### Dimension 2: Test Coverage
New code is exercised by tests at appropriate levels (unit + integration where relevant).

- **Level 1:** No tests for new code
- **Level 2:** Tests cover happy path only
- **Level 3:** Happy path + 1–2 edge cases
- **Level 4:** Happy + edge + error paths; integration tests where boundaries cross
- **Level 5:** Comprehensive coverage including failure modes; tests document behaviour

### Dimension 3: Commit Hygiene
Conventional commits, atomic changes, no WIP-left-behind, signed where required.

- **Level 1:** One mega-commit with mixed concerns
- **Level 2:** Multiple commits but unclear messages
- **Level 3:** Conventional commits followed
- **Level 4:** Atomic commits; each compiles and tests
- **Level 5:** Atomic + conventional + body explains WHY

### Dimension 4: PR Description Clarity
Reviewer can scan + understand changes without reading the diff line-by-line.

- **Level 1:** No description, or description copies file list
- **Level 2:** One-line summary, no change list
- **Level 3:** Summary + change list; no testing notes
- **Level 4:** Summary + change list + testing approach + risk
- **Level 5:** All of L4 + screenshots/evidence + linked design refs

### Dimension 5: Performance Impact
No regressions; performance considerations explicit when relevant.

- **Level 1:** Demonstrable regression introduced
- **Level 2:** Suspected regression, no benchmark
- **Level 3:** No suspected regression, no benchmark either
- **Level 4:** No regression; touched paths benchmarked
- **Level 5:** Improvement quantified or acceptable trade-off documented

## Scoring Logic

- **Aggregate:** average of D1–D5
- **Pass threshold:** 4.0
- **Judge model:** Haiku default; Sonnet for performance-critical or security-critical changes

## Anti-Patterns (Auto-Fail)

- Hardcoded credentials in code
- Skipped or disabled tests without justification
- Force-push to shared branches
- Bypassing CI / pre-commit gates
- Mixed feature + refactor in one commit/PR

## Calibration Reference

- **Known-good:** `plugin/eval/calibration/develop/good/*`
- **Known-bad:** `plugin/eval/calibration/develop/bad/*`
