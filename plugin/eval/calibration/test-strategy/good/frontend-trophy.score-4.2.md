# Test Strategy — `web-app` (React + TypeScript SPA)

## Stack
- React 19, TypeScript 5.7, Vite
- Vitest (unit + component), React Testing Library
- Playwright (E2E)
- MSW (Mock Service Worker) for network in component tests
- Pact (consumer-side) against `bff-service`

## Shape: Testing Trophy (NOT pyramid)

Per Kent Dodds: in modern frontend, **integration tests give the most confidence per dollar**. Pyramid pushes too hard toward isolated component unit tests that pass while the integrated UX is broken.

| Tier | Ratio | Tool | Speed budget |
|---|---|---|---|
| Static (TS + ESLint) | "free" | tsc + eslint | < 30s in CI |
| Unit (pure functions, hooks in isolation) | ~25% | Vitest | < 50ms each |
| **Integration (component + page with MSW)** | **~55%** | Vitest + RTL + MSW | < 1s each |
| E2E (cross-page user journeys) | ~15% | Playwright | < 30s each, max 30 specs |
| Contract (Pact consumer) | ~5% | Pact | runs in CI on schema change |

> Integration is the value layer because that's where component composition + state + network shape user behaviour. Pure-unit hooks are fine to test in isolation, but the bulk of confidence comes from rendered-page tests.

## Coverage Targets

| Metric | Project | Critical (auth, checkout, account-deletion) |
|---|---|---|
| Line | ≥ 80% | ≥ 92% |
| Branch | ≥ 75% | ≥ 88% |
| Mutation score (Stryker for JS) | ≥ 60% | ≥ 80% |

Coverage enforced via `vitest --coverage --reporter=verbose` with thresholds in `vitest.config.ts`. Ratchet: changed files cannot regress.

## Critical-Path Identification

Auth, checkout, account-deletion. Each gets:
- Component-level integration test with MSW (success + 3 failure modes per path)
- Playwright E2E covering the full flow
- Stryker mutation on the underlying logic (`hooks/useAuth.ts`, `pages/checkout/*.ts`)

## Speed Budgets

- Vitest with `pool: 'threads'` + `--shard` in CI
- Playwright sharded across 4 workers; full suite under 8min
- Slow Vitest tests (>1s) flagged via custom reporter; quarantined with owner + 7-day SLA

## Modern Practices

- **Mutation testing (Stryker JS):** scoped to critical-path logic; runs nightly project-wide, per-PR on changed files
- **Property-based (fast-check):** pricing math + form validation; small but high-value coverage (~12 properties)
- **Contract testing (Pact, consumer side):** every BFF schema change verified before merge
- **Visual regression:** intentionally NOT in pipeline (out-of-scope; tracked in design system repo with Chromatic)

## Tool Selection

- Vitest over Jest: native ESM + Vite-native config + 2-3× faster on this project
- Playwright over Cypress: cross-browser (incl. WebKit), better for shared CI workers, parallelism is built-in
- MSW over jest.fn / nock: works at the network layer — closer to real
- Stryker (JS variant): the mature mutation tool in the JS ecosystem

## Adoption Sequence

1. **Now:** line + branch thresholds; MSW + Playwright in CI
2. **Sprint+1:** Pact consumer tests for the BFF schema
3. **Q3:** Stryker on critical paths
4. **Q4:** fast-check property tests on pricing + validators
