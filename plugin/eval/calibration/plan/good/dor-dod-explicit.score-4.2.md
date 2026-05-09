# Implementation Plan — Two-Factor Auth (TOTP)

> Source PRD: `prd/2fa-totp-v1.md`
> Architecture read: `ARCHITECTURE.md` (auth-service, account-service, mobile, web), `CLAUDE.md` (Python 3.12 + FastAPI services, Next.js web, RN mobile)
> Reviewers: product-manager + solution-architect + system-architect (REVIEW-LOG attached)

## Work packages

### WP-1: TOTP secret + enrollment endpoint (auth-service / python-engineer)

**DoR (entry criteria):**
- PRD §3.2 accepted by product-manager
- Threat model reviewed by security-engineer (no blocking issues)
- `pyotp` 2.9 dependency approved per dependency policy
- Database migration template stub merged

**DoD (acceptance criteria):**
- `POST /2fa/enroll/start` returns `{otpauth_uri, secret_b32}` for authed user
- `POST /2fa/enroll/verify` accepts 6-digit code and persists `enabled=true`
- Secret encrypted at rest (KMS envelope)
- Tests: `pytest tests/test_2fa.py` covers happy + invalid-code + replay-detection
- Lint + mypy clean
- API doc updated; example curl in README

### WP-2: Login challenge integration (auth-service / python-engineer)

**DoR:** WP-1 merged; OpenAPI delta approved by mobile + web tech leads
**DoD:**
- `POST /auth/login` returns `{challenge_token, requires:"totp"}` if 2fa enabled
- `POST /auth/login/totp` exchanges challenge_token + code for session
- Token TTL 5 min; one-time use; replay rejected
- Test: `test_login_totp_required` + `test_login_totp_replay_rejected`
- Load test: p99 latency unchanged within 10ms

### WP-3: Backup codes (auth-service / python-engineer)

**DoR:** WP-2 merged
**DoD:**
- `POST /2fa/backup-codes/generate` returns 10 single-use codes
- Codes stored hashed (argon2)
- `test_backup_code_consumed_once` green
- UX team signed off on display format

### WP-4: Web enrollment UI (web / ts-engineer)

**DoR:** WP-1 contract frozen; design tokens published
**DoD:**
- `/settings/security` page renders QR + manual-entry secret
- Submit flow verifies via WP-1 endpoint
- Cypress E2E `2fa-enrollment.spec.ts` green
- WCAG 2.2 AA (focus visible, target size) verified via axe

### WP-5: Mobile enrollment UI (mobile / rn-engineer)

**DoR:** WP-1 contract frozen
**DoD:**
- Settings → Security → 2FA flow
- Detox E2E green on iOS + Android
- Camera-permission denial path handled

### WP-6: QA regression + rollout playbook (qa-engineer)

**DoR:** WP-2 + WP-4 + WP-5 merged
**DoD:**
- 24-test regression matrix executed (web/mobile × 4 browsers × happy/sad)
- Rollback rehearsal completed; recovery < 5 min
- Runbook published in `runbooks/2fa-enable.md`

## Dependency graph

```
WP-1 ──┬── WP-2 ── WP-6
       ├── WP-3
       ├── WP-4 ──┘
       └── WP-5 ──┘
```

WP-3 / WP-4 / WP-5 parallel. Critical path: WP-1 → WP-2 → WP-6.

## Estimation (Fibonacci story points, anchored)

Anchor: WP-2 = 5 points (similar to past JWT refresh feature).

| WP | Points | Best (d) | Likely (d) | Worst (d) |
|---|---:|---:|---:|---:|
| WP-1 | 5 | 3 | 4 | 6 |
| WP-2 | 5 | 3 | 4 | 6 |
| WP-3 | 3 | 1 | 2 | 4 |
| WP-4 | 8 | 4 | 6 | 9 |
| WP-5 | 8 | 4 | 6 | 9 |
| WP-6 | 5 | 2 | 3 | 5 |

## REVIEW-LOG (full)

| Reviewer | Comment | Disposition |
|---|---|---|
| product-manager | "Backup codes are required at GA, not phase-2" | accepted; WP-3 brought into v1 scope |
| solution-architect | "WP-1 must encrypt secret at rest" | accepted; KMS envelope added to DoD |
| system-architect | "WP-2 challenge_token replay handling" | accepted; one-time-use + replay test added to DoD |
| product-manager vs system-architect | "Backup codes UX in WP-3 vs WP-4" | resolved per priority (PM > SA > SysA) — backup codes shown only after enrollment success in WP-4 |
| solution-architect | "Cypress E2E flake risk in CI" | accepted; QA owner adds retry-once policy in WP-6 |
