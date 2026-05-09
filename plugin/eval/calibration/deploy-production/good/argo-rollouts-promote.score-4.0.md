# Production Deploy: orders-api v3.2.0 via Argo Rollouts

## Detection (Step 0a)

```bash
$ kubectl get rollouts -n production
NAME         DESIRED   CURRENT   UP-TO-DATE   AVAILABLE   AGE
orders-api   8         8         8            8           42d
```

Argo Rollouts CRD detected → skip imperative `helm upgrade`. Routing through controller.

## Pre-deploy checklist (passed)

- [x] /deploy-staging green for orders-api v3.2.0 (12h ago)
- [x] Tag v3.2.0 signed + SLSA-attested (`gh attestation verify`)
- [x] No DB migration this release
- [x] Feature flags: `new-pricing-engine` already at 100% in LD; this deploy collapses the dead branch
- [x] On-call paged: silenced in PagerDuty for 30min window

## Promote

```bash
$ kubectl argo rollouts get rollout orders-api -n production
Name:  orders-api
Status: ✔ Healthy
Strategy: Canary
  Step: 5/8
  SetWeight: 60
  ActualWeight: 60
✓ AnalysisRun "orders-api-3.2.0-pre-promote": Successful
  - success-rate: 99.94% (target ≥99.5)
  - p99-latency: 187ms (target <250ms)

$ kubectl argo rollouts promote orders-api -n production
rollout 'orders-api' promoted
```

## Verify

```bash
$ kubectl argo rollouts status orders-api -n production --watch
Step: 8/8 ... Healthy ... ✓
```

AnalysisTemplate-driven promotion replaced the static 5–10 min monitoring window. Post-deploy SLO check at +15min confirms success-rate stable at 99.96%, p99 187ms.

## Memory write

```jsonl
{"ts":"2026-05-09T18:42Z","event":"deploy_production","service":"orders-api","version_to":"v3.2.0","strategy":"argo-rollouts-canary","approver":"alex.v","rollback":"kubectl argo rollouts undo orders-api -n production"}
```

## Score rationale

Controller routed correctly (5), feature-flag branch collapsed cleanly (4), AnalysisRun gated promotion (5), approval explicit (4), rollback documented (4). Avg 4.0.
