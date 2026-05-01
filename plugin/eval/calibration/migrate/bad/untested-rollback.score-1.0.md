# Postgres Upgrade

Going from PG13 to PG14.

## Plan

1. Stop the app
2. Run pg_upgrade
3. Start the app
4. If it breaks, restore from backup

## Rollback

We have backups. If something goes wrong we'll restore. This should work.

## Tests

Will run during the window.

## Risks

None really. Postgres upgrades are usually fine.
