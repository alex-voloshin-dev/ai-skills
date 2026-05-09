# Production Diagnostic — `checkout-api` p99 latency spike

> Severity: P2 | Read-only diagnosis | Region: us-east-1, eu-west-1
> Methodology: Four Golden Signals (latency, traffic, errors, saturation) — Google SRE Workbook ch. 5; RED method for service-level (Tom Wilkie / Weaveworks)
> Observability stack: Datadog APM (traces), Prometheus (metrics), Cloud Logging (logs)

## Summary

`checkout-api` p99 jumped from 180ms to 2.4s starting 2026-04-25 14:12 UTC, ~13× regression. Trace evidence attributes the regression to the `inventory-service.GetReservation` downstream call (p99 went 22ms → 1.9s). Inventory's underlying RDS instance is saturated on connection pool. Error budget impact: 47% of weekly budget burned in 2h.

## Golden Signals — `checkout-api` (last 30m)

| Signal | Value | Baseline | Verdict |
|---|---|---|---|
| Latency p50 | 142ms | 88ms | DEGRADED |
| Latency p99 | 2,420ms | 180ms | **CRITICAL** |
| Traffic | 1,840 rps | 1,750 rps | nominal |
| Errors | 0.4% (5xx) | 0.1% | elevated; not the dominant signal |
| Saturation (CPU) | 38% | 35% | nominal — symptom is downstream |

Source: Datadog dashboard `checkout-api / Golden Signals` ([link](https://app.datadoghq.com/dashboard/abc-123/checkout-golden-signals)).

## Distributed Tracing

Compared 50 fast traces (p50 baseline) vs 50 slow traces (p99 last 10m), filtered by `service:checkout-api status_code:200`:

| Span | Fast trace p99 | Slow trace p99 | Delta |
|---|---|---|---|
| `checkout-api.handle` (root) | 178ms | 2,398ms | +2,220ms |
| `inventory-service.GetReservation` (child) | 22ms | 1,910ms | **+1,888ms — primary contributor** |
| `payments-service.AuthorizeCard` | 96ms | 102ms | +6ms |
| `db.checkout.write` | 14ms | 18ms | +4ms |

The latency moved almost entirely in one span. Saved query: `apm.datadoghq.com/saved-views/checkout-slow-vs-fast-2026-04-25`.

## Inventory Service — RED + USE

RED on `inventory-service` (Tom Wilkie / Weaveworks):

| Metric | Value | Baseline | Verdict |
|---|---|---|---|
| Rate | 2,310 rps | 2,200 rps | nominal |
| Errors | 0.0% | 0.0% | nominal |
| Duration p99 | 1,910ms | 24ms | **CRITICAL** |

USE on the RDS Postgres backing `inventory-service` (Brendan Gregg's USE method):

| Axis | Value | Threshold | Verdict |
|---|---|---|---|
| Utilization (CPU) | 62% | 80% | nominal |
| Saturation (DB connection pool) | 100/100 used; queue depth p99 = 142 | > 90% pool = bad | **CRITICAL** |
| Errors | 0 connection errors | 0 | nominal |

`pg_stat_activity` snapshot via Cloud SQL admin (read-only): 100 active connections, 142 waiting in pool queue, longest wait 1.78s.

## SLO Status

`checkout-api availability+latency` SLO:
- Target: 99.5% requests under 500ms / 30 days
- Current 30d performance: 99.61% (was 99.84% before incident)
- Error budget remaining: 53% (was 100% at week start)
- 1h burn rate: 14× the steady-state rate
- Projected exhaustion at current burn: ~5.3h

## Severity + Blast Radius

- **P2** (customer-impacting; not full outage)
- Affected scope: ~38% of checkout requests p99 > 1s; estimate ~700 users / 5min affected based on traffic + sampling
- Cascading risk: if `inventory-service` enters cascading-failure mode, `cart-service` (depends on inventory) follows within ~10m

## Root Cause Hypothesis (HIGH confidence)

Inventory's RDS connection pool is exhausted. Pool size is 100; under current traffic + recent query that holds connection longer (suspect: a slow `SELECT ... FOR UPDATE` on `reservations` introduced in deploy `inventory-service@v2.41.0` at 14:08, four minutes before the spike), pool saturates and waiters queue.

## Proposed Mitigations (gated on user APPROVE — read-only diagnosis)

These will mutate production. **DO NOT EXECUTE without explicit user APPROVE.**

1. **Rollback `inventory-service` to v2.40.x** (lowest blast-radius; reverses the suspected cause). Blast: full inventory traffic during rollout (~3min); reversible via re-deploy.
2. **Raise pool size 100 -> 200** as bandaid (does not fix slow query; treats symptom). Blast: +0.5 GB RDS memory; reversible via config change.
3. **Both** — rollback now, raise pool to 150 as a buffer for next incident. Blast: as above.

Recommend option 1. Awaiting APPROVE.

## What Was Checked (transparency)

- Datadog APM: trace comparison fast vs slow (links above)
- Prometheus: `pool_active_connections{service="inventory-service"}` over 1h
- Cloud Logging: `severity>=WARNING resource.type="cloud_run_revision"` for both services
- Sentry: 0 new exception fingerprints since 14:00
- Honeycomb: not in this stack (Datadog primary)

## Out of Scope

- Code-level fix for the slow query — that's `/develop` once the rollback restores SLO compliance.
