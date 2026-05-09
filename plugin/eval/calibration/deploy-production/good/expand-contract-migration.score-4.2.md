# Production Deploy: users-api v4.0.0 — expand-contract over 3 deploys

Schema migration: rename column `users.email` → `users.primary_email` plus add `users.verified_at`. Phased per `migrate/references/expand-contract.md`.

## Deploy A (this run): expand phase

Code v4.0.0 ships:
- Adds `users.primary_email VARCHAR(320) NULL` (additive — safe)
- Adds `users.verified_at TIMESTAMPTZ NULL`
- Application reads from `email` (legacy); writes to BOTH `email` AND `primary_email` (dual-write)
- Background job backfills `primary_email := email` for existing rows
- `verified_at` left NULL — populated only by new verification flow

## Pre-deploy checklist (passed)

- [x] /deploy-staging completed Deploy A 24h ago; backfill ran clean (~12M rows in 38min)
- [x] Tag v4.0.0 signed
- [x] DB migration tested forward (Deploy A) AND rollback (Deploy A → A-1) on snapshot replica
- [x] Argo Rollouts canary template configured for users-api with success-rate analyser
- [x] On-call paged

## Deploy

```bash
$ kubectl argo rollouts get rollout users-api -n production
Status: ✔ Healthy
Step: 8/8 (after canary)
```

Post-deploy verification:
```bash
$ psql -c "SELECT COUNT(*) FROM users WHERE primary_email IS NULL;"
 count
-------
     0
$ psql -c "SELECT COUNT(*) FROM users WHERE primary_email != email;"
 count
-------
     0
```

Backfill complete; columns are equivalent. Application happily dual-writes.

## Future (NOT this deploy)

- **Deploy B (next sprint)**: switch reads from `email` → `primary_email`. Dual-write continues. Roll back here if anything breaks.
- **Deploy C**: stop dual-write; reads/writes only `primary_email`.
- **Deploy D**: drop `email` column.

## Score rationale

Expand-contract sequence explicit (5), reads from legacy column preserved (5), backfill verified (5), rollback procedure tested ahead of time (4), each future deploy explicitly enumerated (4). Avg 4.2.
