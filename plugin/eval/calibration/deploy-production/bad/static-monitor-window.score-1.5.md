# Production Deploy: api-gateway v5.1.0

## Pre-deploy

User approved. Tag verified. /deploy-staging green.

## Deploy

```bash
$ kubectl argo rollouts get rollout api-gateway -n production
NAME          STATUS    STRATEGY
api-gateway   Healthy   Canary
```

(Argo Rollouts CRD detected but ignored.)

```bash
$ helm upgrade api-gateway ./charts/api-gateway -n production \
    --set image.tag=v5.1.0 \
    --atomic --timeout 5m --wait
Release "api-gateway" has been upgraded.
```

## Verify

> Monitor for 5–10 minutes per the skill's standard window.

Watched the dashboard for 8 minutes. Error rate stable. Latency within SLO. Calling it done.

```jsonl
{"ts":"...","event":"deploy_production","service":"api-gateway","version":"v5.1.0","monitor_duration_minutes":8}
```

---

**What's wrong with this output**:

1. **Argo Rollouts CRD was detected and then ignored**. `kubectl argo rollouts get` was run but its output was discarded — the deploy bypassed the controller's canary + AnalysisRun and went imperative `helm upgrade`. Two consequences:
   - The Rollout CR's `Spec.SetWeight` plan was overridden — service had a brief mixed-version state until the controller reconciled back.
   - The AnalysisTemplate (presumably configured for this Rollout — typical pattern is `success-rate ≥ 99.5%` over 5min Prometheus window) was bypassed. We had automated SLO-based gating available and didn't use it.
2. **Static 5–10 minute monitoring window** is exactly the runbook smell the skill (Step 0a) tells you to replace with analyzer-based promotion when a controller is present. Static windows give the false impression of validation; the controller's SLO analyzer is data-driven.
3. **No analyzer post-mortem**. Even though the static monitor passed, the controller's AnalysisRun for this rollout has no entry — incident retrospectives lose the ability to query "which deploys were promoted by analyser vs static?".
