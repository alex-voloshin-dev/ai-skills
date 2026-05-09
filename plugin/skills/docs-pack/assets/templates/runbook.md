# Runbook — `<service-name>`

> Operator-facing runbook. SRE-aligned: every alert has an explicit
> **Diagnose → Mitigate → Verify** path. Keep procedures close to
> commands you can copy and run.

## Service overview

- **Service:** `<service-name>` (e.g. `orders-api`)
- **Purpose:** Accepts and processes customer orders.
- **Owners:** `@team-orders` (Slack `#team-orders`, PagerDuty `orders-oncall`).
- **Repo:** `github.com/example/orders-api`.
- **Production URL:** `https://api.example.com/v1/orders`.
- **Tier:** Tier 1 (customer-facing, revenue-impacting).

## Architecture

See [`architecture.md`](./architecture.md) for the C4 Container
diagram. Quick mental model:

```
client → CDN → API gateway → orders-api → Postgres (primary)
                                       ↘ Redis (cache, idempotency)
                                       ↘ orders-events (Kafka topic)
```

## SLO / SLI / SLA

| Indicator (SLI) | Objective (SLO) | Window | SLA |
|---|---|---|---|
| Availability (2xx + 4xx) / total | 99.95% | 30 days rolling | 99.9% |
| p99 latency `POST /v1/orders` | ≤ 400 ms | 30 days rolling | 1000 ms |
| Error budget burn | < 2× expected | 1h and 6h windows | n/a |

Dashboards: [Grafana → Orders → SLO](https://grafana.example.com/d/orders-slo).

## Alerts

Each alert below is wired in `alerts/orders.yaml` and routes to
PagerDuty `orders-oncall`.

### Alert: `OrdersApiP99LatencyHigh`

**Condition:** p99 latency on `POST /v1/orders` > 800 ms for 5 min.

**Diagnose:**

```bash
# 1. Confirm in Grafana
open https://grafana.example.com/d/orders-slo

# 2. Check pod status
kubectl -n orders get pods -l app=orders-api
kubectl -n orders top pods -l app=orders-api

# 3. Check Postgres slow queries
psql $PG_URL -c "select pid, now()-query_start as runtime, state, query
                 from pg_stat_activity
                 where state != 'idle' order by runtime desc limit 10;"

# 4. Check Redis health
redis-cli -h $REDIS_HOST --latency
```

**Mitigate (in order, stop when latency recovers):**

1. Scale out: `kubectl -n orders scale deploy/orders-api --replicas=12`
2. If Postgres-bound: failover read replicas → primary connection in
   `app-config` ConfigMap (see *Rollback* below for the inverse).
3. If a bad deploy in last 60 min: roll back (see *Rollback*).
4. Last resort: enable degraded mode — set
   `FEATURE_ASYNC_ORDER_INTAKE=true` in the ConfigMap; reload pods.

**Verify:**

- p99 < 400 ms for 10 minutes on the SLO dashboard.
- Error rate `< 0.1%`.
- Resolve the page only after both hold for 10 min.

### Alert: `OrdersApiErrorRateHigh`

5xx rate > 1% for 5 min. Same shape: check pods → check deps → roll back.

### Alert: `OrdersDbReplicationLag`

Lag > 30s for 5 min. Page DB on-call. Likely root: long-running write
transaction or replica disk-IO saturation.

### Alert: `OrdersKafkaLagHigh`

Consumer lag > 10k for 10 min. Scale consumer; check downstream
fanout (`billing-worker`, `notify-worker`).

### Alert: `OrdersOomKilled`

Pod OOMKilled in last 5 min. Check the pod's `kubectl describe`;
likely a payload-size regression — roll back to last known good image.

## Common incidents (top 5 playbooks)

### 1. API p99 latency > 2× SLO (worked example)

**Symptoms:** `OrdersApiP99LatencyHigh` page; users report slow
checkout; Grafana shows p99 climbing past 800 ms.

**Step-by-step:**

1. Acknowledge the page in PagerDuty (within 5 min).
2. Open `#incidents-orders` Slack and post:
   `Acking OrdersApiP99LatencyHigh, investigating. IC: @<you>`.
3. Run the **Diagnose** block from `OrdersApiP99LatencyHigh` above.
4. Common cause A — recent deploy: check
   `kubectl -n orders rollout history deploy/orders-api`. If a deploy
   happened in the last 60 min, **roll back** (see Rollback section)
   and verify.
5. Common cause B — Postgres slow query: kill the offending query
   (`SELECT pg_cancel_backend(<pid>);`); scale read replicas.
6. Common cause C — Redis eviction storm: check `redis-cli info
   memory`; if `evicted_keys` is climbing, bump replica count.
7. Once p99 < 400 ms for 10 min: post `Mitigated` in Slack, resolve
   the page, schedule a postmortem (within 5 business days for Tier 1).

### 2. Stuck in `pending` status

Orders sit in `pending` > 5 min. Cause: Kafka consumer lag in
`billing-worker`. Run the `OrdersKafkaLagHigh` playbook.

### 3. Idempotency-key collisions spiking

> 0.1% of `POST /v1/orders` returning 409. Cause: client retry storm.
Look up the noisy `customer_id`; consider a temporary
`/v1/orders` block on that customer if abusive.

### 4. Postgres connections exhausted

`FATAL: too many connections`. Restart the leaking pod
(`kubectl -n orders rollout restart deploy/orders-api`); inspect
`pg_stat_activity` to find the leak.

### 5. CDN cache poisoning

Stale 5xx cached at the edge. Purge per
`CDN runbook (link)` and add `Cache-Control: no-store` to error responses.

## Rollback

```bash
# Find last known good revision
kubectl -n orders rollout history deploy/orders-api

# Roll back one revision
kubectl -n orders rollout undo deploy/orders-api

# Or pin a specific image tag
kubectl -n orders set image deploy/orders-api \
  api=ghcr.io/example/orders-api:<known-good-sha>

# Watch rollout
kubectl -n orders rollout status deploy/orders-api
```

DB migrations: roll-forward only. If a migration is bad, ship a
compensating migration; never `down()` in prod.

## Escalation matrix

| Trigger | Who | How |
|---|---|---|
| Alert unacked > 10 min | Secondary on-call | Auto-page via PagerDuty |
| Tier-1 outage > 30 min | Engineering manager | PagerDuty + phone |
| Data loss suspected | DB on-call + Security | PagerDuty `db-oncall`, Slack `#sec-incidents` |
| Customer escalation | Support manager | Slack `#support-leads` |
| Public communication needed | Comms on-call | PagerDuty `comms-oncall` |

## On-call cheatsheet

**Most-used commands:**

```bash
kubectl -n orders get pods -l app=orders-api -w
kubectl -n orders logs -l app=orders-api --tail=200 -f
kubectl -n orders rollout undo deploy/orders-api
psql $PG_URL -c "select * from pg_stat_activity where state != 'idle';"
redis-cli -h $REDIS_HOST info memory
kafka-consumer-groups --bootstrap-server $KAFKA --describe --group billing-worker
```

**Most-checked dashboards:**

- Orders SLO: `grafana.example.com/d/orders-slo`
- Postgres: `grafana.example.com/d/pg-orders`
- Kafka: `grafana.example.com/d/kafka-orders`

**Common Loki queries:**

```logql
{app="orders-api"} |= "level=error" | json | line_format "{{.msg}}"
{app="orders-api"} |~ "request_id=abc123"
sum by (status) (rate({app="orders-api"} | json [5m]))
```
