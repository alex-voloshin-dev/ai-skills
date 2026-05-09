# Non-Functional Requirements (NFR) Specification

Non-functional requirements describe quality attributes — how the system behaves, not what it does. Categories follow ISO/IEC 25010 (Performance Efficiency, Reliability, Security, Compatibility, Maintainability, Portability, Usability, Functional Suitability) plus operational concerns (cost, observability, compliance) common to production systems.

Every NFR row must be **measurable** — a target value with an explicit measurement method. Replace example values with project-specific numbers; remove rows that do not apply.

## NFR Table

| Category | Specific Requirement | Measurement | Target Value | Source / Justification |
|---|---|---|---|---|
| Performance — Latency | Order create endpoint p50 latency | Server-side histogram, 1-minute window | ≤ 120 ms | PRD-142 §3.2; checkout abandonment baseline |
| Performance — Latency | Order create endpoint p95 latency | Server-side histogram, 1-minute window | ≤ 250 ms | PRD-142 §3.2 |
| Performance — Latency | Order create endpoint p99 latency | Server-side histogram, 1-minute window | ≤ 500 ms | SRE error budget policy v3 |
| Performance — Throughput | Sustained order creation rate | Load test (k6, 30 min ramp) | ≥ 5,000 req/s | Black Friday 2025 peak ×1.5 |
| Scalability | Horizontal scale ceiling for Order API | Pods that can be added before DB connection saturation | ≥ 40 pods at 50 conn/pod | Postgres max_connections=2500, 30% headroom |
| Availability | Checkout flow SLA | Successful HTTP 2xx / total over rolling 30 days | 99.95% | Customer contract Tier-1 |
| Availability — RTO | Recovery time after region failure | Time from incident declared to traffic served from failover region | ≤ 15 min | DR policy DRP-2026-01 |
| Availability — RPO | Maximum acceptable data loss | Time gap between last replicated transaction and failover | ≤ 60 s | Finance audit requirement |
| Security | Authentication for all customer endpoints | OAuth 2.1 with PKCE; manual penetration test pass | 100% endpoints authenticated | OWASP ASVS L2 |
| Security | Secrets management | All secrets sourced from Vault, rotated on schedule | 0 hard-coded secrets; rotation ≤ 90 days | InfoSec policy SEC-04 |
| Compliance & Data Residency | EU customer PII storage | Data physically stored in eu-west region; access logged | 100% in EU; 0 cross-region replicas | GDPR Art. 44; HIPAA N/A; SOC2 CC6.1 |
| API Compatibility / Versioning | Backward compatibility window for v2 API | Months of support after v3 GA | ≥ 12 months with deprecation notices | Public API policy |
| Operability — Observability | Distributed trace coverage | % of inbound requests with full upstream/downstream trace | ≥ 95% | SRE platform SLO |
| Operability — Logs | Structured log retention | Days of searchable retention in central log store | ≥ 30 days hot, 365 days cold | Compliance + incident review |
| Cost | Infrastructure cost per 1k orders | Monthly cloud bill / order count | ≤ $0.45 | Finance budget FY26 unit-economics |

## Verification Methods

- **Performance / Throughput:** synthetic load tests in staging that mirror prod traffic shape, plus production SLO dashboards.
- **Availability:** monthly review of error-budget burn rate; quarterly DR drill measuring RTO/RPO.
- **Security:** automated SAST/DAST in CI, annual external penetration test, continuous secrets scanning.
- **Compliance:** quarterly access-log review, annual SOC2 audit, GDPR data-flow audit on schema change.
- **Cost:** monthly FinOps review; alert on unit cost drift > 15%.

## Out of Scope

List quality attributes that are **explicitly not** targets for this scope, so reviewers do not assume them:

- e.g., Multi-region active-active write traffic (single-region with passive failover only)
- e.g., Real-time analytics for the operations dashboard (acceptable lag ≤ 5 minutes)
