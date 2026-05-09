# Infra-Change Rubric

## Overview

Evaluates `/infra-change` output — Terraform / OpenTofu / Helm / Pulumi / Kubernetes infrastructure change. Six dimensions × five levels. Frame: GitOps wins over imperative; policy gates run pre-plan; destructive operations require explicit human approval.

## Dimensions

### Dimension 1: GitOps Controller Detection (Step 0a)
Argo CD / Flux / Atlantis / HCP Terraform / Spacelift / env0 detected; routes change as a git PR not an imperative apply.

- **Level 1:** `terraform apply` / `helm upgrade` run locally while Argo CD or HCP Terraform owns the resource
- **Level 2:** Notices controller but bypasses ("faster this way")
- **Level 3:** Routes through controller (PR for Atlantis / Argo CD / Flux; run trigger for HCP Terraform / Spacelift / env0)
- **Level 4:** Controller routed + plan output linked from PR + sync window respected
- **Level 5:** All of L4 + drift-detection check before submit (no surprise diffs)

### Dimension 2: OpenTofu Detection (Step 0b)
Substitutes `tofu` for `terraform` when `.terraform-version` or `tofu.lock.hcl` indicates OpenTofu.

- **Level 1:** Runs `terraform` on an OpenTofu repo (potential lockfile drift, license confusion)
- **Level 2:** Notices OpenTofu but uses `terraform` anyway
- **Level 3:** Detects `tofu.lock.hcl` / asdf `opentofu` and uses `tofu`
- **Level 4:** Tofu used + version pinned via `.tool-versions` / `.terraform-version`
- **Level 5:** All of L4 + provider checksums verified against `tofu.lock.hcl`

### Dimension 3: Policy Gate (Step 0c)
Runs Conftest / tfsec / Checkov / OPA as a pre-plan gate when configured.

- **Level 1:** Policy config exists in repo but not run
- **Level 2:** Runs policy after apply (too late)
- **Level 3:** Runs Conftest/tfsec/Checkov pre-plan; failures block
- **Level 4:** Policy run + violations surfaced with rule IDs + waiver process noted
- **Level 5:** All of L4 + per-environment policy (stricter prod) + cost estimate via Infracost when configured

### Dimension 4: Plan Review
Concrete plan summary table per resource (created / changed / destroyed) with risk rating.

- **Level 1:** Pastes raw `terraform plan` output without summary
- **Level 2:** Counts only ("3 to add, 1 to change")
- **Level 3:** Per-resource table with action verb
- **Level 4:** Per-resource table + risk rating + replacement-vs-update flagged
- **Level 5:** All of L4 + downstream impact analysis (which services depend on each replaced resource)

### Dimension 5: Helm Safety
Production Helm upgrades use `--atomic --timeout --wait`.

- **Level 1:** `helm upgrade` without any safety flags on production
- **Level 2:** `--wait` only; no `--atomic`
- **Level 3:** `--atomic --timeout 5m --wait` for production upgrade
- **Level 4:** All of L3 + readiness probes verified + post-render diff shown
- **Level 5:** All of L4 + values-file diff against previous release; chart version diff explained

### Dimension 6: Approval Discipline
Destructive ops require explicit user APPROVE; rollback procedure documented.

- **Level 1:** Resource destroyed without approval
- **Level 2:** Catch-all approval covers many destructive ops
- **Level 3:** Per-destructive-op approval; rollback noted
- **Level 4:** Per-op approval + rollback procedure (state mv backup, helm rollback, `moved {}` block) documented
- **Level 5:** All of L4 + dry-run / `-target` blast-radius limited; recovery path tested in non-prod first

## Scoring Logic

- **Aggregate:** average of D1–D6
- **Pass threshold:** 3.8
- **Judge model:** Sonnet

## Anti-Patterns (Auto-Fail)

- Imperative apply when a GitOps controller owns the resource
- `terraform apply -target=...` used in production (anti-pattern; fragments state)
- `helm upgrade` on production without `--atomic --timeout --wait`
- Destructive op (resource destroy / state rm) without explicit user APPROVE
- `terraform` invoked on an OpenTofu repo (lockfile drift)

## Calibration Reference

- **Known-good:** `plugin/eval/calibration/infra-change/good/*`
- **Known-bad:** `plugin/eval/calibration/infra-change/bad/*`
