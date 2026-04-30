# /security-audit — OWASP-coverage security audit

Comprehensive security scan with OWASP Top 10 (Web 2021) + OWASP GenAI/LLM Top 10 (2025) coverage. Diagnostic + automated fixes for safe issues + remediation plan for the rest.

## When to use

- Pre-release security audit
- Compliance check (SOC 2, ISO 27001, PCI-DSS)
- Threat modeling exercise
- Vulnerability scan after dependency update
- Periodic (quarterly) security health check

## Not for

- Code-review security feedback (line-level) → use `/code-review` with security-checklist
- Penetration testing → use a professional pen-test service
- Production incident response → on-call SRE + `/analyze-prod`

## How to invoke

```bash
/security-audit
/security-audit --scope "secrets,deps,auth" --report-type detailed
/security-audit --scope all --report-type summary
```

| Flag | Default | Effect |
|---|---|---|
| `--scope <areas>` | `all` | `secrets`, `deps`, `auth`, `access-control`, `data-handling`, `crypto`, `infra` (comma-separated) |
| `--report-type` | `summary` | `summary` (1-page exec) or `detailed` (full per-finding analysis) |

## What you get

- `<repo>/.ai-assets-memory/security-audits/<run-id>/SECURITY-REPORT.md` — findings by category with severity (CRITICAL > HIGH > MEDIUM > LOW)
- `<repo>/.ai-assets-memory/security-audits/<run-id>/REMEDIATION-PLAN.md` — per finding: severity, mitigation, suggested owner role
- PR with fixes for automatable issues (dep updates, secret removal from code)
- For CRITICAL: written to `.ai-assets-memory/.committed/security/incidents/<date>.md` (allowlist-validated)

## What's checked

### OWASP Web Top 10 (2021)
1. Broken access control
2. Cryptographic failures
3. Injection
4. Insecure design
5. Security misconfiguration
6. Vulnerable and outdated components
7. Identification and authentication failures
8. Software and data integrity failures
9. Security logging and monitoring failures
10. Server-side request forgery

### OWASP GenAI/LLM Top 10 (2025) — for any AI/LLM component
- LLM01 prompt injection (direct + indirect)
- LLM02 sensitive info disclosure
- LLM03 supply-chain vulnerabilities
- LLM04 data + model poisoning
- LLM05 improper output handling
- LLM06 excessive agency
- LLM07 system prompt leakage
- LLM08 vector + embedding weaknesses
- LLM09 misinformation
- LLM10 unbounded consumption

## The Q2 hard rule — no effort estimates

The audit deliberately produces **no effort estimates** for remediation. Effort is too context-dependent (team velocity, codebase familiarity, dependency on other teams) for a security agent to predict reliably. **You/your PM owns sizing.** The audit gives you findings + mitigations + suggested owner role; you decide priority and effort allocation.

## How it works

`security-engineer` and `devops-engineer` agents work in parallel:
- `security-engineer` — secret scan, dep audit, auth flow, access control, crypto review
- `devops-engineer` — infra security, container scanning, CI/CD security

Lead consolidates → SECURITY-REPORT + REMEDIATION-PLAN. Then `developer` (per stack) fixes automatable issues in a separate PR with explicit user approval.

No RALF — audit is pass-once.

## Common questions

**Why no effort estimates?**
See "Q2 hard rule" above. Security agent doesn't know your team's velocity. Estimates would be hallucination dressed as expertise.

**What's a "false positive"?**
A secret-shaped string in a test fixture, an API doc example, or a commented-out reference. Security-engineer reviews, dismisses with rationale, and whitelists the location for future runs.

**What if a CVE has no fix available?**
Documented in REMEDIATION-PLAN with risk acceptance note + escalation deadline. Workflow doesn't block on un-fixable upstream issues.

**Will this audit my AI/LLM components?**
Yes — if the audit target includes any AI/LLM component (agent harness, prompt template, LLM API integration, RAG pipeline), the GenAI Top 10 IS in scope by default.

**What about authenticated API endpoints?**
Auth flow review covers them. The agent traces login → session → token paths; reviews scopes; flags missing rate limits.

## Examples

### Pre-release full audit
```bash
/security-audit --report-type detailed
```
All scopes; full per-finding analysis. Run before each minor release.

### Dependency-only check after upgrade
```bash
/security-audit --scope deps --report-type summary
```
Fast; ships in a few minutes. Good for post-`npm audit`/post-`pip-audit` follow-up.

### AI/LLM-focused
```bash
/security-audit --scope "data-handling,auth,deps" --report-type detailed
```
Targeted at LLM-feature components. Will explicitly cover LLM Top 10 categories where applicable.

## Related

- `/code-review` (carried) — line-level security feedback
- [`/develop`](develop.md) — implements the remediation PR after audit
- [`/spike`](spike.md) — for threat-modeling exercises that need exploration
- [Memory](../concepts/memory.md) — CRITICAL findings written to `.committed/security/incidents/`
- [Eval](../concepts/eval.md) — `security-audit.md` rubric scores audit quality
