# PRD — Two-Factor Authentication

> Template owned by `feature-design` skill. Producer: `product-manager` agent (Wave 1). Drop concrete values into every section before handoff. Frameworks borrowed from Linear's PRD, Spotify RFC, and Shape Up pitch.

## TL;DR / Overview

One paragraph, ≤ 80 words. Reader should grasp the feature from this alone.

> Example: Add an opt-in second authentication factor (TOTP via authenticator app, with SMS as managed fallback) to the customer login flow. Targets the 12% of paid-tier accounts marked `compliance_required` and unblocks SOC 2 audit. Ships behind a per-tenant feature flag, defaults off for free tier, default on for Enterprise. Success = 60% Enterprise opt-in within 30 days, zero net increase in support tickets per active user.

## Problem statement

What hurts today, who feels it, and the proof. Cite tickets, NPS verbatims, churn cohort data, or compliance findings.

> Example: 4 of our last 11 enterprise renewals stalled on the 2FA control item in their security questionnaire (deals worth ~$320K ARR). Support sees 2.1 password-reset tickets per 100 monthly active users, and forensic logs show 0.3% of monthly logins originate from credential-stuffing patterns. SOC 2 Type II auditor flagged absence of MFA as a Tier-1 finding due 2026-08-31.

## Target users

### Ideal Customer Profile (ICP)

> Example: Enterprise admins (1 per tenant, ≥ 100-seat plan) with explicit compliance officer involvement; Series B+ SaaS companies in fintech, healthtech, or B2B infrastructure.

### Jobs To Be Done (JTBD)

- When my auditor asks for evidence of MFA, I want to point at a tenant-wide enforcement toggle, so I can close the finding without per-user followup.
- When an end-user is enrolling, I want recovery codes auto-generated, so I do not flood IT with lockout tickets.

## Solution overview

Two paragraphs max. What changes from the user's perspective; what we are NOT doing.

> Example: Admins enable 2FA per tenant; users see an enrollment prompt at next login that walks them through QR-code TOTP setup with 8 single-use recovery codes. SMS is offered only when the tenant explicitly enables it (cost: $0.012/message). Admins can view per-user enrollment state and force re-enrollment. We are NOT building hardware-key (WebAuthn) support in v1 — tracked as follow-up.

## User stories with acceptance criteria

| ID | Story | Acceptance criteria (Gherkin-ish) |
|---|---|---|
| US-1 | As an admin I want to enforce 2FA tenant-wide | Given I am admin, when I toggle "Require 2FA" on, then all users without 2FA are forced into enrollment at next login within 24h |
| US-2 | As a user I want to enroll using my authenticator app | Given enrollment prompt, when I scan QR + submit a 6-digit code, then 2FA is active and 8 recovery codes are downloadable once |
| US-3 | As a user I want to recover access if I lose my device | Given I have a recovery code, when I enter it on the login screen, then I am logged in and that code is invalidated |

## Success metrics

| Metric | Baseline | Target | Window |
|---|---|---|---|
| Enterprise tenant 2FA opt-in | 0% | 60% | 30 days post-GA |
| Support tickets per 100 MAU (auth-related) | 2.1 | ≤ 2.1 | 60 days post-GA |
| Credential-stuffing-pattern logins | 0.3% | < 0.05% on 2FA-enrolled accounts | 60 days post-GA |
| SOC 2 finding | Open | Closed | Audit cycle 2026 |

## Scope

### In scope (v1)

- TOTP enrollment + login challenge
- 8 single-use recovery codes per user
- SMS fallback (tenant-opt-in)
- Admin enforcement toggle + per-user enrollment dashboard
- Audit log entries for enrollment, challenge, recovery-code use

### Out of scope (explicit non-goals)

- WebAuthn / hardware keys
- Push-notification 2FA via mobile app
- 2FA for API-key-based machine accounts
- SSO/SAML interaction (handled by separate IDP integration)

## Open questions

1. Should recovery codes auto-rotate on use of last code, or prompt admin? *(owner: pm, due: design review)*
2. Cost model for SMS — pass through to tenant or absorb in Enterprise SKU? *(owner: pricing, due: pre-GA)*
3. Backup TOTP shared-secret recovery — store encrypted by tenant key, or never? *(owner: security-engineer, due: architecture review)*

## Risks (high-level only — full register in `RISKS.md`)

- **User lockout cascade** if recovery codes lost AND device lost — tracked R-3 in RISKS.md
- **SMS spend overrun** if abuser triggers repeated challenges — tracked R-5 in RISKS.md
- **Migration disruption** for tenants currently relying on IP allowlist as their security control — tracked R-7 in RISKS.md

---

*Cross-references: `ARCHITECTURE.md` for system design, `UX-FLOW.md` for enrollment journey, `IMPLEMENTATION-PLAN.md` for work-package decomposition.*
