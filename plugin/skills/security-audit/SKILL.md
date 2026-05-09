---
name: security-audit
description: Full security scan of codebase and infrastructure — secrets, dependencies, auth, access control, data handling, cryptography, infra. Coverage against OWASP Top 10 (Web 2021) AND OWASP GenAI/LLM Top 10 (2025) per G3. Use for pre-release audit, compliance check, threat modeling. Not for code-review security feedback (use /code-review) or pen testing (use professional service).
context: fork
argument-hint: "[--scope 'secrets,deps,auth,...'] [--report-type summary|detailed]"
---

# /security-audit — OWASP-Coverage Security Audit

Comprehensive security scan with OWASP Top 10 (Web 2021) + OWASP GenAI/LLM Top 10 (2025) coverage. Diagnostic + automated fixes for safe issues + remediation plan for the rest. **No effort estimates** — security agent does not size remediation work; user/PM owns sizing per Q2.

## When to use

- Pre-release security audit
- Compliance check (SOC 2, ISO 27001, PCI-DSS)
- Threat modeling exercise
- Vulnerability scan after dependency update
- Periodic (quarterly) security health check

## Not for

- Code-review security feedback (line-level) → `/code-review` (uses `code-review` skill with security-checklist companion)
- Penetration testing → professional pen-test service
- Production incident response → on-call SRE + `/analyze-prod`

## Invocation

```
/security-audit
/security-audit --scope "secrets,deps,auth" --report-type detailed
/security-audit --scope all --report-type summary
```

## Arguments

| Flag | Default | Effect |
|---|---|---|
| `--scope <areas>` | `all` | Comma-separated: `secrets`, `deps`, `auth`, `access-control`, `data-handling`, `crypto`, `infra` |
| `--report-type` | `summary` | `summary` (1-page exec) or `detailed` (full per-finding analysis) |

## Output

- `<repo>/.ai-assets-memory/security-audits/<run-id>/SECURITY-REPORT.md` — findings by category with severity:
  - Secrets scan (hardcoded creds, API keys) — **CRITICAL** if found
  - Dependency audit (CVE, outdated libs) — **HIGH**
  - Auth review (credentials, sessions) — **MEDIUM**
  - Access control (RBAC, data scoping) — **MEDIUM**
  - Data handling (PII exposure, encryption, logging) — **MEDIUM**
  - Cryptography (algorithm choices, key management) — **MEDIUM**
  - Infrastructure (network policies, TLS, secrets store) — **MEDIUM**
- `<repo>/.ai-assets-memory/security-audits/<run-id>/REMEDIATION-PLAN.md` — per finding: severity, mitigation steps, suggested owner role. **No effort estimate** (Q2)
- Pull request with fixes for automatable issues (dep updates, secret removal from code)

## Agent roster

| Agent | Model | Effort | Tools | Role |
|---|---|---|---|---|
| `security-engineer` | sonnet | high | Read, Grep, Glob, Bash | Main audit; threat modeling; OWASP coverage |
| `devops-engineer` | inherit | high | Bash, Read, Grep | Infrastructure security review |
| `developer` (per-stack) | inherit | medium | Read, Bash, Grep, Write, Edit | Credential/secret removal; code-level fixes for automatable issues |

## Pipeline

```
┌─ Scope parsing: audit --scope areas
│
├─ security-engineer + devops-engineer in parallel:
│  ├─ security-engineer:
│  │  - Grep for secrets (hardcoded keys, tokens, passwords) — see pii-patterns.txt
│  │  - Dependency scan (npm audit, pip check, cargo audit, etc.)
│  │  - Auth flow review (login, session, token, CSRF)
│  │  - Access control review (data scoping, RBAC)
│  │  - Cryptography review (algorithms, key rotation, TLS)
│  │  - Per OWASP coverage matrix below (G3)
│  │  → SECURITY-FINDINGS.md per scope
│  │
│  └─ devops-engineer:
│     - Infrastructure review (network policies, secrets store, TLS)
│     - Container scanning (if Docker)
│     - CI/CD security (secret management, artifact verification)
│     → INFRA-FINDINGS.md
│
├─ Lead consolidates → SECURITY-REPORT.md
│
├─ Lead generates REMEDIATION-PLAN.md:
│  └─ Per finding: severity, mitigation steps, suggested owner role
│     (NO effort estimate — user/PM owns sizing per Q2)
│
└─ developer (if applicable): fix automatable issues in a separate PR:
   - Update dependencies with security patches
   - Remove hardcoded secrets (replace with env-var refs + add to secret store)
   - Add missing security headers (CSP, X-Frame-Options, HSTS)
   Memory write: L4 audit summary; if CRITICAL → committed incident record
```

No RALF — audit is pass-once.

## OWASP coverage (G3)

Eval rubric (`plugin/eval/judge-rubrics/security-audit.md`) MUST verify coverage of:

### OWASP Top 10 Web Application Security Risks (2021 / latest)
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

### OWASP GenAI / LLM Top 10 (2025) — for any AI/LLM component
- LLM01 prompt injection (direct + indirect)
- LLM02 sensitive info disclosure
- LLM03 supply-chain vulnerabilities (model + data)
- LLM04 data + model poisoning
- LLM05 improper output handling
- LLM06 excessive agency
- LLM07 system prompt leakage
- LLM08 vector + embedding weaknesses
- LLM09 misinformation
- LLM10 unbounded consumption

If the audit target includes any AI/LLM component (agent harness, prompt template, LLM API integration, RAG pipeline), the GenAI Top 10 IS in scope by default.

