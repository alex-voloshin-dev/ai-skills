# Bugfix Rubric

## Overview

Evaluates `/bugfix` output — root-cause analysis quality, fix correctness, regression coverage. Five dimensions × five levels.

## Dimensions

### Dimension 1: Root-Cause Accuracy
Identified cause is the actual cause (not symptom or correlation).

- **Level 1:** Treats a symptom; actual cause undiagnosed
- **Level 2:** Identifies a contributing factor; misses primary cause
- **Level 3:** Identifies primary cause; under-explains why
- **Level 4:** Primary cause identified + explained with evidence (logs, repro)
- **Level 5:** Primary cause + 5-whys analysis + class-of-bug identified

### Dimension 2: Fix Correctness
Fix addresses root cause; preserves intended behaviour elsewhere.

- **Level 1:** Fix doesn't resolve the bug or breaks other behaviour
- **Level 2:** Fixes the symptom but the root cause remains
- **Level 3:** Fixes the root cause; tests pass
- **Level 4:** Fix is minimal + targeted; no scope creep
- **Level 5:** Fix is minimal + targeted + explained as the right level (vs other valid fixes considered and rejected)

### Dimension 3: Regression Risk
Risk of breaking existing functionality is assessed and mitigated.

- **Level 1:** No regression analysis; broad blast radius
- **Level 2:** Acknowledges risk vaguely
- **Level 3:** Identifies risk areas; runs full test suite
- **Level 4:** Identifies + mitigates with new tests for adjacent code
- **Level 5:** All of L4 + canary plan or feature flag for risky paths

### Dimension 4: Test Coverage (regression test mandatory)
A regression test is added that fails without the fix and passes with it.

- **Level 1:** No regression test added
- **Level 2:** Test added but doesn't actually exercise the bug condition
- **Level 3:** Regression test added; passes with fix
- **Level 4:** Regression test + edge-case tests for related scenarios
- **Level 5:** Regression test + edge cases + meta-test (test that proves the test catches the bug if reverted)

### Dimension 5: Performance Efficiency
Fix doesn't introduce new performance overhead unless necessary and documented.

- **Level 1:** Significant new overhead, undocumented
- **Level 2:** Some overhead, not analyzed
- **Level 3:** No noticeable overhead; not measured
- **Level 4:** Measured; no regression
- **Level 5:** Measured + improvement quantified or trade-off documented

## Scoring Logic

- **Aggregate:** average of D1–D5
- **Pass threshold:** 4.0
- **Judge model:** Haiku default; Sonnet for security-related bugs or hot-path performance bugs

## Anti-Patterns (Auto-Fail)

- No regression test (cannot prove the fix works long-term)
- Treats symptom only (root cause documented as "remains under investigation")
- Workaround that masks future failures (try/except swallowing)
- Fix introduces a TODO or FIXME

## Calibration Reference

- **Known-good:** `plugin/eval/calibration/bugfix/good/*`
- **Known-bad:** `plugin/eval/calibration/bugfix/bad/*`
