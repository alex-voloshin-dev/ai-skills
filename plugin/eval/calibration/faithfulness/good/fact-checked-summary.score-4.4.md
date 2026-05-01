# Summary of Source Material — Factual Accuracy Check

Source: Research paper "Efficient Caching Strategies for Distributed Systems" (Zhang et al., 2024)

## Summary

Zhang et al. conducted experiments comparing three cache invalidation strategies: TTL-based, event-driven, and hybrid. Testing on a simulated e-commerce workload with 1 million keys showed event-driven invalidation achieved 45% lower p99 latency (from 240ms to 132ms) compared to TTL-based, at the cost of 12% higher network traffic for invalidation events. Hybrid approach balanced both metrics: 15% latency improvement with 3% traffic overhead.

The paper recommends event-driven invalidation for systems where cache misses are costly (real-time analytics) and hybrid for systems balancing cost and responsiveness.

## Fact Checks (source quotes)

1. **Event-driven latency improvement: 45% claim**
   - Source p.8, Table 4: "Event-driven p99 latency: 132ms vs TTL 240ms" = (240-132)/240 = 45%. Correct.

2. **Network traffic overhead: 12% for event-driven**
   - Source p.9, Figure 6: "Event-driven total network: 1.12x baseline". Correct (12% overhead).

3. **Hybrid results: 15% latency + 3% traffic**
   - Source p.10, Table 5: "Hybrid p99: 204ms (15% vs TTL baseline)" and "traffic: 1.03x baseline". Correct.

4. **1 million keys used in experiments**
   - Source p.5, Section 3.2: "Testing with 1M keys per cache instance". Correct.

## Confidence

High. All claims grounded in specific table/figure citations. No speculation or inference.
