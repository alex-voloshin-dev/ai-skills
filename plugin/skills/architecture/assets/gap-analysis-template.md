# Gap Analysis — Current vs Target State

Captures the delta between where the system is today and where the architecture wants it to be. Used during architecture analysis, evolution initiatives, and pre-migration assessments. Each row is a discrete, addressable gap — not a vague aspiration. Severity drives prioritization; effort drives scheduling.

## Scoring Conventions

- **Severity:** `Critical` blocks production goals or compliance; `High` causes recurring incidents or significant friction; `Medium` slows velocity but no immediate failure; `Low` cosmetic or future-proofing.
- **Effort:** `S` ≤ 1 person-week, `M` 1–4 weeks, `L` 1–3 months, `XL` > 3 months.

## Gap Table

| Dimension | Current State | Target State | Gap Description | Severity | Effort | Owner | Notes |
|---|---|---|---|---|---|---|---|
| Test coverage — backend | Line coverage 42% on order-service; no contract tests | ≥ 80% line, contract tests for all 14 inter-service endpoints | Untested code paths in payment refund flow caused 3 prod incidents in Q1 | Critical | L | Backend Lead | Tracked in INC-2104, INC-2147, INC-2189 |
| API documentation | OpenAPI spec exists but is hand-written and 4 months stale; missing 6 endpoints | Spec auto-generated from code on every PR; 100% endpoint coverage; published to internal portal | Onboarding new partners takes 5+ days due to outdated docs | High | M | API Platform Team | Adopt oapi-codegen + generate-on-CI |
| Monitoring depth | Host-level CPU/memory only; no app-level traces or RED metrics | Distributed tracing on all services; RED metrics per endpoint; SLO dashboards | Mean time to diagnose tail-latency spikes is 47 min vs 10 min target | High | L | SRE | OpenTelemetry collector + Grafana Tempo PoC ready |
| Deploy automation | Manual `kubectl apply` from operator workstation; no GitOps; no rollback automation | ArgoCD GitOps; canary via Argo Rollouts; automated rollback on SLO breach | Risk of config drift, no audit trail, MTTR for failed deploys is 35 min | High | L | Platform Eng | Aligns with DORA elite-tier targets |
| Secrets management | `.env` files committed in 2 legacy repos; AWS keys 8 months old | All secrets in Vault; rotation policy enforced ≤ 90 days; no plaintext in repos | InfoSec audit finding SEC-2026-04; blocks SOC2 renewal | Critical | M | Security Eng | Vault is provisioned but not adopted by 4 services |
| ARCHITECTURE.md freshness | Last meaningful update 14 months ago; missing 3 services that shipped since | Living doc updated as part of every architecture-touching PR | Onboarding engineers form mental model from outdated diagrams | Medium | S | Tech Writer + Architects | Add CI lint rule on architectural directory changes |
| Database backup verification | Daily pg_dump runs but no restore-test automation | Weekly automated restore to ephemeral env + integrity check | Last manual restore drill was 9 months ago; RPO claim unverified | Medium | M | DBA / SRE | Integrate with DR runbook |
| Frontend build performance | CI build 18 min; no incremental cache; tests rerun on every push | ≤ 6 min CI build; remote build cache (Turborepo / Nx); test impact analysis | Slow CI is the #1 complaint in dev-experience survey 2026-Q1 | Medium | M | DX Team | Cost-justified by 11 engineers × 4 builds/day |

## Recommended Sequencing

1. **Critical / Short effort first** (S/M Critical rows above) — secrets management before SOC2 deadline.
2. **Critical / Long effort in parallel tracks** — test coverage and observability initiative running concurrently with separate owners.
3. **High Severity** picked up after Critical track stabilizes.
4. **Medium / Low** scheduled into quarterly platform-investment slots.

## Open Questions

- Which gaps require external dependencies (vendor procurement, security review, legal sign-off)?
- Are any gaps blocked on decisions still in flight (open ADRs)?
- Which gaps are candidates for collapse into a single migration initiative vs sequential fixes?
