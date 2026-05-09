# PR Created — fix(auth): rotate session token on privilege escalation

> Forge: GitHub
> Source: `/develop` produced `REVIEW-LOG.md` at `.ai-assets-memory/sessions/2026-05-08-auth-fix/REVIEW-LOG.md`
> Branch: `fix/auth-session-rotation` → `main`
> URL: https://github.com/acme/web/pull/4322

## REVIEW-LOG ingestion

`REVIEW-LOG.md` from `/develop` was treated as the primary source for the description below. RALF iteration count, reviewer sign-offs, and open follow-ups are surfaced verbatim.

- RALF iterations: 2 (oracle: `tests/auth/test_session_rotation.py::test_token_rotates_on_promote`)
- Reviewer sign-off: `security-engineer` ✓ (round 2), `backend-engineer` ✓ (round 2)
- QA sign-off: ✓ — 14/14 tests; coverage on `app/auth/session.py` rose from 67% → 91%
- Open follow-ups carried into "Out of Scope" below

## Title

`fix(auth): rotate session token when user role changes (CVE-INTERNAL-2026-04)`

## Body

### Summary
A user whose role was elevated mid-session retained the original token. An attacker with the old token could replay against newly-authorized endpoints. We now rotate the session token on any role change and invalidate the old token immediately.

### Changes (per REVIEW-LOG)
- `app/auth/session.py` — `rotate_on_role_change` middleware; old-token revocation list (TTL = remaining session lifetime)
- `app/auth/middleware.py` — wired in request pipeline before authorization check
- `tests/auth/test_session_rotation.py` — 14 cases covering elevation, demotion, concurrent sessions

### Risk + rollback
- Risk: low (logged-in users see one extra round-trip on role change)
- Rollback: revert PR; no schema change; revocation list is in-memory only

### Test plan
- [x] Unit + integration tests pass (14/14)
- [x] Manual: elevated role A, captured old token, attempted access → 401 ✓
- [x] Load: rotation adds ≤ 8 ms p99 (k6 smoke)

### Linked
- Issue: #4180 (internal CVE)
- ADR: `docs/adr/0042-session-token-rotation.md`

### Out of scope (open follow-ups from REVIEW-LOG)
- Move revocation list to Redis (currently per-pod in-memory) — tracked in #4325
- Add admin-tool to force-rotate sessions for an account — tracked in #4326

## Reviewers

Per CODEOWNERS for `app/auth/**`:
- @acme/security (required)
- @acme/backend (required)

## Branch hygiene

- Branch is `fix/auth-session-rotation`, not `main`
- Working tree clean
- Rebased on `origin/main`

## Untrusted-content handling

Diff is 480 LOC. Summary written from `git log --stat` + `REVIEW-LOG.md` (both trusted). Raw diff was not pasted into the LLM prompt — only file list + commit messages.
