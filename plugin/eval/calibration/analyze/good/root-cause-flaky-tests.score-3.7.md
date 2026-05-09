# Analysis — Why is the integration test suite flaky?

> Question: integration suite failure rate jumped from 1.2% to 14% over the last 4 weeks. Root cause?
> Frameworks applied: 5 Whys (primary), Fishbone (cross-check across categories)
> Date: 2026-04-23

## Executive Summary

**FACT:** Failure rate rose from 1.2% (Mar 15) to 14% (Apr 21) on the `integration-suite` job in CI. 87% of failures are timeouts on 4 specific tests.
**INFERENCE:** Root cause is shared-fixture contention on the test Postgres container after a parallelism bump in CI config (HIGH confidence).
**RECOMMENDATION:** Per-test isolated schemas (one Postgres database per worker) — concrete remediation below. Confidence: HIGH (matches the 5 Whys chain + Fishbone cross-check).

## Decomposition

Investigated four candidate causes (MECE across the test pyramid):

1. Test code regressions (new flaky assertions)
2. Test data state (cross-test contamination)
3. CI infrastructure (workers, network, image pulls)
4. Application code under test (real regressions surfacing as flakes)

## 5 Whys Chain

1. **Why** is the suite flaky? → 87% of failures are timeout on tests that touch the `orders` table.
2. **Why** are those tests timing out? → Lock waits in Postgres > 30s on those specific tests (evidence: `pg_stat_activity` snapshots in CI logs).
3. **Why** are there lock waits? → Multiple test workers writing to the `orders` table simultaneously without isolation.
4. **Why** are workers sharing tables? → Workers share a single Postgres database; isolation is by transaction-rollback, which doesn't release advisory locks.
5. **Why** did this start now? → CI parallelism was raised from 4 to 12 workers on Mar 14 (commit `e7a44b2`); the contention threshold for advisory locks crossed at ~8 concurrent writers.

Root cause: shared Postgres container + raised CI parallelism = lock-wait contention on a few hot tables.

## Fishbone Cross-Check

| Category | Candidate cause | Status |
|---|---|---|
| People | New tests added without isolation | INFERENCE — possible contributor; not primary |
| Process | CI parallelism change without isolation review | FACT — confirmed via commit history |
| Tools | Postgres advisory lock semantics | FACT — confirmed via pg_locks snapshots |
| Materials | Test fixtures shared across workers | FACT — verified in `tests/conftest.py:42` |
| Measurement | Flaky-test detector window too short | INFERENCE — minor (caught the trend ~7d late) |
| Environment | CI worker capacity | DISMISSED — workers nominal (12% CPU, 30% mem) |

Fishbone confirms the 5 Whys conclusion: process change (parallelism bump) hit a tool limit (advisory locks on shared tables).

## Recommendations

1. **Per-test schema isolation** (PRIMARY): each worker creates a fresh schema; advisory locks scope per-schema. Owner: platform-test. Effort: ~3 engineer-days.
2. **Restore parallelism to 4** (INTERIM, today): unblocks the suite within an hour while #1 lands.
3. **CI isolation-review checklist** for any future parallelism change. Owner: devops-lead.

## Confidence + Sensitivity

- HIGH on root cause (lock-wait contention)
- MEDIUM on whether per-schema isolation is the lowest-effort fix (could also use Testcontainers per-test, but estimated +2 days)
- A counter-hypothesis ruled out: not a network flake (CI worker network metrics flat across the regression window)

## Out of Scope (deferred)

- Concrete schema-isolation implementation → `/develop` once accepted
- CI runner replatform → separate `/architecture` initiative if we want to go further
