# Production Deploy

```bash
$ helm upgrade billing-api ./charts/billing-api -n production \
    --set image.tag=v1.7.4
Release "billing-api" has been upgraded. Happy Helming!
```

Deploy applied. Smoke test passed. Done.

---

**What's wrong with this output**:

1. **No APPROVE gate**. The skill mandates explicit user APPROVE before any production mutation, plus a SECOND APPROVE acknowledging the rollback plan. Both skipped.
2. **No `--atomic --timeout --wait`**. Helm command is naked — if any pod fails its readiness probe, the upgrade leaves the release in a half-deployed state. `--atomic` would auto-rollback.
3. **No risk assessment** (Step 1 of skill). Risk matrix not produced. Severity unknown.
4. **No rollback plan documented**. If this deploy goes wrong, on-call has no pre-built command to roll back.
5. **No staging verification mentioned**. Was /deploy-staging green for this version? No record.
6. **No memory write**. `.ai-skills-memory/runs.jsonl` not updated; this deploy is invisible to subsequent /plugin-doctor runs and /analyze-prod incident retrospectives.
7. **No on-call paging**. PagerDuty not silenced; if a flap fires during deploy, the on-call gets paged for noise.
8. **No smoke-suite discovery**. The skill says "Run the project's existing smoke suite (tests/smoke/, e2e/ with @smoke)". The output claims "Smoke test passed" but doesn't show what was run.

Net effect: production deploy completed, but the entire safety net the skill exists to provide was bypassed.
