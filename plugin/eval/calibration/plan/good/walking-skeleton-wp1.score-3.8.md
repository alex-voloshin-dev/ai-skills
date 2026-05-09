# Implementation Plan — Order-Refund flow

> Source PRD: `prd/refund-flow-v1.md`
> Architecture read: `ARCHITECTURE.md` (order-service, payment-service, ledger), `CLAUDE.md` (Java 21 + Spring Boot 3)
> Reviewers: product-manager + solution-architect + system-architect (REVIEW-LOG below)

## Architecture grounding

- `order-service` owns order state; transitions only via state-machine
- `payment-service` proxies Stripe; responsible for refund API calls
- `ledger` records double-entry rows; eventually consistent via Outbox
- New state `REFUND_REQUESTED` to be added to order state-machine

## WP-1: Walking skeleton (thinnest E2E)

Single happy-path: customer-initiated refund on a single-item order paid by card, full refund, no edge cases.

- Endpoint: `POST /orders/{id}/refund` (order-service)
- Calls payment-service refund proxy synchronously (no async retry yet)
- Records ledger entry inline (Outbox added in WP-3)
- Returns 200 + refund-id

DoR: API contract approved; Stripe sandbox key available
DoD: E2E test creates order → pays → refunds; ledger row exists; integration test green; manual sandbox click-through works

## WP-2: State-machine + persistence

Extend order state-machine with `REFUND_REQUESTED → REFUND_COMPLETED / REFUND_FAILED`. Persist transitions.

DoR: WP-1 merged
DoD: state-machine unit tests cover all valid transitions + 3 invalid; flyway migration applied

## WP-3: Async retry + Outbox

Replace inline payment + ledger calls with Outbox-driven async dispatch. Retry with expo backoff.

DoR: WP-2 merged
DoD: chaos test (50% Stripe failure rate) shows eventual success; no double-refund

## WP-4: Partial + multi-item refunds

DoR: WP-3 merged
DoD: 6 partial-refund cases pass; idempotency key tested

## WP-5: Admin override path

DoR: WP-4 merged
DoD: admin role can refund any order; audit log entry per override

## Dependency graph

```
WP-1 ── WP-2 ── WP-3 ── WP-4 ── WP-5
```

Linear by design — refund correctness depends on state-machine integrity. No parallelization until WP-4 done.

## Estimation (three-point, dev-days)

| WP | Best | Likely | Worst | PERT |
|---|---:|---:|---:|---:|
| WP-1 | 2 | 3 | 5 | 3.2 |
| WP-2 | 2 | 3 | 4 | 3.0 |
| WP-3 | 4 | 6 | 9 | 6.2 |
| WP-4 | 3 | 5 | 8 | 5.2 |
| WP-5 | 1 | 2 | 3 | 2.0 |
| **Sum** | | | | **19.6 days** |

## REVIEW-LOG

| Reviewer | Comment | Disposition |
|---|---|---|
| solution-architect | "WP-1 inline ledger write breaks pattern" | accepted as deliberate skeleton tradeoff; WP-3 reverts to Outbox |
| product-manager | "Need partial refunds in v1" | accepted; sequenced as WP-4 (was de-scoped originally) |
| system-architect | "Idempotency key on refund POST" | accepted; added to WP-1 DoD |
