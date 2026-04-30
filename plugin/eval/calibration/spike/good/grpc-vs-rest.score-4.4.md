# Spike — Should we use gRPC instead of REST for service-to-service?

## Question
For our 8 internal services, would migrating from REST/JSON to gRPC reduce p99 latency by ≥ 20% and reduce serialization CPU by ≥ 40%?

## Time Cap: 120 min (used: 110 min)

## Findings

### Latency benchmark (real, on our staging hardware)
- REST p99 (current): 38ms median, 72ms p99 over 10k calls (`order-service` → `inventory-service`)
- gRPC p99 (proof-of-concept): 19ms median, 41ms p99 over 10k calls (same client/server pair)
- **Improvement: 50% median, 43% p99** — meets the 20% target

### Serialization CPU
- REST/JSON: 14% of CPU on `inventory-service` under benchmark load
- gRPC/Protobuf: 6% of CPU under same load
- **Improvement: 57% reduction** — meets the 40% target

### Operational cost
- Adds protobuf toolchain (codegen step in CI: +90s per build)
- Streaming requires careful client lifecycle management — moderate ramp-up time for new engineers
- Observability: gRPC standard interceptors integrate with existing OTel spans (verified)

### Migration effort estimate
- Per service: ~8 engineer-days (proto schema design + codegen wiring + dual-mode rollout + tests)
- 8 services × 8 days = 64 engineer-days
- Critical path 4 weeks (services with mutual dependencies must move together in pairs)
- Confidence: medium (one team has gRPC experience; rest don't)

## Trade-offs Considered

| Option | Latency | CPU | Effort | Tooling |
|---|---|---|---|---|
| Stay on REST/JSON | baseline | baseline | 0 | none |
| **gRPC/Protobuf** | -50% / -43% | -57% | 64 ed | adds protoc + grpc-tools |
| MessagePack on REST | -15% / -12% | -30% | 16 ed | adds msgpack lib only |
| Cap'n Proto | -55% / -50% | -60% | 80 ed | new ecosystem; no team experience |

## Recommendation

**GO — phased migration over 8 weeks.** gRPC meets both targets with reasonable effort. MessagePack is the cheaper alternative but doesn't hit the latency bar.

## Next Steps

- **Week 1–2:** schema design for the 2 highest-traffic service pairs (order ↔ inventory, payment ↔ order)
- **Week 3–4:** dual-mode rollout (REST + gRPC simultaneously, traffic split 50/50, measure)
- **Week 5–8:** remaining 6 services
- **Decision deadline for go/no-go on full rollout: end of Week 4**
- **Owner:** platform-team
- **Criteria for revisit:** if Week 4 measurements miss target on second service pair → re-spike on alternative options

## POC artifacts
- `spike-poc-2026-04-20/grpc-poc/` — minimal order ↔ inventory pair (commit 8a7f3b2)
- Benchmark results: `spike-poc-2026-04-20/results.csv`