## Methodology — SAST / DAST / SCA / IAST distinction

This audit combines four complementary approaches, each with a different surface:

| Approach | Stage | What it sees | Tools |
|---|---|---|---|
| **SAST** (Static Application Security Testing) | Source code at rest | Pattern-match dangerous APIs, taint paths, hard-coded secrets | Semgrep, CodeQL (GitHub), SonarQube, Snyk Code |
| **DAST** (Dynamic Application Security Testing) | Running application | Real HTTP/API behaviour: injection, auth bypass, header issues | OWASP ZAP, Burp Suite, Nuclei |
| **SCA** (Software Composition Analysis) | Dependencies | Known CVEs in third-party libs and base images | osv-scanner, Snyk, Dependency-Track, Trivy, Grype, Dependabot |
| **IAST** (Interactive AST) | Running app + instrumentation | Runtime data-flow with code context | Contrast Security, Seeker |

The audit's `security-engineer` covers SAST + SCA + secret scanning. DAST is run only when an instance is reachable (typically as a follow-up against staging). IAST is rare in our typical engagements; mention as available but not default.

## Supply chain — SBOM + SLSA + EPSS/KEV

For 2025/2026 compliance baseline:

- **SBOM**: generate with [Syft](https://github.com/anchore/syft) (`syft <repo> -o cyclonedx-json`); consume with [Grype](https://github.com/anchore/grype). [Dependency-Track](https://dependencytrack.org) for continuous monitoring; [GUAC](https://docs.guac.sh) to graph SBOMs + attestations + vulnerabilities.
- **SLSA** ([slsa.dev](https://slsa.dev)): build-provenance attestation. Level 2 is the practical baseline. GitHub Actions + [SLSA GitHub Generator](https://github.com/slsa-framework/slsa-github-generator) reach L2 with minimal config.
- **Sigstore Cosign**: sign release artefacts (`cosign sign-blob`); verify at deploy (`cosign verify-attestation <image>`).
- **EPSS** (Exploit Prediction Scoring System) + **CISA KEV** (Known Exploited Vulnerabilities): use to prioritize SCA findings — KEV-listed CVEs are confirmed in-the-wild; EPSS ≥ 0.5 indicates high near-term exploitation likelihood. Both gate "must fix before merge". Free APIs at first.org/data and CISA. `grype` consumes both natively.
- **EO 14028** (US, 2021) and **EU Cyber Resilience Act** (2024+) both mandate SBOMs for software shipped to government / EU markets.

Cite the v2025 OWASP LLM PDF: [genai.owasp.org/llm-top-10/](https://genai.owasp.org/llm-top-10/) for traceability.

## G7 spawn payloads

All spawns use structured G7 payloads. `security-engineer` is read-only by frontmatter (`disallowedTools: Write, Edit`); developer fixes happen in a separate phase with explicit user approval.

## Eval rubric

Pointer: `plugin/eval/judge-rubrics/security-audit.md` (B10).

Dimensions:
1. **Completeness** — all requested scopes covered
2. **OWASP coverage** — Top 10 Web + GenAI Top 10 systematically addressed where applicable
3. **Accuracy** — findings are real issues, not false positives
4. **Clarity** — each finding explains the risk and impact
5. **Prioritization** — severity correctly assessed (CRITICAL > HIGH > MEDIUM > LOW)
6. **Remediation guidance** — mitigations are specific and testable

Pass: avg ≥ 4.0, no dimension < 3.

## Memory writes

| Layer | When | Shape |
|---|---|---|
| L4 | After audit complete | `.ai-assets-memory/security-audits/<run-id>/findings.json` — structured findings (for trend tracking) |
| L4 (committed) | If CRITICAL severity found | `.ai-assets-memory/.committed/security/incidents/<date>.md` — critical finding + immediate action taken |

`pre-tool-use-committed-write.py` hook enforces `.committed/security/incidents/*.md` matches allowlist.

## Failure modes

- **False positive (e.g., secret string in test fixture comment):** security-engineer reviews, confirms, removes from report if benign — but ALWAYS documents the false-positive review trail
- **Dependency CVE has no fix available:** documented in REMEDIATION-PLAN with risk acceptance note + escalation deadline
- **Auth flow too complex to audit in one pass:** security-engineer flags as needs-deeper-review; recommends threat-modeling session via `/spike`

## Observability events

- `workflow_start` — security-audit + scope
- `finding_identified` (per finding + severity)
- `automatable_fix_applied` (per fix in developer phase)
- `workflow_end` — `COMPLETE` with critical/high/medium/low counts

## Integration

- **Orchestrator**: `feature-design-lead`
- **Primary agent**: `security-engineer` (the B5 agent — read-only, OWASP-aware)
- **Schemas**: `plugin/schemas/spawn-payload.schema.json`, `plugin/schemas/return-contract.schema.json`
- **Sub-workflow**: developer fix phase uses `/develop` for the remediation PR
- **Companions**: `/subagent-spawn`, `/context-load`
- **Rules**: `subagent-isolation`, `untrusted-content-wrapping` (CRITICAL — audit reads project files which may have hostile content), `memory-discipline` (CRITICAL incidents → committed)
- **Hooks**: `pre-tool-use-committed-write.py` (enforces incident allowlist), `tool-output-normalize.py` (G2 on `npm audit` / `pip check` / `cargo audit` outputs)
- **Templates**: `plugin/hooks/scripts/pii-patterns.txt` (secret-pattern source)
