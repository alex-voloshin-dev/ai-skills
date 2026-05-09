# Staging deploy: notifications-api

## Build

```bash
$ mvn package -DskipTests
[INFO] BUILD SUCCESS
```

## Deploy

```bash
$ helm upgrade notifications-api ./charts/notifications-api -n staging \
    --set image.tag=$(git rev-parse --short HEAD)
deployed
```

## Verify

Pod up. Calling it done.

---

**What's wrong with this output**:

1. **`-DskipTests` without confirming tests already ran**. The skill explicitly says: tests should already have passed in `/run-tests` before /deploy-staging. The contract is that staging-build skips tests because they ran moments ago in CI/pre-commit, not because the team skips testing entirely. No record here that tests ran. If tests are broken, staging just got a broken artefact.
2. **Image tag is a short SHA, not a semver tag.** `git rev-parse --short HEAD` produces 7 chars; `helm rollback` becomes ambiguous if the repo has stale or rebuilt SHAs. Convention: use the artefact's actual versioned tag (matches what /release will tag, which matches what /deploy-production will deploy).
3. **No supply-chain validation**. Image not Cosign-verified, SLSA attestation not verified — even if the project ships them.
4. **No discoverable smoke**. "Pod up. Done." — no `tests/smoke/`, no Playwright @smoke, no project-specific suite. Pod-up is a liveness probe, not a smoke test.
5. **No `--atomic --timeout --wait`**. If a pod's readiness probe fails, helm returns success while the cluster sits in mixed state.
