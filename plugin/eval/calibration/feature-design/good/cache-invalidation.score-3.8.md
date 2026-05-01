# Cache Invalidation Strategy — Feature Design

> Feature: cache-invalidation-2026q2
> Date: 2026-04-15
> Author: solution-architect
> Status: approved

## Goal & Success Metrics

Reduce stale-data incidents in the product catalogue from 12 per quarter to ≤ 2 per quarter by end of Q3 2026, by introducing time-bounded write-through invalidation with explicit purge fan-out across all CDN edges.

## Acceptance Criteria

1. P99 stale read window drops from 8h (current) to ≤ 30s after a write commits
2. Cache hit rate stays ≥ 92% (current 94%; ≤ 2pt drop acceptable)
3. Purge fan-out completes within 5s for the worst-case region pair
4. Zero new failure modes introduced (validated via chaos test on a non-critical subset before full rollout)

## Architecture

| Component | Responsibility | Owner |
|---|---|---|
| Write-through proxy | Intercepts catalog writes; emits invalidation event | platform |
| Purge dispatcher | Translates events to per-CDN purge API calls; deduplicates | platform |
| TTL fallback | 30-minute hard TTL behind active purge for safety | platform |

Sequence (write path): write → DB commit → emit purge event → CDN edge purge (fan-out) → ack within 5s.

## Trade-offs Considered

- **Active purge vs short TTL only:** chose active purge — 30s p99 stale window vs 5min from TTL alone. Cost: +1 service hop per write.
- **Sync vs async invalidation:** async — write latency stays ≤ 12ms p99; staleness window slightly larger but bounded.
- **Per-key vs prefix-purge:** per-key — finer control; ~3× the API cost; acceptable at current write volume.

## Rollout

1. Wave 1: enable write-through for `catalog.products` only (5% of catalog writes); monitor 7d
2. Wave 2: expand to `catalog.inventory` (40% of writes); monitor 7d
3. Wave 3: full rollout
4. Each wave gated on: P99 stale window measured, purge dispatcher error rate < 0.1%, no new alerts

## Risks

| Risk | P × I | Mitigation | Owner |
|---|---|---|---|
| Purge dispatcher overload at peak | M × H | Token-bucket rate limit per region; backoff + retry | platform-sre |
| CDN provider purge API outage | L × H | TTL fallback within 30 min; alert at error rate > 1% | platform-sre |
| Write-path latency regression | L × M | Pre-rollout perf test; rollback at >15% p99 increase | platform |
| Cost overrun on per-key purges | M × M | Quarterly cost review; switch to prefix-purge if > $X/mo | platform-finops |

## Rollback

Per wave: feature flag disables write-through; system falls back to TTL-only. Recovery within 5 min. Tested on 2026-04-12 dress rehearsal (recovery measured: 3m12s).

## Open Questions

- Should we expose a manual purge API to ops? (assigned: platform-pm)
- Region-pair latency for purge fan-out beyond US-EU pair? (assigned: platform-sre)
