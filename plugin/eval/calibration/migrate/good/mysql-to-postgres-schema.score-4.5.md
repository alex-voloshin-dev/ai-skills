# Migration Plan — MySQL → PostgreSQL (schema + data)

## Pre-flight Checklist

- [x] Backup verified (MySQL 8.0 full backup 2026-04-15; restore tested on staging)
- [x] Replication paused on MySQL read replicas
- [x] PostgreSQL 15.2 cluster provisioned and tested
- [x] Data size: 847GB user tables; 156GB indexes (staging mirror identical)
- [x] Application compatibility: tested all ORM queries (SQLAlchemy + Hibernate) against PG on staging; 3 dialects fixed
- [x] Maintenance window: 2026-04-28 11:00–13:00 UTC
- [x] Client library versions: mysql-connector-java 8.0.33 (tested with PG driver 42.7), PyMySQL 1.1.0 → psycopg2 2.9.9

## Forward Procedure

1. **T-30m:** run final MySQL-to-PG dump validation (row counts match 100%)
2. **T-20m:** drain connections; pause LB
3. **T-10m:** MySQL read-only mode (FLUSH TABLES WITH READ LOCK)
4. **T-0:** capture checksum baseline on 15 highest-traffic tables
5. **T+0–T+8m:** import schema + data via pg_restore (parallel jobs=12)
6. **T+8m:** ANALYZE on all schemas (statistics rebuild)
7. **T+10m:** foreign-key constraint verification + index count check
8. **T+12m:** smoke test (CRUD on canary data)
9. **T+15m:** switch connection string; enable LB
10. **T+20–T+60m:** monitor query performance + error rates

## Rollback Procedure (TESTED 2026-04-16 on staging)

1. Disable LB
2. Switch connection string back to MySQL
3. Restart application
4. Verify MySQL still has all data (read-only snapshot preserved)
5. Resume MySQL replication
6. Resume normal operations

Recovery time (staging dress rehearsal): 8 minutes from "switch back" to app up.

## Data Integrity Checks

**Pre-migration baseline (2026-04-27 20:00 UTC):**
- Row counts per table (users: 2.1M, orders: 18.3M, items: 47.2M, etc.)
- Checksums on users, orders, payments, transactions
- Foreign-key constraint count: 89
- Total index count: 487

**Post-migration verification:**
- Row counts match baseline 100%
- Checksums match (0 data corruption)
- Constraints verified OK
- Index rebuild completes without errors

## Performance Baseline

Captured on MySQL staging (pre-cutover):
- Top-20 query patterns: avg latency 45ms, p99 180ms
- Throughput: 12,000 req/sec @ 200 concurrent connections
- Replication lag: < 100ms

Staging migration test (MySQL→PG): latency 47ms avg, p99 185ms (negligible regression; PG query planner may even improve).

## Risk Matrix

| Risk | P × I | Mitigation | Owner |
|---|---|---|---|
| Network timeout during 8min import | M × M | Connection pool timeout increased to 15s; retry logic enabled | database-eng |
| PG autovacuum blocks app post-cutover | M × M | Autovacuum tuned before cutover; aggressive tune for first 1h | database-sre |
| Application code incompatibility (dialects) | M × H | All ORM tests run vs PG on staging; found + fixed 3 dialect issues pre-cutover | app-team |
| Constraint violation on import | L × H | Constraints disabled during import; re-enabled + validated post-import | database-eng |

## Sign-off

- DBA: approved 2026-04-17 (rollback tested + procedure signed)
- Engineering: approved 2026-04-18
- On-call SRE: scheduled + briefed 2026-04-27 10:00 UTC
