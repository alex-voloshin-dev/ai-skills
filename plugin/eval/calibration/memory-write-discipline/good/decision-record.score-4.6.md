# Memory Entry — Architecture decision

**Topic:** Cache invalidation strategy choice

**Decision:** Use event-driven invalidation (not TTL-only) for product catalog.

**Context:** Product updates happen ~10/minute in prod. Current TTL-only approach (5min window) causes stale data in customer-facing catalog 30% of the time.

**Trade-offs evaluated:**
- TTL-only: simple, but 5min stale window
- Event-driven: complexity + latency (add 50ms per write), but invalidates instantly
- Hybrid: balance, but more code to maintain

**Recommendation:** Event-driven. Stale data costs > operational complexity.

**Implemented:** 2026-04-15. Event publisher on product model triggers cache purge to Redis. Measured impact: stale window dropped from 300s to <2s.

**Success criteria:**
- Stale data incidents < 1/quarter (vs. 12/quarter before)
- Event publish latency < 50ms p99

**Status:** Met both. Monitoring 30d before declaring stable.

**Related:** Spike report #4099 (GrpcVsRest evaluation), feature design #4050 (cache invalidation).

**Confidence:** High. Production metrics confirm.
