# Test Strategy — `pricing-engine` (Python)

## Stack
- Python 3.12, FastAPI
- pytest + pytest-cov + pytest-xdist
- Hypothesis for property-based tests
- mutmut for mutation testing

## Pyramid

| Tier | Ratio | Speed budget |
|---|---|---|
| Unit | ~75% | < 50ms each, suite < 60s |
| Integration | ~20% (FastAPI TestClient + Testcontainers Postgres) | < 5s each, suite < 4min |
| E2E | ~5% (against staging) | < 30s each |

Pyramid shape because the engine is computational — most behaviour is testable without a server.

## Coverage Targets (line + branch + mutation, with percentages)

| Metric | Project | Critical (`pricing/rules.py`, `pricing/discounts.py`) |
|---|---|---|
| Line | ≥ 90% | ≥ 95% |
| Branch | ≥ 85% | ≥ 92% |
| Mutation score (mutmut) | ≥ 65% project; reported per-file | ≥ 80% |

> Mutation score is the headline metric here. Line coverage of 95% means little if mutants survive — the rules engine is full of off-by-one and operator-flip risks.

Ratchet: per-file ratchet via `--diff` ratchet check in CI — coverage on changed files cannot regress.

## Critical-Path Identification

`rules.py` and `discounts.py` carry the business logic; `cart.py` orchestrates. All three paths get:
- Property-based tests via Hypothesis (input strategies for cart contents, customer tiers, promo codes)
- Mutation runs scoped to these files in CI (full project mutation runs nightly)

## Speed Budgets

- pytest-xdist with `-n auto` keeps the suite under the 60s unit budget
- Slow tests above 50ms get marked `@pytest.mark.slow` and run only in nightly
- Hypothesis examples capped at 100 per test in CI; 1000 in nightly

## Modern Practices

- **Mutation testing (mutmut):** required gate on critical files; mutation score reported in PR
- **Property-based (Hypothesis):** rules-engine strategy generators for cart contents
- **Contract testing:** **N/A** — `pricing-engine` is the only consumer of `catalog-service`; both teams the same. Will revisit if we add a second consumer.

## Tool Selection

- pytest over unittest: ecosystem + plugin support
- mutmut over MutPy: mutmut is faster on this project size and actively maintained
- Hypothesis: industry standard for Python property-based testing
- Coverage threshold enforced by `pytest --cov-fail-under=90`

## Adoption Sequence

1. **Now:** line + branch thresholds enforced
2. **Next sprint:** Hypothesis on `rules.py` (5 properties to start)
3. **Q3:** mutmut on critical files
4. **Q4:** ratchet mutation score upward by 5pp
