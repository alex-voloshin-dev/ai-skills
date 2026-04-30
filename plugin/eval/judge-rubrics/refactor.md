# Refactor Rubric

## Overview

Evaluates `/refactor` output — behaviour-preserving structural change. Five dimensions × five levels.

## Dimensions

### Dimension 1: Behaviour Equivalence
All existing tests pass; no breaking changes to public API surface.

- **Level 1:** Tests fail OR public API breaks
- **Level 2:** Tests pass; one minor public-surface change undocumented
- **Level 3:** Tests pass; public surface preserved
- **Level 4:** Tests pass + new tests added for previously-untested paths exposed by refactor
- **Level 5:** All of L4 + API diff check produces empty diff for public surface

### Dimension 2: Code Improvement
Readability, maintainability, or performance demonstrably improved.

- **Level 1:** Refactor makes code worse (more complex, harder to read)
- **Level 2:** Lateral move (no improvement)
- **Level 3:** Modest improvement (one dimension)
- **Level 4:** Clear improvement (readability OR maintainability OR performance)
- **Level 5:** Multiple dimensions improved + measured (e.g., complexity score before/after)

### Dimension 3: Scope Correctness
Refactor stays within stated goal; no unrelated changes mixed in.

- **Level 1:** Mixes feature changes / bug fixes / unrelated cleanup
- **Level 2:** Mostly on scope; one or two unrelated changes
- **Level 3:** On scope; minor stylistic side-trips
- **Level 4:** Strictly on scope
- **Level 5:** Strictly on scope + scope-creep candidates explicitly noted as future work

### Dimension 4: Test Coverage Preserved
Test suite still exercises the code at same coverage level.

- **Level 1:** Coverage drops materially
- **Level 2:** Coverage drops slightly, not noted
- **Level 3:** Coverage preserved; tests adapted to new structure
- **Level 4:** Coverage preserved + tests improved (clearer names, less brittle assertions)
- **Level 5:** Coverage preserved + tests refactored alongside production code (parallel cleanliness)

### Dimension 5: Documentation Updated
Docstrings, comments, README reflect changes.

- **Level 1:** Docs left referring to old structure
- **Level 2:** Some docs updated, others stale
- **Level 3:** Docstrings updated; README unchanged
- **Level 4:** Docstrings + README + relevant ADRs updated
- **Level 5:** All of L4 + migration note for downstream consumers (if signature evolved)

## Scoring Logic

- **Aggregate:** average of D1–D5
- **Pass threshold:** 4.0
- **Judge model:** Haiku default; Sonnet for refactors that touch performance-sensitive code paths

## Anti-Patterns (Auto-Fail)

- Mixes feature change with refactor
- Tests modified to PASS the new code (rather than refactor maintaining test behaviour) without justification
- Public API breaks without migration guide
- Same-error-repeats:2 pattern triggered (per `ralph-budget.md`) — likely behaviour change masquerading as refactor

## Calibration Reference

- **Known-good:** `plugin/eval/calibration/refactor/good/*`
- **Known-bad:** `plugin/eval/calibration/refactor/bad/*`
