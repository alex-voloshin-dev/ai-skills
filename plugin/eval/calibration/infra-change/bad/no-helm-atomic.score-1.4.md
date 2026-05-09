# Infra change: bump payments-api chart version

```bash
$ helm upgrade payments-api ./charts/payments-api -n production \
    --set image.tag=v2.7.1 \
    -f values.production.yaml
Release "payments-api" has been upgraded.
STATUS: deployed
```

Half the pods crashed during rollout (`CrashLoopBackOff` due to missing env var in v2.7.1). The other half kept serving v2.7.0. Service is now in mixed state.

```bash
$ kubectl get pods -n production -l app=payments-api
NAME                            READY   STATUS             RESTARTS   AGE
payments-api-7d8b9c4-abcde      0/1     CrashLoopBackOff   3          2m
payments-api-7d8b9c4-fghij      0/1     CrashLoopBackOff   3          2m
payments-api-old-xyz            1/1     Running            0          7d
payments-api-old-uvw            1/1     Running            0          7d
```

Helm reports "deployed" because the upgrade *command* completed — but the cluster never reached Ready. Recovery requires manual `helm rollback`.

---

**What's wrong with this output**:

1. **No `--atomic`**. With `--atomic`, helm would have rolled back automatically when the new pods failed readiness, leaving the cluster on v2.7.0 cleanly. Without it, helm hands back "deployed" and disappears, leaving an operator to figure out the half-broken state.
2. **No `--timeout`**. The default is 5min, which is fine, but explicit `--timeout 5m` makes the intent legible to the next reader.
3. **No `--wait`**. Without `--wait`, helm returns as soon as the API server accepts the manifest — not when pods are actually running. So "deployed" reports premature success.
4. **No `helm-diff` preview before upgrade**. `helm diff upgrade` would have shown the new env var was required by the chart but missing from `values.production.yaml`, and the operator could have caught it pre-flight.

The skill explicitly tells you `--atomic --timeout --wait` for prod. This is exactly the failure mode that flag combination prevents.
