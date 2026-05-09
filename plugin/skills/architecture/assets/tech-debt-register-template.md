# Technical Debt Register

Tracks accumulated debt as **financial instruments**: every item has a *principal* (cost to repay), *interest* (ongoing cost paid every iteration), a *forces-payment* trigger, and a *priority* (Hot = pay now, Cold = monitor and revisit). Modeled on Ward Cunningham's debt metaphor and the McConnell taxonomy (intentional/unintentional, prudent/reckless).

## Conventions

- **ID:** `TD-NNN` — append-only; do not reuse numbers after closure.
- **Interest Cost:** the recurring tax — slowdown per change, defect rate, on-call burden, hiring difficulty, security exposure window.
- **Principal:** effort to fully repay (pay-down) the debt — `S` ≤ 1 wk, `M` 1–4 wk, `L` 1–3 mo, `XL` > 3 mo.
- **Risk:** what gets harder or breaks during repayment — backward-incompatible API change, data migration, security exposure during transition.
- **Forces Payment:** the looming requirement that converts Cold debt into Hot debt — dependency EOL, scale ceiling, regulatory deadline, blocking feature.
- **Priority:** `Hot` (repay this quarter), `Cold` (monitor; reassess each quarter).

## Register

| ID | Description | Location | Interest Cost | Principal | Risk | Forces Payment | Priority | Owner |
|---|---|---|---|---|---|---|---|---|
| TD-001 | Order-service uses synchronous Kafka publish inside DB transaction; tail latency tied to broker health | `services/order/internal/publish/sync.go` | Every Kafka maintenance event causes p99 latency spike (3 incidents YTD); +30 min on-call per occurrence | M (4 wks — implement transactional outbox per ADR-014) | Medium — requires consumer idempotency verification; safe via expand-contract over 2 releases | Black Friday 2026 traffic forecast +60%; current pattern won't survive | Hot | Backend Lead |
| TD-002 | Frontend monorepo has 3 versions of React (16.14, 17.0, 18.2) across 11 apps; shared component library compiled against 16 | `apps/*/package.json`, `packages/ui/` | New components must polyfill for 16; Storybook flaky; hiring complaint — candidates expect 18+ | L (10 wks — upgrade apps incrementally + drop UI-lib 16 support) | Medium — visual regression on 11 apps; requires Chromatic baseline refresh | React 16 LTS ended; security advisories no longer backported | Hot | Frontend Lead |
| TD-003 | No formal database migration tool; schema changes applied via ad-hoc SQL files in `db/migrations/`, no rollback scripts | `db/migrations/` (47 files since 2024) | DBA spends ~6 hrs/release reviewing diffs; one prod incident from out-of-order apply (INC-2089) | M (3 wks — adopt `golang-migrate` + backfill rollback scripts for last 6 months) | Low — tool addition is additive; legacy files stay as-is | None imminent — but next compliance audit will flag it | Cold | DBA |
| TD-004 | Customer-service exposes internal IDs (auto-increment integers) in public API responses, allowing enumeration | `services/customer/api/*.go` (response DTOs) | Enumeration vector flagged in last pen test; rate-limit mitigates but doesn't eliminate; 1 abuse case in 2025 | L (8 wks — introduce opaque tokens + dual-read window + deprecate integer IDs) | High — public API change; partner integrations consume current IDs; 12-month deprecation window required | Annual pen test re-test in Q3 2026; partner CISO escalation possible | Hot | Security Eng + API Platform |
| TD-005 | Search subsystem uses Elasticsearch 6.8 (EOL since 2022-08); custom plugins block straightforward upgrade | `infra/elasticsearch/`, `services/search/` | No security patches; cluster restarts require manual plugin rebuilds; SRE on-call burden +4 hrs/month | XL (16 wks — rebuild plugins on OpenSearch 2.x + dual-index migration) | High — search relevance regression possible; A/B test required; data re-index 2.4 TB | InfoSec deadline 2026-Q4; AWS managed-ES 6.8 retirement notice | Hot | Search Team Lead |

## Quarterly Review

At the end of each quarter, for each Hot row: confirm progress, escalate if blocked. For each Cold row: re-evaluate Forces Payment column — has anything changed (new dependency EOL announced, scale forecast revised, regulation passed) that would flip it to Hot? Capture closures with the closing PR/ADR link and remove the row to a separate `tech-debt-closed.md` archive.

## Anti-Patterns to Reject

- Vague items ("clean up service X") — split into concrete TD entries with measurable interest cost.
- Items without a Forces Payment column — without a trigger, the item is a wishlist, not debt.
- "Bundle everything into a v2 rewrite" — almost always more expensive than incremental repayment per item.
