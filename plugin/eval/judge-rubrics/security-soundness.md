# Security Soundness Rubric

## Overview

Cross-cutting rubric: code/architecture has no obvious vulnerabilities. Applied to develop, bugfix, refactor, migrate, security-audit. Lighter-weight than `security-audit` (this rubric is a pre-merge gate; the workflow is a deep audit).

## Dimensions

### Dimension 1: Secret Handling
No hardcoded credentials, API keys, tokens, or PII in source.

- **Level 1:** Hardcoded secret committed
- **Level 2:** Secret-shaped string in test fixture without redaction
- **Level 3:** Secrets in env vars; .env in .gitignore
- **Level 4:** Secrets in env vars + secret manager integration documented
- **Level 5:** All of L4 + rotation procedure documented

### Dimension 2: Input Validation
External inputs (HTTP body, CLI args, file contents) validated before use.

- **Level 1:** Inputs trusted blindly; SQL injection / command injection path open
- **Level 2:** Some inputs validated; gaps remain
- **Level 3:** All inputs validated; validation logic centralized
- **Level 4:** All of L3 + validation library used (no ad-hoc regex parsing)
- **Level 5:** All of L4 + property-based tests for validation invariants

### Dimension 3: Auth Enforcement
Endpoints, files, operations check authorization before action.

- **Level 1:** Auth absent on protected operations
- **Level 2:** Auth present but bypassable (predictable IDs, no signature)
- **Level 3:** Auth checks present + correct scope
- **Level 4:** All of L3 + tests verify unauthorized access is denied
- **Level 5:** All of L4 + RBAC matrix documented

### Dimension 4: Dependency Risk
Dependencies are pinned; CVE-scanned; no known-vulnerable versions.

- **Level 1:** Floating versions; old vulnerable deps
- **Level 2:** Pinned but not scanned
- **Level 3:** Pinned + scanned; known CVEs documented as accepted
- **Level 4:** Pinned + scanned + auto-update bot configured
- **Level 5:** All of L4 + dependency graph reviewed for transitive risk

### Dimension 5: Untrusted Content Handling
External content (LLM inputs, user-uploaded files, third-party API responses) treated as untrusted.

- **Level 1:** External content passed directly to executors / sinks
- **Level 2:** External content sanitized for one class of attack (XSS only)
- **Level 3:** External content sanitized + escaped per output context
- **Level 4:** All of L3 + LLM inputs wrapped in `<untrusted_content>` envelope per `untrusted-content-wrapping.md`
- **Level 5:** All of L4 + indirect prompt injection test fixtures cover the surface

## Scoring Logic

- **Aggregate:** average of D1–D5
- **Pass threshold:** 4.0
- **Judge model:** Sonnet (security judgment + LLM-injection awareness)

## Anti-Patterns (Auto-Fail)

- Hardcoded secret in source committed to git
- SQL query built via string concatenation with user input
- Prompt assembled with untrusted text not in `<untrusted_content>` envelope
- `eval()` / `exec()` over untrusted input
- Disabled SSL/TLS verification

## Calibration Reference

- **Known-good:** `plugin/eval/calibration/security-soundness/good/*`
- **Known-bad:** `plugin/eval/calibration/security-soundness/bad/*`
