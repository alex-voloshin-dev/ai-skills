# Deploy-Production Rubric

## Overview

Evaluates `/deploy-production` output — production rollout. Six dimensions × five levels. Frame: GitOps controller ownership over imperative apply; explicit human approval gates; verifiable rollback before promote.

## Dimensions

### Dimension 1: Approval Gates
Explicit user APPROVE before deploy AND a separate APPROVE for the rollback plan.

- **Level 1:** Deploys with no approval gate
- **Level 2:** One blanket "ok?" covering deploy + rollback
- **Level 3:** APPROVE on deploy; rollback plan implied not approved
- **Level 4:** APPROVE on deploy + APPROVE on rollback plan + APPROVE on canary promote
- **Level 5:** All of L4 + named approver recorded; checkpoint logged to memory for audit

### Dimension 2: Controller Detection (Step 0a)
Argo CD / Flux / Argo Rollouts / Flagger detected; imperative apply skipped when a controller owns the namespace.

- **Level 1:** `helm upgrade` / `kubectl apply` run directly while Argo CD owns the namespace
- **Level 2:** Notices controller but pushes a one-off apply "just for speed"
- **Level 3:** Routes through the controller (git PR for Argo CD / Flux; Rollout `promote` for Argo Rollouts)
- **Level 4:** Controller routed + verifies sync status + uses controller-native promotion (AnalysisTemplate, Flagger metric webhook)
- **Level 5:** All of L4 + writes a controller-level audit entry (Application annotation / Rollout note)

### Dimension 3: Feature-Flag Awareness (Step 0b)
LaunchDarkly / Unleash / OpenFeature / Flagsmith / Split detected; deploy decoupled from release where possible.

- **Level 1:** Couples deploy + release; flag platform ignored despite `launchdarkly-server-sdk` in lockfile
- **Level 2:** Notices flag platform, ships behind a flag, but enables flag in same window
- **Level 3:** Dark-deploy proposed; flag flip is a separate step
- **Level 4:** Dark-deploy + targeted flag rollout (% / segment) + kill-switch contract documented
- **Level 5:** All of L4 + feature-flag SDK metric (e.g., evaluation rate) included in monitor window

### Dimension 4: Risk Assessment
Risk matrix populated with concrete, change-specific factors — not generic.

- **Level 1:** "Low risk" with no rationale
- **Level 2:** Generic categories (perf / security / data) without ties to the change
- **Level 3:** Risk factors named per change (DB migration / cache key change / external API)
- **Level 4:** Likelihood × impact rated per factor; mitigations linked
- **Level 5:** All of L4 + blast-radius estimate (% traffic, $ cost, customer count) cited

### Dimension 5: Smoke + Monitor
Discovers project's smoke suite; chooses SLO-based or static-window monitoring per controller availability.

- **Level 1:** No smoke; "looked at logs for a minute"
- **Level 2:** Generic curl on `/health`
- **Level 3:** Discovers `e2e/` / `tests/smoke/` / Playwright `@smoke` and runs it
- **Level 4:** Smoke suite + SLO-based monitor when Argo Rollouts/Flagger present (AnalysisTemplate / metric webhook); static window with named metrics otherwise
- **Level 5:** All of L4 + abort criteria expressed as PromQL / Datadog query / equivalent

### Dimension 6: Rollback Plan Executable
Rollback commands ready, not narrative.

- **Level 1:** "We can roll back if needed"
- **Level 2:** General mention of `helm rollback`
- **Level 3:** Specific rollback command for the chosen controller (`helm rollback <rel> <prev-rev>` / `argocd app rollback` / `flux suspend`)
- **Level 4:** Rollback command + verification step + estimated MTTR
- **Level 5:** All of L4 + data-rollback path documented (or expand-contract migration noted so rollback is forward-compatible)

## Scoring Logic

- **Aggregate:** average of D1–D6
- **Pass threshold:** 3.8
- **Judge model:** Sonnet (production deploy = high cost of error)

## Anti-Patterns (Auto-Fail)

- Deploys without explicit user APPROVE
- Imperative `helm upgrade` / `kubectl apply` when Argo CD / Flux owns the namespace
- Static "monitor 5 minutes" when SLO-based promotion was available
- No rollback command documented
- Smoke skipped after deploy

## Calibration Reference

- **Known-good:** `plugin/eval/calibration/deploy-production/good/*`
- **Known-bad:** `plugin/eval/calibration/deploy-production/bad/*`
