# Test Strategy Rubric

## Overview

Evaluates `/test-strategy` output — the design artifact: pyramid shape, coverage targets, tooling. Six dimensions × five levels. Distinct from `/run-tests` (execution) and `/test-local` (local dev sweep).

## Dimensions

### Dimension 1: Pyramid Alignment
Recommendation respects the test pyramid (many unit, fewer integration, fewest E2E) — or articulates an alternative (Kent Dodds testing trophy) with rationale.

- **Level 1:** Inverts pyramid (E2E-heavy) without rationale
- **Level 2:** Pyramid named; ratios off
- **Level 3:** Pyramid shape recommended; ratios reasonable
- **Level 4:** Pyramid OR trophy chosen explicitly with stack-fit rationale (e.g., "trophy fits SPA — integration is the value layer")
- **Level 5:** All of L4 + ratios anchored to time/cost budget across CI tiers

### Dimension 2: Coverage Targets
Specific (line / branch / mutation) with percentages, not "high coverage".

- **Level 1:** "Should have good coverage"; no number
- **Level 2:** One number for "coverage" without dimension
- **Level 3:** Line OR branch percentage stated
- **Level 4:** Line + branch + mutation thresholds; per-package overrides where critical
- **Level 5:** All of L4 + ratchet policy (no regression past current value)

### Dimension 3: Critical-Path Identification
Auth / payment / data mutation flagged for higher coverage.

- **Level 1:** Uniform target; no path-specific bumps
- **Level 2:** Critical path mentioned; coverage same as rest
- **Level 3:** Critical paths listed with raised thresholds
- **Level 4:** Critical paths + property-based / mutation tests scoped to them
- **Level 5:** All of L4 + threat-model-driven path enumeration (auth, money, PII)

### Dimension 4: Speed Budgets
Unit < 50ms / integration < 5s / E2E < 30s applied (or stack-justified deviation).

- **Level 1:** No timing budgets
- **Level 2:** "Tests should be fast" without numbers
- **Level 3:** Per-tier budgets stated
- **Level 4:** Per-tier budgets + measurement plan + flake-quarantine policy
- **Level 5:** All of L4 + parallelization strategy (sharding / worker count) sized to budget

### Dimension 5: Modern Practices Named
Mutation testing (mutmut / pitest / stryker), property-based (Hypothesis / fast-check), contract testing (Pact) named where relevant.

- **Level 1:** None named; example-only tests assumed
- **Level 2:** One named; not justified for the stack
- **Level 3:** At least two named with applicability
- **Level 4:** Mutation + property-based + contract addressed (each: included or explicitly skipped with reason)
- **Level 5:** All of L4 + adoption sequence (e.g., "start with property-based on parser; mutation in Q3")

### Dimension 6: Tool Selection
Picks the right runner / framework for the stack (pytest vs jest vs vitest vs JUnit / Maven Surefire vs go test).

- **Level 1:** Wrong tool for stack (e.g., pytest on Node)
- **Level 2:** Tool named without rationale
- **Level 3:** Stack-appropriate tool named
- **Level 4:** Tool + plugin set (coverage, parallel, snapshot) chosen for stack
- **Level 5:** All of L4 + version pinning + CI-runner integration noted

## Scoring Logic

- **Aggregate:** average of D1–D6
- **Pass threshold:** 4.0
- **Judge model:** Sonnet (strategy quality benefits from broader pattern knowledge)

## Anti-Patterns (Auto-Fail)

- Coverage stated as "high" / "good" without numbers
- E2E recommended for unit-testable logic (inverted pyramid)
- Mutation / property-based / contract testing never named even when relevant
- Wrong runner for the detected stack
- Strategy that sets thresholds the team cannot actually run in CI (no budget reality check)

## Calibration Reference

- **Known-good:** `plugin/eval/calibration/test-strategy/good/*`
- **Known-bad:** `plugin/eval/calibration/test-strategy/bad/*`
