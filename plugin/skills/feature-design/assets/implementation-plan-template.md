# Implementation Plan — Two-Factor Authentication

> Template owned by `feature-design` skill. Producer: `feature-design-lead`. Decomposes the PRD into work packages, each owned by one engineer role. Three-point estimates use **best / likely / worst** in working days. Walking-Skeleton WP-1 is mandatory: thinnest end-to-end path through the system, demoable, before any horizontal layer is fully built.

## Work-package overview

| ID | Title | Role | Estimate (B / L / W days) | dependsOn |
|---|---|---|---|---|
| WP-1 | Walking skeleton: TOTP enroll + challenge for one hardcoded admin | python-engineer + frontend-engineer | 1 / 2 / 4 | — |
| WP-2 | Persistence layer: 2fa_secrets, recovery_codes, audit_log tables | db-engineer | 1 / 2 / 3 | WP-1 |
| WP-3 | Recovery-code generation, hashing, single-use enforcement | python-engineer | 1 / 2 / 4 | WP-2 |
| WP-4 | Admin enforcement toggle (tenant-level) + force-re-enroll endpoint | python-engineer | 1 / 2 / 3 | WP-2 |
| WP-5 | Enrollment UI flow (QR scan, code confirm, recovery codes download) | frontend-engineer | 2 / 3 / 5 | WP-1, WP-3 |
| WP-6 | Login challenge UI + clock-skew hint copy | frontend-engineer | 1 / 2 / 3 | WP-1 |
| WP-7 | SMS fallback (Twilio adapter, rate limit, daily cap, alerting) | python-engineer | 2 / 3 / 6 | WP-3 |
| WP-8 | Audit-log writer + admin per-user enrollment dashboard | full-stack-engineer | 2 / 3 / 5 | WP-4 |
| WP-9 | E2E test pack (enrollment, login, recovery, lockout, SMS rate limit) | qa-engineer | 2 / 3 / 5 | WP-5, WP-6, WP-7 |

Critical path likely: WP-1 → WP-2 → WP-3 → WP-5 → WP-9 ≈ 12 likely days.

---

## WP-1 — Walking skeleton (MANDATORY FIRST)

> Walking-Skeleton pattern: thinnest end-to-end path through every architectural layer. Goal is NOT a complete feature — it is a proof that the deployment, request path, persistence, and UI render are wired and demoable. Everything else fills out from this scaffold. Cope-with-deletes, error handling, and edge cases come later.

| Field | Value |
|---|---|
| Title | TOTP enroll + challenge for one hardcoded admin user |
| Description | Hardcode a single admin's user-id; expose `/2fa/enroll` returning a fresh TOTP secret + QR; expose `/2fa/verify` accepting a 6-digit code; render a minimal "scan this, type code" page; persist secret in a single `users_2fa` row (no migrations layer yet). Demo: one human enrolls and logs in successfully end-to-end |
| Affected services | `auth-service` (new endpoints), `web-frontend` (one new page), `users` table (one new column added by ad-hoc DDL — replaced properly in WP-2) |
| Developer role | `python-engineer` (backend endpoints) + `frontend-engineer` (single page) |
| dependsOn | none |
| Best / Likely / Worst | 1 / 2 / 4 days |
| Definition of Ready | PRD US-2 finalized; ARCHITECTURE.md auth-service section drafted; pyotp library approved by security-engineer; staging tenant available |
| Definition of Done | Live demo recorded: empty account → enroll → next-login challenge passes → audit-log line appears in stdout. No automated tests required at this stage — that is WP-9. Code committed behind `feature.2fa_skeleton` flag, default OFF |
| WP-specific risks | Pyotp lib version mismatch with current Python (3.11) — verified at DoR; QR rendering library must work in our SSR pipeline (test in spike if uncertain) |

---

## WP-2 — Persistence layer

| Field | Value |
|---|---|
| Title | `2fa_secrets`, `recovery_codes`, `auth_events` tables + migrations |
| Description | Replace WP-1 ad-hoc column with proper schema. `2fa_secrets`: per-user encrypted secret + KMS key reference. `recovery_codes`: hashed (argon2id), one-row-per-code, used_at timestamp. `auth_events`: append-only log keyed by (tenant_id, user_id, event_type, timestamp) |
| Affected services | `auth-service` (read/write), `database` (new tables + migrations) |
| Developer role | `db-engineer` |
| dependsOn | WP-1 (for endpoint shape contract) |
| Best / Likely / Worst | 1 / 2 / 3 days |
| Definition of Ready | DATA-MODEL.md approved by security-engineer; KMS key alias provisioned in dev + staging |
| Definition of Done | Migration up/down both runnable on a copy of prod schema; rollback verified; query `EXPLAIN`s on the lookup-by-user-id path show index hit |
| WP-specific risks | KMS round-trip latency on hot path — pre-validate < 5ms p99 in staging |

---

## WP-9 — E2E test pack (illustrative — pattern same as WP-3..WP-8)

| Field | Value |
|---|---|
| Title | E2E test pack for 2FA |
| Description | Playwright suite covering: happy-path enrollment, challenge on next login, recovery-code single-use, recovery-code exhaustion path, SMS rate-limit triggering, admin force-re-enroll. Backend pytest suite for unit + integration on each endpoint |
| Affected services | `e2e-tests` repo, CI pipeline |
| Developer role | `qa-engineer` |
| dependsOn | WP-5, WP-6, WP-7 |
| Best / Likely / Worst | 2 / 3 / 5 days |
| Definition of Ready | All UI flows feature-flagged as `feature.2fa_v1`; staging tenant seeded with test users |
| Definition of Done | Coverage report shows ≥ 85% line coverage on auth-service 2FA module; CI green on 3 consecutive runs; flake rate < 2% over 50 nightly runs |
| WP-specific risks | Playwright TOTP timing flakes — use `pyotp.now() - 30s` strategy with explicit clock seed |

---

## Estimation conventions

- **Best**: everything goes right, no surprise, no review feedback round
- **Likely**: typical execution including one review round
- **Worst**: dependency surprise, second review round, or non-trivial spike inside the WP
- Schedule with **Likely** for sprint commitment; track Worst as buffer signal

## Sequencing notes

- WP-1 unblocks everything — start it on Day 1.
- WP-7 (SMS fallback) is the single biggest worst-case uncertainty; consider a 0.5-day spike before committing to its WP-Likely estimate.
- WP-9 starts with stub fixtures as soon as WP-5 lands; it does not have to wait for WP-7.

---

*Cross-references: `PRD.md` (US-1..3 trace into WP-4, WP-5, WP-3 respectively), `RISKS.md` (R-3 → DoR for WP-3, R-5 → DoD for WP-7).*
