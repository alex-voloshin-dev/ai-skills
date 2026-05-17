# Security Audit Report — Auth Flow + Dependency Scan

> Scope: secrets, deps, auth (per `--scope "secrets,deps,auth"`)
> Audit standards: OWASP Web Top 10 (2021), OWASP GenAI/LLM Top 10 (2025) — N/A this audit (no LLM components in scope)

## Summary

3 findings: 0 CRITICAL, 1 HIGH, 2 MEDIUM. Remediation plan attached separately.

## Findings

### HIGH-1 — Session token replay window
**Category:** OWASP A07:2021 — Identification and Authentication Failures
**Location:** `src/auth/token.py:42-58`, `src/auth/session.py:91`
**Risk:** Session tokens have no nonce. A captured token replays for the full lifetime (8h).
**Reproduction:** Capture `Set-Cookie: session=...` from any login response; replay against any protected endpoint within 8h → 200 OK with original user's data.
**Threat model:** Network attacker on shared coffee-shop wifi (TLS terminates at LB; LB → app over TLS; assumption: TLS holds). Worse if `Secure` flag absent (separately fixed in #4218).
**Severity justification:** likelihood Medium (TLS holds in normal case), impact High (full session takeover).
**Mitigation (suggested owner: backend):**
1. Add `nonce` claim to JWT (rotate per request)
2. Validate nonce against per-user counter
3. Rotation policy documented
**Test case:** integration test that replays a captured token after a fresh request — must 401.

### MED-1 — Outdated `requests` library with known CVE
**Category:** OWASP A06:2021 — Vulnerable and Outdated Components
**Location:** `requirements.txt:18` — `requests==2.28.1`
**CVE:** CVE-2024-35195 (info disclosure in `Session.send` redirect handling) — fixed in 2.32.0
**Severity justification:** likelihood Low (specific to redirect-following with auth), impact Medium (info disclosure).
**Mitigation (suggested owner: devops):**
1. `requests==2.32.3` (current latest as of audit date)
2. Run integration suite to verify no breaking changes (changelog reviewed: backward-compat)
**Auto-fixable:** yes (PR #4231 generated alongside this audit).

### MED-2 — `httpOnly` flag missing on debug cookie
**Category:** OWASP A03:2021 — Injection (XSS surface)
**Location:** `src/middleware/debug.py:23` (only mounted in dev/staging)
**Risk:** XSS could read debug cookie → leaks request trace IDs.
**Severity justification:** Medium (dev/staging only; no production exposure); fix is trivial.
**Mitigation:** add `httpOnly=True` to cookie builder.
**Auto-fixable:** yes.

## What Was Checked (transparency)

- Secrets scan: pii-patterns.txt run against entire src/ tree → 0 matches (good)
- Dependency scan: `pip-audit` against `requirements.txt` → 1 finding (MED-1 above)
- Auth flow review: traced login, session, logout, token-refresh paths → 1 finding (HIGH-1)
- CSRF: existing `Django-style` token validates correctly on state-changing endpoints (verified)
- Rate limit: `/login` rate-limited at 10/min/IP (configured correctly)
- Password policy: bcrypt cost 12 (current best-practice); minimum length 12 (good)

## False Positives Identified + Dismissed

- `tests/fixtures/test_users.py:8` — `password = "test-password-not-real"` flagged by secret-pattern grep; reviewed and confirmed test fixture; whitelisted in `.ai-skills-memory/.committed/security/false-positives.md`
- `docs/architecture/auth.md:142` — example JWT secret in code block; reviewed; whitelisted (clearly marked as example)

## Coverage Notes

- GenAI/LLM Top 10 N/A — no AI/LLM components in audit scope
- Crypto review N/A — out of scope per `--scope` flag (will need separate `--scope crypto` run)
