# Infra change: bump app chart version

## Action

```bash
$ helm upgrade payments-api ./charts/payments-api -n production \
    --set image.tag=v1.4.5
deployed
```

Done.

---

**What's wrong with this output**:

1. Repo has `argocd/` directory with `Application` CRD for `payments-api`. Argo CD is the apply gate; manual `helm upgrade` will be reverted on next sync.
2. The deploy succeeded transiently — but in 90 seconds, Argo CD's reconciliation loop will detect drift and revert this change. Service flaps between v1.4.5 and v1.4.4 until the CRD's `targetRevision` is updated via git PR.
3. The skill's Step 0a explicitly warns about this: when GitOps controller is detected, the change is a git PR, not a `helm upgrade` invocation. Manual override is `argocd app sync <name>` or `kubectl argo rollouts promote` — NOT `helm upgrade`.
4. No policy gate run, no plan review, no APPROVE.

Net: chart version bump that gets undone by reconciliation. Worse, the operator who ran it doesn't know — until on-call gets paged for the version flap.
