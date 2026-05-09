# Deploy-Staging Rubric

## Overview

Evaluates `/deploy-staging` output — staging / preview / pre-prod deploy. Six dimensions × five levels. Frame: lower bar than production but still verifiable; respect tests-already-ran contract; surface next-step (promote? hold?).

## Dimensions

### Dimension 1: Controller / Preview-Env Detection
Detects Argo CD ApplicationSet pullRequest / Loft vCluster / Tilt / Skaffold and uses it.

- **Level 1:** Imperative apply on a cluster managed by ApplicationSet pullRequest
- **Level 2:** Notices a preview-env tool but spins a separate path
- **Level 3:** Detects the tool and uses it (PR-namespace via ApplicationSet, vCluster, `tilt up`, `skaffold dev`)
- **Level 4:** Tool routed + per-PR namespace / preview URL captured + TTL respected
- **Level 5:** All of L4 + cleanup plan documented (auto-delete on PR close)

### Dimension 2: Build Correctness
Right build command per stack; respects test-already-ran contract.

- **Level 1:** `mvn package -DskipTests` / `npm run build --skip-test` without checking whether tests already ran
- **Level 2:** Re-runs tests inside build despite upstream `/develop` having run them
- **Level 3:** Build command matches stack; tests skipped because contract says they already ran
- **Level 4:** Stack-correct build + reproducible (lockfile honoured, no floating tags)
- **Level 5:** All of L4 + build artefact attested (Cosign / SBOM produced) when ecosystem supports

### Dimension 3: Method Selection
Helm vs kubectl vs Docker Compose vs serverless deploy chosen correctly per project.

- **Level 1:** kubectl apply on a Helm-managed release (orphans the release)
- **Level 2:** `docker compose up` on a Kubernetes-only project
- **Level 3:** Method matches the project's deploy convention
- **Level 4:** Method + values-file selection per env (staging vs prod) + namespace correct
- **Level 5:** All of L4 + secrets sourced via the project's secret-mount (External Secrets / Vault Agent / Sealed Secrets)

### Dimension 4: Smoke Tests
Discovers and runs a smoke suite.

- **Level 1:** Deploy without verification
- **Level 2:** Generic curl on root URL
- **Level 3:** Discovers `e2e/` / `tests/smoke/` / Playwright `@smoke` and runs it
- **Level 4:** Smoke suite + per-test pass/fail surfaced + service URL printed
- **Level 5:** All of L4 + perf smoke when project has one (`k6`, `artillery`, `wrk` script)

### Dimension 5: Supply-Chain Validation
Cosign / SBOM / SLSA verified on staging artefact when project ships them.

- **Level 1:** Pulls and deploys image without signature check though `.cosign.pub` is in repo
- **Level 2:** Mentions signature but does not verify
- **Level 3:** `cosign verify --key ...` run; failure blocks deploy
- **Level 4:** Cosign verify + SBOM diff against last release + SLSA provenance check
- **Level 5:** All of L4 + artefact pinned by digest, not tag, in the staging manifest

### Dimension 6: Output Structure
Clear status + service URL + post-deploy verification + next-step.

- **Level 1:** Wall of `kubectl` output without summary
- **Level 2:** Status line but no URL or next-step
- **Level 3:** Status + service URL + verification done
- **Level 4:** Status + URL + verification + recommended next step (`/deploy-production` ready, or hold, or rollback)
- **Level 5:** All of L4 + diff vs. previous staging release; per-service health + observability links

## Scoring Logic

- **Aggregate:** average of D1–D6
- **Pass threshold:** 3.5
- **Judge model:** Sonnet

## Anti-Patterns (Auto-Fail)

- `mvn package -DskipTests` (or equivalent) without confirming upstream tests ran
- Deployed with no verification step
- kubectl apply on a Helm-managed release
- Wrong runtime mode chosen (Next.js as static when Edge runtime needed)
- Output is a kubectl log dump with no summary

## Calibration Reference

- **Known-good:** `plugin/eval/calibration/deploy-staging/good/*`
- **Known-bad:** `plugin/eval/calibration/deploy-staging/bad/*`
