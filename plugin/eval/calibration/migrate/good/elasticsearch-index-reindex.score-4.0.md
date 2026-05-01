# Migration Plan — Elasticsearch index reindexing (v7 → v8 analysis)

## Pre-flight Checklist

- [x] Snapshot created: `es-backup-2026-04-17` (16 indices, 340GB)
- [x] Staging cluster (3-node ES 8.10) provisioned; tested with production-scale data
- [x] Mapping changes reviewed: 2 field types changing (text → keyword, nested → flattened)
- [x] Analysis pipeline compatibility: 8 custom analyzers tested; all compatible
- [x] Application expectations: search queries tested against both v7 and v8 mappings; 1 query needed adjustment
- [x] Storage requirement: +20% during reindex; 60GB headroom confirmed
- [x] Maintenance window: 2026-05-04 01:00–02:30 UTC (1.5h budget; rolling reindex expected ~45min)

## Forward Procedure

1. **T-15m:** switch search to read-only (error on write attempts, clients queued)
2. **T-10m:** wait for in-flight requests ≤ 5
3. **T-0:** snapshot ES cluster state
4. **T+0:** begin reindex-by-query on index_v7 → index_v8 (parallel=4)
5. **T+30m:** reindex completes; validation begins
6. **T+35m:** checksums match baseline (doc count, hash of top-1000 by relevance)
7. **T+40m:** switch alias from index_v7 → index_v8
8. **T+45m:** warm cache (query top-100 search patterns against v8)
9. **T+50m:** enable write access; monitor for anomalies
10. **T+60–T+90m:** monitor latency + error rates

## Rollback Procedure (TESTED 2026-04-19 on staging)

1. Switch alias back to index_v7 (instant)
2. Verify write latency on v7 (should be normal)
3. Keep index_v8 for rollforward if needed
4. Monitor error rates; declare success after 10min clean

Rollback recovery time (staging): 2 minutes from decision to serving on v7.

## Data Integrity Checks

**Pre-cutover baseline (2026-05-03 18:00 UTC):**
- Document count per index: captured to JSON
- Checksum of top-1000 search results (sorted by score) for 5 key queries
- Query latency percentiles (p50, p95, p99)

**Post-cutover verification:**
- Doc counts match within 0.01% (allows for new writes during reindex)
- Search result checksums match (same ordering)
- Latency: within 5% of baseline

## Performance Baseline

Captured on v7 production (2026-04-10):
- Search latency p99: 245ms
- Indexing throughput: 8,000 docs/sec
- Replication lag: < 50ms

Staging reindex test (v7→v8): latency improved to p99 210ms (8% gain from v8 query planner).

## Risk Matrix

| Risk | P × I | Mitigation | Owner |
|---|---|---|---|
| Reindex query timeout | M × H | Timeout increased to 2h; slicing enabled (4 concurrent) | search-eng |
| Write queue buildup during reindex | M × M | Queue max 5000; clients see 503 after threshold (acceptable) | search-sre |
| Analysis pipeline incompatibility | L × H | All 8 custom analyzers tested vs v8 mappings; 0 failures | search-team |
| Alias switch race (writes during cutover) | L × M | Write lock held during alias switch (< 1s); atomic operation | search-sre |

## Sign-off

- Search team lead: approved 2026-04-18
- SRE: approved 2026-04-20 (rollback tested)
- On-call: scheduled for window
