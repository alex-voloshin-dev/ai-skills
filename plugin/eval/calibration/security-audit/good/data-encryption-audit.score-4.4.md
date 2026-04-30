# Security Audit Report — Data Encryption + Key Management

> Scope: encryption, key-management (per `--scope "encryption,key-management"`)
> Audit standards: OWASP Web Top 10 (2021), OWASP GenAI/LLM Top 10 (2025) — N/A this audit (no LLM components in scope)

## Summary

2 findings: 0 CRITICAL, 1 HIGH, 1 MEDIUM. No show-stoppers; mitigations straightforward.

## Findings

### HIGH-1 — TLS certificate expires without renewal automation
**Category:** OWASP A02:2021 — Cryptographic Failures
**Location:** Kubernetes secret `tls-cert-production` — certificate expires 2026-07-15
**Risk:** When certificate expires, all HTTPS connections fail. Users cannot access the service. If renewal is manual and noticed late, extended outage possible.
**Reproduction:** Check certificate: `openssl x509 -in cert.pem -noout -dates` → shows expiry 2026-07-15 (today is 2026-04-28; 78 days left).
**Threat model:** Operational failure (not malicious attack) → widespread availability outage.
**Severity justification:** likelihood Medium (76 days until expiry; typical renewal window is 30 days before, so this is on track), impact High (service unavailable for all users).
**Mitigation (suggested owner: devops/sre):**
1. Implement cert-manager (Kubernetes cert-manager CRD) with auto-renewal
2. Set up email alerts 30 days before expiry + 7 days before expiry
3. Automated renewal → new certificate deployed to K8s secret
4. Test renewal procedure on staging (not just assume it works)
**Test case:** `test_tls_cert_renewal_automation_active` — verify cert-manager is installed + watching the secret.

### MEDIUM-1 — Database credentials stored in plaintext in config file
**Category:** OWASP A02:2021 — Cryptographic Failures (or A06 depending on interpretation)
**Location:** `config/staging.env` — `DB_PASSWORD=my-staging-password-123`
**Risk:** Repository is readable by all engineers. Credentials are version-controlled and visible in git history forever.
**Severity justification:** likelihood Medium (staged for commit; easy to miss), impact Medium (database access compromise, staging only; production secrets use AWS Secrets Manager).
**Mitigation (suggested owner: devops):**
1. Remove plaintext credentials from repo; use AWS Secrets Manager or similar
2. `.env.example` shows structure without secrets
3. Operators inject secrets at deploy time via CI/CD secret management
4. Rotate staging DB password immediately (assumed compromised)
**Test case:** `test_no_plaintext_secrets_in_config` — grep for password= patterns in config files; should fail if found.

## What Was Checked (transparency)

- TLS/SSL configuration: 1 issue found (HIGH-1)
- Certificate chain: verified 3-chain depth, all valid
- Key storage: checked where keys are stored (Kubernetes secrets + AWS KMS for prod)
- Encryption at rest: MySQL `InnoDB` tablespaces encrypted with AWS KMS key
- Encryption in transit: TLS 1.3 enforced; TLS 1.0/1.1 disabled
- Key rotation policy: documented; annual rotation scheduled
- Config file scan: plaintext passwords flagged (MEDIUM-1)
- SSH key audit: reviewed authorized_keys on jumphost; 2 inactive keys found (already noted in infra backlog)

## False Positives Identified + Dismissed

- `docs/deployment/troubleshooting.md:47` — example showing `DB_PASSWORD=example` for illustration; whitelisted (clearly marked as example, not a real secret).

## Coverage Notes

- GenAI/LLM Top 10 N/A — no AI/LLM components in audit scope
- Hardware security module (HSM) review N/A — out of scope (would be separate audit if HSM used)
