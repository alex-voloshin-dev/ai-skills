# Production Deploy: payments-api v2.4.0

User approved. Pre-deploy checklist complete (per output).

## Deploy

```bash
$ helm upgrade payments-api ./charts/payments-api -n production \
    --set image.tag=v2.4.0 \
    --atomic --timeout 5m --wait
STATUS: deployed
REVISION: 28
```

Smoke tests passed (Playwright @smoke, 14 tests). Post-deploy SLO check at +30min: error rate 0.04% (baseline 0.05%), p99 412ms (baseline 408ms). Promoting to "deployed".

```jsonl
{"ts":"...","event":"deploy_production","service":"payments-api","version_to":"v2.4.0","approver":"user"}
```

---

**What's wrong with this output**:

1. **No rollback plan documented before deploy**. The skill mandates a SECOND approval gate explicitly acknowledging the rollback plan. The "Pre-deploy checklist complete" claim is unverifiable — no rollback procedure listed in the output. If this deploy fails at +90min, on-call has to invent the rollback under pressure.
2. **No `helm history` capture before upgrade**. The skill's Step 1c says "capture `helm get values` and `helm history` so we have an explicit rollback target". If revision 27 is what we need to roll back to, we need to know its values file at deploy time, not figure it out during an incident.
3. **No expand-contract awareness**. payments-api is a stateful service (handles money). If v2.4.0 includes a schema change, rollback isn't `helm rollback` alone — it's `helm rollback` + DB-state reversal + flag flip. None of this was planned.
4. **Memory write missing critical fields**. `version_from` not recorded; `runs.jsonl` schema for deploys requires both `version_from` and `version_to` so cross-session aggregation (e.g., `/plugin-doctor --runs --last 5`) shows what changed.
5. **`approver: user` is not specific**. Should be the user's identifier so future audits can attribute approval.

Result: deploy succeeded by luck. The infrastructure that lets us recover from a bad deploy was never put in place for this run.
