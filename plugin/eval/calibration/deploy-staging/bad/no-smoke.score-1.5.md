# Staging deploy: search-api v0.4.2

## Build

```bash
$ docker build -t ghcr.io/acme/search-api:v0.4.2 .
$ docker push ghcr.io/acme/search-api:v0.4.2
```

## Deploy

```bash
$ kubectl set image deployment/search-api search-api=ghcr.io/acme/search-api:v0.4.2 -n staging
deployment.apps/search-api image updated
```

## Verify

Image rolled out.

---

**What's wrong with this output**:

1. **Zero verification beyond rolled-out status**. The skill's Step 4 requires running smoke tests — list them, run them, report pass/fail. None of that happened.
2. **`kubectl set image` instead of helm upgrade**. The repo has `charts/search-api/`. Using `kubectl set image` directly bypasses the chart's values file, which means the deployed pods have stale env vars / resource limits / probes from whatever was last `helm upgrade`d. Mixing imperative `kubectl` with declarative `helm` causes silent drift between Git and cluster.
3. **No log inspection** (Step 4a). `kubectl logs --since=5m` would show the new pods' first error if any.
4. **No project-specific smoke suite check**. The skill explicitly enumerates `tests/smoke/`, `e2e/` with `@smoke`-tagged Playwright, Cypress smoke specs, Postman/Newman, K6/Artillery as places to look. None checked.
5. **Result**: a deployed image that may or may not work. No early signal whether to promote to /deploy-production or hold.
