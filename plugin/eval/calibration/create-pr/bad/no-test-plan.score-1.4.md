# PR Created — feat(api): add /v2/orders endpoint

> Forge: GitHub
> Branch: `feat/orders-v2` → `main`
> URL: https://github.com/acme/api/pull/4321

## Title

`feat(api): add /v2/orders endpoint with pagination`

## Body

### Summary
Adds a v2 orders endpoint with cursor pagination. Supersedes the v1 offset-based endpoint, which will be deprecated in a future release.

### Changes
- `app/api/v2/orders.py` — new endpoint
- `app/api/v2/__init__.py` — route registration
- `docs/api/v2/orders.md` — endpoint docs

### Type
- [x] Feature

### Test plan

(empty)

### Screenshots
N/A

## Reviewers

@acme/api-platform (auto-suggested per CODEOWNERS)

## Branch hygiene

- Not on main
- Working tree clean

## CI

Required checks queued: `lint`, `unit-tests`, `integration-tests`.

## Notes

Reviewer will not know what was tested. The endpoint touches order data — without a test plan, it is unclear whether the new pagination has been verified against real data, whether v1 still works, or whether auth/rate-limit behaviour was checked. Reviewer will have to ask, adding a round-trip.
