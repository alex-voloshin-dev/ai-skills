# Local Test Sweep — `billing-service` Quality Gate

## Stack Scope

| Tier | Tool | Status | Duration |
|---|---|---|---|
| Static | eslint + tsc | PASS | 22s |
| Unit | vitest | PASS (561/561) | 38s |
| Integration | vitest + Testcontainers (Postgres + LocalStack S3) | PASS (74/74) | 3m 04s |
| Contract (Pact consumer) | pact-js | PASS (12/12) | 11s |
| E2E | Playwright against compose | PASS (8/8) | 4m 18s |
| Load (smoke) | k6 — 30 RPS for 60s, p99 < 300ms | PASS (p99 = 213ms) | 1m 09s |
| a11y | axe-core | PASS (0 violations) | within E2E |

## Quality Gate (the headline output)

| # | Check | Threshold | Actual | Status |
|---|---|---|---|---|
| 1 | Lint | 0 errors | 0 | **PASS** |
| 2 | Typecheck | 0 errors | 0 | **PASS** |
| 3 | Unit pass rate | 100% | 561/561 | **PASS** |
| 4 | Integration pass rate | 100% | 74/74 | **PASS** |
| 5 | Contract pass rate | 100% | 12/12 | **PASS** |
| 6 | E2E pass rate | 100% | 8/8 | **PASS** |
| 7 | Line coverage | ≥ 85% | 88.7% | **PASS** |
| 8 | Branch coverage | ≥ 80% | 83.4% | **PASS** |
| 9 | Mutation score (Stryker on critical files) | ≥ 75% | 79.2% | **PASS** |
| 10 | Load p99 | < 300ms | 213ms | **PASS** |
| 11 | a11y violations | 0 | 0 | **PASS** |
| 12 | Bundle size budget | < 250KB gz | 218KB | **PASS** |
| 13 | Open security advisories on direct deps | 0 critical/high | 0 | **PASS** |
| 14 | Visual regression | not in scope | — | **SKIP** (delegated to design-system repo) |

## Verdict

**Overall: PASS** — every applicable gate green; one explicit SKIP with rationale.

## Commit Advice (wired to gate result)

- Result: PASS → **proceed to commit + push**
- Suggested commit-message subject: `feat(billing): add SCA-3DS challenge flow for EU cards`
- Pre-push: `git push -u origin feat/sca-3ds`
- PR template auto-filled from this report
- If the gate had been FAIL: would have advised hold + listed first failing check

## Infrastructure Lifecycle

- Provision: `docker compose up -d --wait` with healthchecks
- Reuse: Testcontainers singleton across vitest workers
- Cleanup: `try { run } finally { docker compose down -v --remove-orphans }` — runs on success AND failure
- Idempotent re-run safe (purge labelled containers/volumes from prior runs)

## Cross-Platform

OS detection: Linux (Ubuntu 24.04 dev container). Port-check used `ss`. Same helper tested on macOS (`lsof`) and Windows PowerShell (`Get-NetTCPConnection`).
