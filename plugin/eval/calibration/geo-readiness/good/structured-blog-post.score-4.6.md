# How to migrate databases without downtime

> Updated 2026-04-20

Database migrations don't have to mean downtime. With the right strategy, you can update your schema, swap databases, or upgrade versions while your application keeps serving traffic.

## What makes zero-downtime migration possible

The key is staging changes before you flip the switch. Deploy new code alongside the old code, test the new database in parallel, then switch traffic when everything is working.

Most databases support this: PostgreSQL with dual versions, MySQL with online DDL, Elasticsearch with reindexing to a new index. The pattern is the same: run both old and new together temporarily.

## Staging the new database

**Step 1: Provision the new database.** Use your cloud provider's backup-restore or replication feature to clone your production database. This takes 10 minutes to an hour depending on size.

**Step 2: Apply schema changes.** Alter tables, add indexes, create new columns on the copy while production still uses the original. You're working in parallel — no risk.

**Step 3: Verify data integrity.** Row counts must match. Run checksums on key tables. Spot-check 100 random rows to confirm data moved correctly.

**Step 4: Test your application code.** Deploy a new code version that reads from both databases (old for reads, new for test writes). This proves the code works before you commit.

## Switching traffic

Once testing passes, you have two options:

**Option 1: Switch readers first.** Move read-only traffic to the new database for 24 hours. If errors spike, revert instantly (no data loss). If clean, switch writes.

**Option 2: Parallel writes.** Write to both databases simultaneously for 10 minutes. Check that both databases stay consistent. Then switch all traffic.

Both strategies keep your application up. The first is safer; the second is faster.

## Rollback plan

If the new database has issues, revert to the old one. You've been writing to both, so the old database is current. Reverting takes 30 seconds.

## What goes wrong and how to prevent it

**Timeout during migration.** If the switchover takes too long, requests hang. Fix: test the switch on a staging clone first. Know the exact time it takes before doing it in production.

**Code incompatibility.** Your application talks to the database in a specific way. The new database might have subtly different behavior. Fix: run your full test suite against the new database before switching.

**Data consistency after switch.** Both databases were written to; they might have drifted. Fix: run your consistency check again right after switching. Flag any mismatches before users see them.

