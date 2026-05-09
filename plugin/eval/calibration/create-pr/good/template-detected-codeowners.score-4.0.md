# PR Created — feat(billing): add proration on plan upgrade

> Forge: GitHub
> Branch: `feat/billing-proration` → `main`
> URL: https://github.com/acme/web/pull/4318

## Repo conventions detected

- `.github/PULL_REQUEST_TEMPLATE.md` present — body filled per template sections
- `CODEOWNERS` parsed:
  - `app/billing/**` → @acme/payments
  - `app/api/billing/**` → @acme/payments, @acme/api-platform
- Reviewers suggested: `@acme/payments` (required), `@acme/api-platform` (required)
- `.github/labeler.yml` matched `area/billing` and `area/api` — labels applied

## Branch hygiene

- Current branch: `feat/billing-proration` (not main)
- Working tree clean (`git status` empty)
- Rebased on `origin/main` (HEAD is 0 commits behind base)

## Title

`feat(billing): prorate charges on mid-cycle plan upgrade`

## Body (rendered from template)

### Summary
Customers upgrading mid-cycle were charged the full new-tier price. This change prorates by remaining seconds in the billing period and credits unused old-tier value.

### Changes
- `app/billing/proration.py` — new `compute_proration` helper
- `app/api/billing/upgrade.py` — calls helper before invoice item create
- `tests/billing/test_proration.py` — 14 cases including DST boundary

### Type
- [x] Feature
- [ ] Bug fix
- [ ] Breaking change

### Test plan
- [x] Unit: `pytest tests/billing/test_proration.py` — 14/14 pass
- [x] Integration: Stripe test-mode upgrade flow verified end-to-end
- [x] Regression: existing upgrade flow unchanged for full-cycle upgrades
- Manual smoke after deploy: upgrade a test account from Pro to Enterprise mid-cycle, verify invoice line items.

### Screenshots
N/A (server-side)

### Rollback
Revert PR. No DB migration; safe to revert without data fix-up.

## CI

- Required checks: `lint`, `unit-tests`, `integration-tests`, `policy-conftest` — all queued
- Diff size: 312 LOC across 4 files (under the 800-line review-friendly cap)
