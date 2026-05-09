# Local Test Sweep — `orders-service` Pre-Commit Verification

## Stack Scope

| Tier | Tool | Status | Duration |
|---|---|---|---|
| Static (lint + typecheck) | ruff + mypy | PASS | 18s |
| Unit | pytest | PASS (412/412) | 47s |
| Integration | pytest + Testcontainers (Postgres + Redis + RabbitMQ) | PASS (84/84) | 4m 12s |
| E2E (local) | Playwright against compose stack | PASS (12/12) | 6m 33s |
| Load (smoke) | k6 — 50 RPS for 60s, p99 < 250ms | PASS (p99 = 198ms) | 1m 10s |
| a11y | axe-core via Playwright | PASS (0 violations) | within E2E |

## Infrastructure Lifecycle

### Provision

`docker compose up -d --wait` brings up:
- `postgres:16` (depends_on healthcheck)
- `redis:7` (healthcheck `redis-cli ping`)
- `rabbitmq:4-management` (healthcheck on management port)
- `orders-service` (depends_on all of the above with `condition: service_healthy`)

`--wait` blocks until all services pass their healthchecks. No raw `sleep` anywhere — readiness is derived from declared health probes.

### Integration tier — Testcontainers usage

For tier-2 integration (pytest), containers are managed via Testcontainers Python:
- Postgres container (real db, real schema migrations applied)
- Redis container (real cache)
- LocalStack container for S3 (real-shaped API)

Mocks reserved for: external paid APIs only (Stripe, SendGrid). Everything we can run, we run.

Container reuse via `testcontainers-singleton` pattern across pytest-xdist workers — single Postgres instance shared, isolation by per-test schema.

## Cross-Platform Commands

OS detected: Linux (CI runner). Port-check helper used `ss -tlnp` (Linux). For local dev, the helper branches:

```python
def find_listener(port):
    if platform.system() == "Darwin":
        return _run("lsof -i :{port} -sTCP:LISTEN".format(port=port))
    if platform.system() == "Windows":
        return _run("powershell -c \"Get-NetTCPConnection -LocalPort {port} -State Listen\"".format(port=port))
    return _run("ss -tlnp 'sport = :{port}'".format(port=port))
```

## Cleanup

`try/finally` ensures cleanup runs on success AND failure:
- `docker compose down -v --remove-orphans` (removes volumes + networks + orphan containers)
- Testcontainers `with` blocks auto-stop containers per test session
- Idempotent — re-running clean removes any stragglers from prior aborted runs

## Quality Gate

| Check | Threshold | Actual | Status |
|---|---|---|---|
| Unit pass rate | 100% | 100% (412/412) | PASS |
| Integration pass rate | 100% | 100% (84/84) | PASS |
| E2E pass rate | 100% | 100% (12/12) | PASS |
| Line coverage | ≥ 90% | 92.3% | PASS |
| Branch coverage | ≥ 85% | 87.1% | PASS |
| Mutation score (mutmut, critical files) | ≥ 80% | 82% | PASS |
| Load p99 | < 250ms | 198ms | PASS |
| a11y violations | 0 | 0 | PASS |
| Type errors | 0 | 0 | PASS |

**Overall verdict: PASS — proceed to commit.**

Commit advice: ready. Suggested commit-message subject already drafted by `/develop` lead.
