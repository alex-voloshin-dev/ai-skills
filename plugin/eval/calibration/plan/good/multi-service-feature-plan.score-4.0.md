# Implementation Plan — In-App Notifications v1

> Source PRD: `prd/in-app-notifications-v1.md`
> Architecture read: `ARCHITECTURE.md` (event bus, notification-service, mobile-bff), `CLAUDE.md` (Go services, RN client)
> Reviewers: product-manager + solution-architect + system-architect (all 3 passes complete; REVIEW-LOG attached)

## Architecture grounding

- `notification-service` (Go) owns user-prefs + delivery
- `event-bus` (Kafka) carries domain events; new topic `notif.events.v1` to be added
- `mobile-bff` (Go) fans out to RN client via existing WebSocket
- `web-bff` already has SSE channel; reused
- Storage: existing Postgres `notification` schema; one new table `user_notification_pref`

## Work packages

| WP | Service / Role | Title | DoR | DoD |
|---|---|---|---|---|
| WP-1 | notification-service / go-engineer | Walking skeleton: emit `notif.created.v1` on user.signup; persist + deliver via WS to one test user | bus topic created; schema registry entry approved | E2E test: signup → WS receives notification ≤ 2s; `make test` green |
| WP-2 | data-platform / db-engineer | `user_notification_pref` table + migration + repo | WP-1 schema reviewed | migration applied on staging; repo unit tests ≥ 90% cov |
| WP-3 | notification-service / go-engineer | Pref-aware delivery (skip if user opted out) | WP-2 merged | integration test: pref=off → no delivery; pref=on → delivery |
| WP-4 | mobile-bff / go-engineer | WS subscription auth + per-user channel routing | WP-1 merged | load test: 1k concurrent users, p99 fan-out < 200ms |
| WP-5 | web-bff / ts-engineer | SSE adapter for notif.events.v1 (parallel to WP-4) | WP-1 merged | E2E: web tab receives event ≤ 1s |
| WP-6 | mobile-rn / ts-engineer | RN client: receive + render notif card | WP-4 contract frozen | RN unit tests + Detox E2E green |
| WP-7 | web / ts-engineer | Web client: receive + render bell + drawer | WP-5 contract frozen | Cypress E2E green |
| WP-8 | qa-engineer | Cross-platform regression suite | WP-6 + WP-7 merged | full suite green on CI |

## Dependency graph

```
WP-1 ──┬── WP-2 ── WP-3
       ├── WP-4 ── WP-6 ──┐
       └── WP-5 ── WP-7 ──┴── WP-8
```

No cycles. Critical path: WP-1 → WP-4 → WP-6 → WP-8. WP-3 has 2-day slack. WP-5+WP-7 parallel to mobile branch.

## Estimation (three-point, in dev-days)

| WP | Best | Likely | Worst | PERT mean |
|---|---:|---:|---:|---:|
| WP-1 | 2 | 3 | 5 | 3.2 |
| WP-2 | 1 | 2 | 3 | 2.0 |
| WP-3 | 2 | 3 | 5 | 3.2 |
| WP-4 | 3 | 4 | 7 | 4.3 |
| WP-5 | 2 | 3 | 4 | 3.0 |
| WP-6 | 3 | 4 | 6 | 4.2 |
| WP-7 | 3 | 4 | 6 | 4.2 |
| WP-8 | 2 | 3 | 4 | 3.0 |
| **Critical-path PERT** | | | | **14.7 days** |

PERT formula: `(best + 4*likely + worst) / 6`. Confidence band ±25%.

## REVIEW-LOG (excerpt)

| Reviewer | Comment | Disposition |
|---|---|---|
| product-manager | "WP-3 should include analytics events" | accepted; added `notif.delivered` analytics event to WP-3 DoD |
| solution-architect | "WP-4 fan-out at 1k users — what about 10k?" | deferred to phase 2; documented in PRD §non-goals |
| system-architect | "WP-1 walking skeleton must include the WS leg, not just persist" | accepted; DoR/DoD updated to require WS receive step |
| product-manager vs solution-architect | conflict on whether SSE is in v1 scope | resolved per priority order (PM > SA > SysA) — kept in v1 |
