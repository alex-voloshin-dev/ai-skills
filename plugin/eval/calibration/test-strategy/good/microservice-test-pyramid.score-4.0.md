# Test Strategy — `orders-service` (microservice in fleet of 14)

## Stack
- Java 21 + Spring Boot 3.3
- Maven Surefire (unit) + Failsafe (integration)
- Pact Broker for contract tests
- Stryker via Maven plugin for mutation tests on critical paths

## Pyramid Shape (canonical for this stack)

| Tier | Target ratio | Tooling | Speed budget |
|---|---|---|---|
| Unit | ~70% of count | JUnit 5 + Mockito | < 50ms each, full suite < 90s |
| Integration | ~20% | Spring Boot Test slices + Testcontainers | < 5s each, full suite < 8min |
| Contract (consumer + provider) | ~7% | Pact | < 3s each |
| E2E | ~3% | Cucumber + RestAssured against staging | < 30s each, max 20 scenarios |

## Coverage Targets

| Metric | Project-wide | Critical path |
|---|---|---|
| Line coverage | ≥ 85% | ≥ 95% |
| Branch coverage | ≥ 80% | ≥ 90% |
| Mutation score (Stryker) | ≥ 70% | ≥ 85% |

Ratchet policy: **no regression from current value** — coverage report fails the build if any metric drops by more than 0.5pp on the changed package.

## Critical-Path Identification

Per threat model + money handling:
- `OrderService.placeOrder` (entry point, money in)
- `PaymentClient.charge` (idempotent retry)
- `RefundService.issueRefund` (money out)
- `OrderRepository.findByCustomerId` (data leak risk if miscoded)

Critical paths get the higher thresholds AND get property-based tests via jqwik (boundary amounts, currencies, idempotency-key collisions).

## Modern Practices

- **Mutation testing (Stryker for Java):** running on critical-path packages every PR; full sweep nightly. Mutation score is the strongest signal that tests actually verify behaviour vs structure.
- **Property-based (jqwik):** scoped to money math + idempotency-key handling. Hypothesis-style generators for currency tuples.
- **Contract testing (Pact):** consumer side runs in CI; provider verifies against the Pact Broker on every PR. Without this, breaking schema changes in `payments-service` slip through.
- **E2E:** kept deliberately small (< 20 scenarios) — covers user journeys, not branches.

## Speed Budgets — Measurement Plan

- Surefire reports parsed in CI, per-test duration tracked over time
- Tests slower than budget enter a quarantine list (skipped from PR runs, run nightly) with an owner and a 14-day fix window
- Integration suite parallelised via Surefire `forkCount=1C` (one fork per core)

## Tool Selection Rationale

- Maven Surefire/Failsafe over Gradle test: project is on Maven; not a fight worth picking
- Mockito over EasyMock: industry default in Spring ecosystem
- Stryker over PIT: PIT was unmaintained for 11 months; Stryker actively shipping
- Testcontainers over H2: H2 dialect-quirks burned us in Q4 2025; real Postgres only
- Pact over Spring Cloud Contract: shared with Node consumers; Pact has mature multi-language brokers

## Adoption Sequence

1. **Now:** unit + integration thresholds applied; Pact wired
2. **Q3:** Stryker on critical paths; baseline mutation score
3. **Q4:** ratchet mutation score upward as gaps close
