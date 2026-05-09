# Production Diagnostic — `notifications-worker` CrashLoopBackOff

> Severity: P3 | Read-only diagnosis | Cluster: prod-us-east-1
> Methodology: Four Golden Signals + USE on the affected workload — Google SRE Workbook + Brendan Gregg
> Observability stack: Prometheus + Grafana, GKE Cloud Logging, Sentry

## Summary

`notifications-worker` deployment in `notifications` namespace: 4 of 6 pods in `CrashLoopBackOff` since 2026-04-25 12:40 UTC. Root cause: missing GCP Secret Manager binding for `SENDGRID_API_KEY` after this morning's IAM rotation. Pods exit with code 1 within 8s of start; restart count climbs. SLO impact: notification send-rate dropped 38%; error budget 12% consumed (still healthy).

## Golden Signals — `notifications-worker`

| Signal | Value | Baseline | Verdict |
|---|---|---|---|
| Latency (msg send p99) | N/A — pods crash before processing | 220ms | **N/A — workload not running** |
| Traffic (queue depth) | 12,400 msgs backlog | < 50 msgs | **CRITICAL** |
| Errors (pod exit code 1) | 47/min | 0/min | **CRITICAL** |
| Saturation (worker capacity) | 33% (2/6 pods running) | 100% | **DEGRADED** |

Source: Grafana dashboard `notifications/SLI-overview` ([link](https://grafana.example.com/d/notif-sli)). Prometheus saved query for the panel: `kube_pod_container_status_restarts_total{namespace="notifications",pod=~"notifications-worker-.*"}`.

## Pod Evidence (read-only)

```
$ kubectl --context=prod-us-east-1 -n notifications get pods -l app=notifications-worker
NAME                                  READY   STATUS             RESTARTS      AGE
notifications-worker-7f9-4kp8m        0/1     CrashLoopBackOff   38 (12s ago)  102m
notifications-worker-7f9-9nq2p        0/1     CrashLoopBackOff   38 (8s ago)   102m
notifications-worker-7f9-bd4xk        0/1     CrashLoopBackOff   38 (44s ago)  102m
notifications-worker-7f9-l2vq8        0/1     CrashLoopBackOff   37 (1m ago)   102m
notifications-worker-7f9-w8h4n        1/1     Running            0             102m
notifications-worker-7f9-x3nrt        1/1     Running            0             102m
```

`describe` excerpt for one of the failing pods:
```
Last State:     Terminated
  Reason:       Error
  Exit Code:    1
  Started:      Sat, 25 Apr 2026 14:12:18 +0000
  Finished:     Sat, 25 Apr 2026 14:12:26 +0000
```

The 2 pods that ARE running started before 12:40 UTC (the IAM rotation timestamp).

## Logs Evidence

Cloud Logging filter: `resource.type="k8s_container" resource.labels.namespace_name="notifications" severity>=ERROR`

```
2026-04-25T14:12:25.443Z [worker.boot] error="failed to fetch secret: rpc error:
code = PermissionDenied desc = Permission 'secretmanager.versions.access' denied
on resource 'projects/prod-shared/secrets/sendgrid-api-key/versions/latest'"
```

47 occurrences/min, all from pods started after 12:40 UTC. The 2 running pods loaded the secret before rotation and have it cached for the lifetime of the process.

## USE Method on the Workload

| Axis | Value | Verdict |
|---|---|---|
| Utilization (worker pod count) | 2/6 effective | **CRITICAL** |
| Saturation (queue depth) | 12,400 msgs (rising 200/min) | **CRITICAL** |
| Errors (pod exits) | 38 restarts × 4 pods | **CRITICAL** |

## SLO Status

`notifications.send-success-rate` SLO:
- Target: 99.0% / 30 days
- Current 30d: 98.94% (still inside budget)
- Error budget remaining: 88% (12% consumed in 102m)
- 1h burn rate: 6× steady-state
- Projected exhaustion if pattern continues: ~14h — actionable, not panic

## Severity + Blast Radius

- **P3** — degraded, not down. Backlog absorbs short-term spikes; not customer-visible until backlog > 30min processing time.
- Affected scope: notification delivery latency rising; estimated 1,800 users/hour with > 5min delay
- Cascading risk: if backlog crosses 50k msgs, downstream `digest-builder` will fall behind too

## Root Cause Hypothesis (HIGH confidence)

This morning's GCP IAM rotation (changelog: `iam/rotations/2026-04-25-am`) revoked the old service-account binding to the `sendgrid-api-key` secret without granting the new binding. New pods started after rotation cannot read the secret; cached pods are unaffected.

## Proposed Mitigations (gated on user APPROVE — read-only diagnosis)

These mutate production. **DO NOT EXECUTE without explicit user APPROVE.**

1. **Re-grant secret access to the service account** (root-cause fix):
   ```
   gcloud secrets add-iam-policy-binding sendgrid-api-key \
     --member=serviceAccount:notifications-prod@... \
     --role=roles/secretmanager.secretAccessor
   ```
   Blast: minimal — IAM-only; reversible via removing the binding.
2. **Rolling restart** of the deployment to pick up the new permission:
   ```
   kubectl --context=prod-us-east-1 -n notifications rollout restart deploy/notifications-worker
   ```
   Blast: ~3min during which the 2 healthy pods drain; reversible via `rollout undo`.

Recommend executing 1 then 2. Awaiting APPROVE.

## What Was Checked (transparency)

- Prometheus: pod restart counters, queue depth time series
- Cloud Logging: error-severity logs for the namespace
- Sentry: 0 new fingerprints (auth error happens before Sentry init)
- IAM audit log: confirmed the rotation timestamp matches incident start within 30s

## Out of Scope

- Long-term fix to make secret rotation atomic (binding-rotate operator). That's an `/architecture` initiative.
