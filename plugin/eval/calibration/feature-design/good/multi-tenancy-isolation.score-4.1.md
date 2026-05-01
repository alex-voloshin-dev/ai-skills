# Multi-Tenancy Isolation — Feature Design

> Feature: multi-tenant-isolation-2026q2
> Date: 2026-04-18
> Author: platform-architect
> Status: approved

## Goal & Success Metrics

Enable two independent SaaS customers to run workloads on shared infrastructure without data leakage or resource interference. Target: zero data-leakage incidents in Y1; resource contention alerts triggered within 60s of threshold breach.

## Acceptance Criteria

1. Customer data queries always return only data owned by the authenticated customer (enforced at DB query layer)
2. Resource quotas per tenant (CPU, memory) enforced; overage blocks further requests with clear error message
3. Audit log captures all cross-tenant access attempts (including failures); reviewable per tenant
4. Multi-tenant test suite passes 100% before rollout

## Architecture

| Component | Responsibility | Owner |
|---|---|---|
| Auth middleware | Extracts customer ID from JWT; sets request context | identity |
| Query rewriter | Adds `WHERE customer_id = ?` to all user-initiated queries | data-platform |
| Quota enforcer | Tracks per-tenant CPU/memory; returns 429 when exceeded | scheduler |
| Audit sink | Logs all data access + quota breaches; keyed by tenant | observability |

Sequence (data read): JWT decode → set context → query rewrite → audit log → return results.

## Trade-offs Considered

- **Query-layer vs row-level security:** chose query rewrite — simpler to audit, no database-specific RLS syntax. Slightly higher cost per query (~2ms) but acceptable.
- **Hard quotas vs soft quotas with burst:** hard quotas — predictability matters more than short bursts. Customers can request higher tier for sustained growth.
- **Per-request vs per-session audit:** per-request — finer grain; logs larger (estimated 50MB/day); retention window 90 days.

## Rollout

1. Wave 1: enable for read-only test customer account; run load test 3d
2. Wave 2: enable for 3 beta customers; monitor audit logs 7d
3. Wave 3: GA rollout; legacy single-tenant mode remains available 6 months

Gating: zero data-leakage detected, audit log error rate < 0.01%, quota enforcement latency < 100ms p99.

## Risks

| Risk | P × I | Mitigation | Owner |
|---|---|---|---|
| Quota bypass via session reuse | M × H | Quota state reset on JWT refresh; rate-limit JWT reissue | identity-eng |
| Audit log lag (stale context) | L × M | Synchronous audit writes on critical paths; async on bulk ops | observability |
| Query rewrite performance | M × M | Index plan per rewritten query; benchmarked vs baseline | db-eng |
| Customer quota miscalibration | M × L | Tier-wise defaults; customer support can adjust; reviewed monthly | product-ops |

## Rollback

Per wave: disable query rewriter (return customer_id check only); fall back to single-tenant path. Recovery < 2 min. Tested 2026-04-17 (measured: 1m45s).

## Open Questions

- How to handle legacy API clients that don't send JWT? (assigned: identity-pm)
- Quota limits per tier — customer feedback needed (assigned: product)

