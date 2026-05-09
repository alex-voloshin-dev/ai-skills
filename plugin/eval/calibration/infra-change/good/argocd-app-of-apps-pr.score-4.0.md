# Infra change: bump nginx-ingress chart 4.10 → 4.11 via Argo CD PR

## Detection (Step 0a)

```bash
$ ls argocd/ apps/
argocd/applications.yaml
$ grep -l "Application" argocd/*.yaml | head -3
argocd/applications.yaml
```

Argo CD `Application` CRDs in repo → change is git PR, not local `helm upgrade`.

## Workflow

```bash
$ git checkout -b chore/bump-nginx-ingress-4.11
# Edit argocd/applications.yaml: targetRevision: 4.11.0
$ git diff
- targetRevision: 4.10.2
+ targetRevision: 4.11.0

$ git commit -am "chore(infra): bump nginx-ingress 4.10.2 → 4.11.0"
$ gh pr create --title "..." --body "..."
```

After PR review + merge, Argo CD reconciles automatically:

```bash
$ argocd app get nginx-ingress -n argocd
Status:    Healthy / Synced
Revision:  argocd/applications.yaml @ <merge-sha>
```

No imperative `helm upgrade` was run. The controller owns the apply.

## Score rationale

Detection (5), routed via PR (5), no imperative apply (4), reconcile verified (3). Avg 4.0.
