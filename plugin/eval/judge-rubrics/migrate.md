# Migrate Rubric

## Overview

Evaluates `/migrate` output — schema/library/version migration with documented + tested rollback. Five dimensions × five levels.

## Dimensions

### Dimension 1: Plan Completeness
Pre-flight checklist + forward procedure + rollback procedure all documented.

- **Level 1:** No formal plan; ad-hoc steps
- **Level 2:** Forward procedure only; no pre-flight or rollback
- **Level 3:** All three sections; rollback shallow ("revert the deploy")
- **Level 4:** All three sections; rollback procedure detailed and step-by-step
- **Level 5:** All of L4 + dry-run results + dependency graph + go/no-go gates

### Dimension 2: Rollback Safety
Rollback procedure is TESTED and proven reversible (not just documented).

- **Level 1:** Rollback claims to work but never executed
- **Level 2:** Rollback partially tested (e.g., on dev only)
- **Level 3:** Rollback tested on staging
- **Level 4:** Rollback tested on staging + production-shaped data
- **Level 5:** All of L4 + rollback executed in dress rehearsal + recovery time measured

### Dimension 3: Data Integrity
Validation checks confirm data preserved through migration.

- **Level 1:** No integrity check
- **Level 2:** Row-count check only
- **Level 3:** Row count + checksums on key tables
- **Level 4:** Row count + checksums + foreign-key constraints + spot-check business invariants
- **Level 5:** All of L4 + automated parity test comparing pre/post for sampled records

### Dimension 4: Performance Impact
Post-migration performance measured against baseline; regressions identified.

- **Level 1:** No measurement; performance issues discovered in prod
- **Level 2:** Latency measured; no throughput
- **Level 3:** Latency + throughput on staging
- **Level 4:** All of L3 + p95 + p99 + load test
- **Level 5:** All of L4 + canary metrics from production rollout

### Dimension 5: Risk Awareness
Identified risks + mitigations + escalation paths.

- **Level 1:** Risks unidentified
- **Level 2:** 1–2 risks; mitigations vague
- **Level 3:** 3+ risks; each with a mitigation
- **Level 4:** 3+ risks ranked by probability/impact; mitigations detailed
- **Level 5:** All of L4 + named escalation owners + decision tree for each risk type

## Scoring Logic

- **Aggregate:** average of D1–D5
- **Pass threshold:** 4.0
- **Judge model:** Sonnet default (migrations have high blast radius; subtle integrity issues)

## Anti-Patterns (Auto-Fail)

- Untested rollback procedure
- "Rollback by restoring backup" without RTO/RPO commitments
- Data loss detected and not addressed before sign-off
- No staging dry-run for production migration
- Forward procedure depends on a manual step nobody owns

## Calibration Reference

- **Known-good:** `plugin/eval/calibration/migrate/good/*`
- **Known-bad:** `plugin/eval/calibration/migrate/bad/*`
