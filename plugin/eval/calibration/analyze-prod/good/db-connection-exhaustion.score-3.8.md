# Production Diagnostic — `users-api` 5xx error rate climbing

> Severity: P2 | Read-only diagnosis | Region: us-east-1
> Methodology: USE method on RDS — Brendan Gregg; RED on the service — Tom Wilkie
> Observability stack: Prometheus + Grafana, RDS Performance Insights, Cloud Logging

## Summary

`users-api` 5xx error rate rose from 0.05% to 3.8% starting 2026-04-25 13:50 UTC. Root cause: connection pool exhaustion on the RDS Postgres `users` cluster — pool saturated at 100/100 active, queue p99 = 4.2s, then HikariCP times waiters out at 30s causing 503 responses. Saturation, not utilization, is the failing axis.

## RED Method — `users-api` (last 20m)

| Metric | Value | Baseline | Verdict |
|---|---|---|---|
| Rate | 4,200 rps | 4,000 rps | mild rise; not the cause |
| Errors | 3.8% (5xx) | 0.05% | **CRITICAL** |
| Duration p99 | 8.4s | 240ms | **CRITICAL** |

Source: Grafana `users-api / RED` dashboard. Saved Prometheus query: `sum(rate(http_requests_total{service="users-api",status=~"5.."}[5m])) / sum(rate(http_requests_total{service="users-api"}[5m]))`.

## USE Method on RDS `users` cluster

| Axis | Value | Threshold | Verdict |
|---|---|---|---|
| Utilization (CPU) | 41% | 80% | nominal |
| Utilization (memory) | 68% | 90% | nominal |
| **Saturation (connection pool)** | 100/100 active; pool queue p99 = 4.2s | > 90% pool = bad | **CRITICAL** |
| Errors (DB-level) | 0 | 0 | nominal — error surfaces at the app, not the DB |

The DB itself is healthy. Saturation is on the application-side connection pool, not on RDS.

Source: RDS Performance Insights (link) + custom Prometheus exporter `pgbouncer_pool_active_connections{cluster="users-prod"}`.

## Logs Evidence

Cloud Logging:
```
2026-04-25T13:52:14.227Z [users-api.handler] error="HikariPool-1 - Connection is not
available, request timed out after 30001ms" trace_id=a7f3...
[447 occurrences in last 5m]
```

The 30s timeout is the HikariCP default; it confirms the wait queue is exceeding the timeout.

## Distributed Tracing

Sampled 30 5xx-returning traces from APM:
- 28/30 spent > 30s in `db.acquireConnection` span before failing
- 2/30 had genuine query errors (unrelated)

So 93% of the 5xx population is connection-pool starvation specifically.

## SLO Status

`users-api availability` SLO:
- Target: 99.9% / 30 days
- Current 30d: 99.74%
- Error budget remaining: -260% (budget exhausted; in deficit)
- 1h burn rate: 38× steady-state
- Already burned through the weekly budget; eating into monthly

This is a budget-deficit incident — needs immediate mitigation.

## Severity + Blast Radius

- **P2** verging on P1 if budget continues to burn
- Affected scope: ~3.8% of all user-touching requests fail; estimate 1,600 users / 5min hitting an error toast
- Cascading risk: `auth-service` depends on `users-api`; if its retry budget exhausts, login starts failing too (saw this pattern in the 2025-11 incident)

## Root Cause Hypothesis (MEDIUM-HIGH confidence)

Suspect: a deploy at 13:48 UTC (`users-api@v3.18.0`) changed the user-list endpoint to fetch a related-records join WITHOUT a connection-scoped batch — each request now holds a connection during a slow N+1 scan. Pool saturates under steady traffic.

Confidence MEDIUM-HIGH because we have the deploy timing correlation (2 minutes before incident start) and the trace evidence pointing at acquireConnection waits, but the slow-query culprit hasn't been pinpointed by query-id yet (`pg_stat_statements` review pending).

## Proposed Mitigations (gated on user APPROVE — read-only diagnosis)

These mutate production. **DO NOT EXECUTE without explicit user APPROVE.**

1. **Rollback `users-api` to v3.17.x** (best blast-radius / certainty trade-off given the deploy correlation). Blast: ~3min rolling deploy; reversible.
2. **Raise pool size 100 -> 200** while v3.18.x runs. Blast: +0.4 GB RDS active memory; symptom relief only.
3. **Both** — rollback + buffer pool size for headroom.

Recommend option 1.

## What Was Checked (transparency)

- Prometheus: pool, RPS, error rate, latency time series
- Grafana: USE + RED dashboards
- RDS Performance Insights: top queries (slow-query analysis pending detailed review)
- Cloud Logging: HikariCP timeout pattern
- APM (Datadog): trace samples for 5xx population
- Sentry: 1 new fingerprint (the connection-timeout exception itself)

## Out of Scope

- Code fix for the N+1 query introduced in v3.18.0 — that's `/develop` once SLO is restored
- Pool-size sizing strategy review — would be a follow-up `/architecture` if recurrent
