# Security Audit Report — REST API Endpoints + Input Validation

> Scope: api, input-validation (per `--scope "api,input-validation"`)
> Audit standards: OWASP Web Top 10 (2021), OWASP GenAI/LLM Top 10 (2025) — N/A this audit (no LLM components in scope)

## Summary

4 findings: 1 CRITICAL, 1 HIGH, 2 MEDIUM. Remediation plan attached. No LLM Top 10 applicability.

## Findings

### CRITICAL-1 — SQL injection in order search endpoint
**Category:** OWASP A03:2021 — Injection
**Location:** `src/api/orders.py:87-92`
**Risk:** `GET /api/orders?search=<input>` constructs SQL directly without parameterization. Attacker can inject `' OR '1'='1` to bypass filters.
**Reproduction:** 
```
curl "http://localhost:8000/api/orders?search=' OR status='pending"
```
Returns all orders regardless of visibility. With admin account, can union-inject to extract user data.
**Threat model:** Authenticated user (customer) escalates to read all orders + see admin queries + potentially extract schema.
**Severity justification:** likelihood High (public endpoint, no rate limit on search), impact Critical (full data exfiltration).
**Mitigation (suggested owner: backend):**
1. Use parameterized queries (ORM with query params)
2. Input validation: allowlist characters (alphanumeric + hyphens only)
3. Stored procedure for order search if performance needed
**Test case:** `test_orders_search_injection_prevented` — confirm `' OR` in search returns empty set, not all orders.

### HIGH-1 — Missing rate limit on password reset endpoint
**Category:** OWASP A07:2021 — Identification and Authentication Failures
**Location:** `src/api/auth.py:156-165`
**Risk:** `POST /api/auth/reset-password` accepts unlimited reset requests. Attacker can brute-force reset tokens or spam users' inboxes.
**Reproduction:** 100 requests with same email → 100 reset emails sent. Tokens are 6-digit codes (only 1M combinations).
**Threat model:** Attacker auto-generates tokens and tests against target user's account.
**Severity justification:** likelihood High (no rate limit), impact High (account takeover).
**Mitigation (suggested owner: backend):**
1. Rate limit: 5 reset requests per hour per IP + email
2. Token length: increase from 6 to 8 digits or use 32-char random string
3. Token TTL: reduce from 24h to 15min
**Test case:** `test_reset_password_rate_limit_enforced` — confirm 6th request returns 429.

### MEDIUM-1 — Debug mode enabled in production
**Category:** OWASP A01:2021 — Broken Access Control (information disclosure)
**Location:** `config/prod.env` — `DEBUG=true` (should be false)
**Risk:** Stack traces leak source code paths, environment variables, database queries to error responses.
**Severity justification:** likelihood Medium (env var mis-config, happens during deployment), impact Medium (source code exposure, not direct RCE).
**Mitigation (suggested owner: devops):**
1. `DEBUG=false` in prod config
2. Error handler returns generic "Internal Server Error" in prod, preserves detailed logs server-side
3. CI gate: block deploy if DEBUG=true detected in prod config
**Test case:** `test_prod_debug_disabled` — POST invalid request, confirm response has no stack trace.

### MEDIUM-2 — CORS allows origin `*` with credentials
**Category:** OWASP A01:2021 — Broken Access Control
**Location:** `src/middleware/cors.py:12` — `allowed_origins: ["*"]` + `allow_credentials=true`
**Risk:** Browser security relaxed; any website can make authenticated requests on behalf of user.
**Severity justification:** likelihood Medium (unusual mis-config), impact Medium (session fixation, CSRF-like behavior).
**Mitigation (suggested owner: backend):**
1. Change `allowed_origins` to explicit list: `["https://myapp.com", "https://admin.myapp.com"]`
2. If `allow_credentials=true`, origins must be explicit (not `*`)
3. Document CORS policy in ADR
**Test case:** `test_cors_wildcard_with_credentials_blocked` — confirm wildcard + credentials rejected at startup.

## What Was Checked (transparency)

- API endpoint inventory: found 32 endpoints across 4 services
- Input validation: traced 28 endpoints for parameterization; 1 SQL-injectable found (CRITICAL-1)
- Rate limiting: checked 8 auth-sensitive endpoints; 1 unprotected (HIGH-1)
- CORS policy: reviewed middleware; 1 misconfiguration (MEDIUM-2)
- Debug mode: audited prod config files; 1 issue (MEDIUM-1)
- Secrets scan: no API keys/passwords in code
- Dependency audit: `pip-audit` clean

## False Positives Identified + Dismissed

- `src/api/orders.py:50` — dynamically builds table names for `SELECT * FROM {table_name}`; appears injectable but actually whitelisted against hardcoded list of 3 tables in `ALLOWED_TABLES` constant. Reviewed; low risk.

## Coverage Notes

- GenAI/LLM Top 10 N/A — no AI/LLM components in audit scope
- Cryptography review N/A — out of scope (recommend separate audit)
