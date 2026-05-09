# Staging deploy: per-PR ephemeral namespace via Argo CD ApplicationSet

## Detection (Step 0)

```bash
$ kubectl get applicationsets -n argocd
NAME                AGE
preview-envs        90d

$ kubectl get applicationset preview-envs -n argocd -o yaml | yq '.spec.generators[0]'
pullRequest:
  github:
    owner: acme
    repo: orders-api
    tokenRef:
      secretName: gh-token
      key: token
```

ApplicationSet with `pullRequest` generator → per-PR staging environments are created automatically. Manual `helm upgrade` would conflict with the controller.

## Trigger via PR

```bash
$ gh pr create --title "feat: streaming order export" --body "..."
$ gh pr view --json number
{"number": 4218}
```

Argo CD reconciles; namespace `pr-4218` appears within ~90s:

```bash
$ kubectl get ns pr-4218
NAME       STATUS   AGE
pr-4218    Active   1m

$ kubectl get application -n argocd | grep pr-4218
pr-4218-orders-api   pr-4218   Synced  Healthy
```

## Smoke against PR namespace

Service URL: `http://orders-api.pr-4218.svc.cluster.local:8080` (or via per-PR Ingress, e.g. `pr-4218.staging.acme.dev`).

```bash
$ npx playwright test --grep @smoke --base-url=https://pr-4218.staging.acme.dev
22 passed (6.8s)
```

## Cleanup (automatic)

When PR closes/merges, Argo CD ApplicationSet removes the namespace. Zero manual cleanup.

## Score rationale

Detected ApplicationSet correctly (5), routed via PR open (4), per-PR isolation correct (5), automatic cleanup (4), discoverable smoke (4). Avg 4.2.
