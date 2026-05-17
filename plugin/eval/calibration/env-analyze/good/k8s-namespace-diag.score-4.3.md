# Environment Diagnostic — Kubernetes prod namespace

> Scope: k8s-namespace:prod | Auto-fix: disabled

## Summary

18 pods across 3 deployments. 1 pod pending (waiting for node), 1 pod in CrashLoopBackOff. Root cause: memory limits misconfigured + missing init container dependency. 2 anomalies fixable.

## Pod Status

| Pod | Deployment | State | Restarts | CPU | Memory | Age |
|---|---|---|---|---|---|---|
| api-prod-abc123 | api | Running | 0 | 45m | 256Mi | 4h |
| api-prod-def456 | api | Running | 0 | 52m | 312Mi | 4h |
| worker-prod-ghi789 | worker | Running | 5 | 120m | 1.2Gi | 4h |
| worker-prod-jkl012 | worker | CrashLoopBackOff | 12 | — | — | 4h |
| postgres-prod-mno345 | postgres | Running | 0 | 80m | 2.1Gi | 4h |
| cache-prod-pqr678 | cache | Pending | 0 | — | — | 2h |

## Logs (error-filtered)

### worker-prod-jkl012 (CrashLoopBackOff)
```
ERROR: Liveness probe failed: unable to connect to init service on localhost:5000
Error: connect ECONNREFUSED 127.0.0.1:5000
[crash]
[restart]
[repeat]
```

### cache-prod-pqr678 (Pending)
```
Events: 0/3 nodes available: 3 Insufficient memory. Pod requires 1Gi, no node has >= 800Mi available.
```

## Resource Saturation

- Node 1: CPU 78%, Memory 91% (saturated)
- Node 2: CPU 45%, Memory 67%
- Node 3: CPU 52%, Memory 73%

## Network Sanity

- DNS: `nslookup postgres.prod` resolves to 10.0.2.45 (correct)
- Pod-to-pod: api → postgres: 2.3ms latency
- Pod-to-external: api → upstream API: 45ms (acceptable)

## Identified Anomalies

| Anomaly | Severity | Evidence | Class |
|---|---|---|---|
| `worker-prod-jkl012` CrashLoopBackOff | HIGH | 12 restarts in 4h, logs show init service unreachable | Dependency/Config |
| `cache-prod-pqr678` Pending | HIGH | Insufficient memory on all nodes; requests 1Gi | Capacity |
| `worker-prod-ghi789` high restart count | MEDIUM | 5 restarts in 4h, no recent errors in logs | Flakiness |

## Root Causes

1. **worker-prod-jkl012:** Init container (provides config service on :5000) not defined in deployment. Worker pod starts before init completes, probes fail, pod restarts. Repeats forever.

2. **cache-prod-pqr678:** Pod requests 1Gi memory. Nodes have < 800Mi available. Pod stuck pending. Node 1 is 91% saturated; Node 2/3 have only ~700Mi free each.

3. **worker-prod-ghi789:** 5 restarts, but logs clean. Likely a liveness probe timing out under load (hard to diagnose without metrics); intermittent.

## Recommended Actions (manual)

1. **Fix worker-prod-jkl012 init dependency:**
   ```bash
   kubectl set env deployment/worker -c worker INIT_SERVICE_REQUIRED=true
   kubectl rollout restart deployment/worker
   kubectl wait --for=condition=progressing=True deployment/worker --timeout=5m
   ```
   Reversibility: high — prior version still available.

2. **Fix cache memory requests:**
   ```bash
   kubectl patch deployment cache -p '{"spec":{"template":{"spec":{"containers":[{"name":"cache","resources":{"requests":{"memory":"512Mi"}}}]}}'
   kubectl rollout restart deployment/cache
   ```
   Reversibility: medium — requires manual re-patch if 512Mi insufficient.

3. **Monitor worker-prod-ghi789 flakiness:**
   - Enable verbose logging: `kubectl set env deployment/worker LOG_LEVEL=debug`
   - Collect metrics: `kubectl top pods -l deployment=worker --containers`
   - Revisit in 1h; if restarts continue, escalate to deeper investigation

## Out-of-Scope

- Node capacity: adding more nodes requires cloud infra changes (out of pod scope)
- Upstream API latency (45ms): would require network investigation outside this namespace

## Memory Write

Baseline saved to `.ai-skills-memory/env-reports/k8s-prod-<run-id>/`.
