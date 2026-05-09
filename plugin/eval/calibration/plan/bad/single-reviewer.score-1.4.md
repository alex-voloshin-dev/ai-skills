# Implementation Plan — Subscription Tiers

> Source PRD: `prd/subscription-tiers.md`
> Architecture read: yes — `ARCHITECTURE.md` and `CLAUDE.md` both consulted
> Reviewer: solution-architect only

## Work packages

| WP | Service | Title | Three-point (d) |
|---|---|---|---|
| WP-1 | billing-service | Tier model + migration | 2/3/5 |
| WP-2 | billing-service | Stripe product + price sync | 3/4/7 |
| WP-3 | api-gateway | Tier-based rate limit | 2/3/4 |
| WP-4 | web | Pricing page + upgrade flow | 4/6/9 |
| WP-5 | qa-engineer | Regression | 2/3/4 |

## Dependency graph

```
WP-1 ── WP-2 ── WP-3
                 └── WP-4 ── WP-5
```

No cycles. Looks correct.

## DoR / DoD

Each WP has a one-liner DoR + DoD (objective).

## REVIEW-LOG

| Reviewer | Comment | Disposition |
|---|---|---|
| solution-architect | "WP-3 needs cache invalidation for rate-limit config" | accepted; added to DoD |

## Issues with this plan

- Architecture was read and the WP decomposition is otherwise solid (estimates, graph, DoR/DoD all present)
- BUT: only solution-architect reviewed. product-manager and system-architect were not consulted
- product-manager would catch missing entitlement-revocation-on-downgrade scenario (real gap)
- system-architect would flag the api-gateway / billing-service consistency window as needing explicit treatment
- The multi-reviewer pass is a hard requirement of `/plan`; running with one reviewer is a process violation
