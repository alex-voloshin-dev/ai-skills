# Security Review Checklist

Security-focused review checklist. Apply to all changes that touch authentication, authorization, data handling, APIs, infrastructure, or dependencies.

## Authentication & Authorization

- [ ] Authentication is required for all non-public endpoints
- [ ] Authorization checks enforce least-privilege access
- [ ] Session management is secure (expiry, rotation, invalidation)
- [ ] Password handling uses bcrypt/argon2 with proper cost factor
- [ ] Multi-factor authentication flows are correctly implemented
- [ ] OAuth/OIDC flows validate state parameter and redirect URIs
- [ ] API keys and tokens have appropriate scopes and expiry

## Input Validation & Injection

- [ ] All user input is validated on the server side
- [ ] SQL queries use parameterized statements (no string concatenation)
- [ ] NoSQL queries are parameterized (no operator injection)
- [ ] Command execution does not include user-controlled input
- [ ] File paths are sanitized (no path traversal — `../`)
- [ ] XML parsing disables external entities (XXE prevention)
- [ ] HTML output is escaped (XSS prevention)
- [ ] Deserialization uses safe libraries with type restrictions
- [ ] Regular expressions are safe from ReDoS (no catastrophic backtracking)

## Data Protection

- [ ] Sensitive data encrypted at rest (AES-256 or equivalent)
- [ ] TLS 1.2+ enforced for all data in transit
- [ ] PII is not logged, cached unnecessarily, or exposed in errors
- [ ] Secrets are loaded from environment/vault — never hardcoded
- [ ] Database columns with sensitive data have appropriate access controls
- [ ] File uploads are validated (type, size, content) and stored safely
- [ ] Backups are encrypted and access-controlled

## API Security

- [ ] Rate limiting implemented for public endpoints
- [ ] CORS policy is restrictive (specific origins, not `*`)
- [ ] CSRF protection enabled for state-changing operations
- [ ] Response headers include security headers (CSP, HSTS, X-Frame-Options)
- [ ] Error responses do not leak internal details (stack traces, SQL errors)
- [ ] API versioning prevents accidental exposure of deprecated endpoints
- [ ] Request size limits configured to prevent abuse

## Infrastructure & Configuration

- [ ] Default credentials are changed
- [ ] Debug mode is disabled in production
- [ ] Unnecessary ports and services are disabled
- [ ] Container images use minimal base images (distroless/alpine)
- [ ] Kubernetes pods run as non-root with read-only filesystem
- [ ] Network policies restrict pod-to-pod communication
- [ ] Secrets stored in Kubernetes Secrets or external vault (not ConfigMaps)

## Dependencies & Supply Chain

- [ ] No known vulnerabilities in dependencies (check with `npm audit`, `safety`, etc.)
- [ ] Dependencies are pinned to specific versions
- [ ] Lock files are committed and up to date
- [ ] No unnecessary dependencies added
- [ ] Transitive dependencies reviewed for critical updates
- [ ] Container base images are from trusted registries

## Logging & Monitoring

- [ ] Security events are logged (login attempts, authorization failures, config changes)
- [ ] Logs do not contain secrets, tokens, or passwords
- [ ] Alerts configured for suspicious patterns (brute force, privilege escalation)
- [ ] Audit trail maintained for sensitive operations
