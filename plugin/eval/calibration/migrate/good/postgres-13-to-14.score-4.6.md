# Migration Plan — Postgres 13.10 → 14.11

## Pre-flight Checklist

- [x] Backup verified (last full backup: 2026-04-13 02:00 UTC; restore tested into staging on 2026-04-14)
- [x] Replication paused on read-only replicas during cutover window
- [x] Compatibility matrix reviewed:
  - All extensions: pg_stat_statements (compat), postgis 3.4 (compat), timescaledb 2.13 (NEW: requires 14.x — also tested)
  - All client libraries: psycopg2 2.9.9, sqlalchemy 2.0.27, JDBC 42.7.2 — all listed as 14-compat in their changelogs
- [x] Storage requirements: +5% during pg_upgrade --link mode → confirmed enough headroom
- [x] Maintenance window scheduled with stakeholders (2026-04-22 02:00–04:00 UTC; 2h budget, 30m expected)

## Forward Procedure

1. T-15m: drain new connections (LB removes app from pool)
2. T-10m: wait for in-flight transactions ≤ 5; manual abort > 5
3. T-5m: stop application
4. T-0: snapshot for rollback
5. T+0–T+10: `pg_upgrade --link --jobs=8`
6. T+10: ANALYZE all schemas (statistics rebuild)
7. T+15: smoke test (read + write to canary tables)
8. T+20: data integrity check (row counts + checksums on top-50 tables)
9. T+25: enable application; LB adds back to pool
10. T+30: monitor SLIs for 30 min before declaring success

## Rollback Procedure (TESTED 2026-04-14 on staging clone)

1. Stop application
2. Mount the snapshot from T-0
3. Restart Postgres 13.10 instance from snapshot
4. Reconfigure replication (retain replica catch-up window)
5. Smoke test + data integrity check
6. Re-enable application

Recovery time measured in dress rehearsal: 14 min from "ROLLBACK" decision to application back up.

## Data Integrity Checks

Pre-cutover baseline captured 2026-04-21 18:00 UTC:
- Row counts per table (top 50 + all > 1M rows): saved to `migrate-2026-04-22/baseline-rowcounts.json`
- Checksums on `users`, `orders`, `payments` (3 highest-risk tables): saved to `baseline-checksums.json`
- Foreign-key constraint count: 142
- Index count: 318

Post-migration verification compares against baseline. Diff = 0 expected (excluding the snapshot-time delta from T-15m).

## Performance Baseline

- `EXPLAIN ANALYZE` captured for top-10 query patterns 2026-04-15
- Post-migration replay measured on staging clone: latency change < 3% on all 10
- p99 query time: 142ms → 138ms (slight improvement from PG14 query planner)

## Risk Matrix

| Risk | P × I | Mitigation |
|---|---|---|
| pg_upgrade fails mid-process | L × H | --link mode is reversible until ANALYZE; abort + restore snapshot |
| Application bug exposed by stricter PG14 SQL | M × M | Staging dress rehearsal completed; 0 issues; CI test suite passes against PG14 |
| Replication lag on resume | M × L | Replicas paused pre-cutover; catch-up time ~ 8 min based on staging |
| Storage exhaustion during --link | L × H | Pre-checked; 30% headroom available |

## Sign-off
- Engineering: approved 2026-04-19
- DBA: approved 2026-04-20 (rollback tested + signed)
- On-call SRE: scheduled for the window
