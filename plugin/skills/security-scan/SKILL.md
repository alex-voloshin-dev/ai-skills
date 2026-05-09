---
name: security-scan
description: Security scan workflow — dependency audit, OWASP checklist, secrets scan, vulnerability report. Applies software-engineer role with security focus. Use when auditing a repo for vulnerabilities, before a release or production deploy, when a CVE alert needs investigation, when reviewing a third-party dependency upgrade, or as the security gate inside `/code-review`, `/security-audit`, or `/develop`.
context: fork
argument-hint: "scope or focus area for the scan"
allowed-tools: Read, Grep, Glob, Bash
---

# Security Scan

Automated security audit for the project. Checks dependencies for known vulnerabilities, scans for hardcoded secrets, and reviews code against OWASP guidelines.

## Scope vs `/security-audit`

`security-scan` = lightweight, automated, code- and dependency-layer scan. Runs as a CI / pre-deploy / pre-merge gate.

`/security-audit` = comprehensive periodic audit. Adds threat modeling, OWASP LLM Top 10 (2025) coverage, multi-agent pipeline, REMEDIATION-PLAN doc, committed incident record on CRITICAL.

**If the codebase contains AI / LLM components** (LLM API clients, prompt templates, vector stores, RAG pipelines, agent orchestration), this skill alone is **insufficient**. Escalate to `/security-audit` for OWASP LLM Top 10 (2025) coverage — this is a hard plugin requirement (G3). Detection markers: `import anthropic` / `import openai` / `from langchain` / `from llama_index` / `pinecone` / `weaviate` / `qdrant` SDKs / `tiktoken` / files matching `*prompt*` / `*agent*` / `*llm*`.

## 1. Detect Project Stack

Read `CLAUDE.md` and project config to determine:

- **Language(s)** and dependency managers
- **Infrastructure** (Docker, Kubernetes, Terraform)
- **Existing security tools** (Snyk, Trivy, OWASP dependency-check, etc.)

## 2. Dependency Audit (SCA)

Software Composition Analysis — find known vulnerabilities in third-party dependencies. Distinguished from SAST (static code analysis) and DAST (dynamic / running-app testing).

Run the project's dependency vulnerability scanner. Prefer `osv-scanner` (Google, ecosystem-aware) where possible — it cross-checks the OSV database which is more comprehensive than `npm audit` alone (which over-reports and ignores reachability).

| Stack | Primary command | Alternatives |
|---|---|---|
| Node.js (npm/pnpm/yarn) | `npx osv-scanner --lockfile=package-lock.json` | `npm audit`, `pnpm audit`, `audit-ci` |
| Python (pip/poetry) | `pip-audit` | `safety check`, `osv-scanner --lockfile=poetry.lock` |
| Java (Maven) | `mvn org.owasp:dependency-check-maven:check` | OWASP Dependency-Track, Snyk, Sonatype Lifecycle |
| Java (Gradle) | `gradle dependencyCheckAnalyze` | same |
| Go | `govulncheck ./...` | `osv-scanner` |
| Rust | `cargo audit` | `osv-scanner --lockfile=Cargo.lock` |
| .NET | `dotnet list package --vulnerable` | OWASP Dependency-Check |
| Container image | `trivy image <image>` or `docker scout cves` | `grype <image>` (Anchore) |

Classify findings using **EPSS** (Exploit Prediction Scoring System — likelihood the CVE is exploited in the wild over the next 30 days) and **CISA KEV** (Known Exploited Vulnerabilities catalogue — confirmed in-the-wild exploitation):

| Tier | Criterion | Action |
|---|---|---|
| **Block** | On CISA KEV catalogue | Fix before merge; if no upstream fix available, apply workaround or remove dependency |
| **Critical** | EPSS ≥ 0.5 OR CVSS ≥ 9.0 | Fix before merge |
| **High** | EPSS 0.1–0.5 OR CVSS 7.0–8.9 | Fix before next release |
| **Medium** | EPSS < 0.1 AND CVSS 4.0–6.9 | Track; schedule fix when upgrade available |
| **Low** | CVSS < 4.0 | Note; address in next maintenance cycle |

EPSS data: query `https://api.first.org/data/v1/epss?cve=<CVE-ID>` (free, JSON). KEV catalogue: `https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json`. `grype` consumes both natively when configured.

## 2b. SBOM (Software Bill of Materials)

Generate and verify a CycloneDX or SPDX SBOM. Required for compliance with US Executive Order 14028 and the EU Cyber Resilience Act (CRA, 2024+).

| Tool | Output formats | Notes |
|---|---|---|
| [Syft](https://github.com/anchore/syft) (Anchore) | CycloneDX, SPDX, Syft-JSON | Default choice. `syft <repo-or-image> -o cyclonedx-json` |
| [CycloneDX CLI](https://github.com/CycloneDX/cyclonedx-cli) | CycloneDX | Native CycloneDX validator + merge |
| Language-specific | varies | `cyclonedx-bom` (Python), `cyclonedx-maven-plugin` (Maven), `@cyclonedx/cyclonedx-npm` (npm) |

Once generated, the SBOM is the input for downstream tooling:
- [Grype](https://github.com/anchore/grype) — scans the SBOM against OSV / NVD / GitHub Advisory / KEV
- [Dependency-Track](https://dependencytrack.org) — continuous SBOM monitoring (host-it-yourself)
- [GUAC](https://docs.guac.sh) — graph DB linking SBOMs, attestations, and vulnerability data

## 2c. Build provenance (SLSA)

[SLSA](https://slsa.dev) (Supply-chain Levels for Software Artifacts) attests that an artefact was built from a specific source by a specific builder. Levels 1–4; Level 2 is the practical 2025/2026 baseline.

| SLSA level | Requirement | How to achieve |
|---|---|---|
| L1 | Build process generates provenance | Any CI; record commit + build args |
| L2 | Hosted, tamper-resistant builder + signed provenance | GitHub Actions + [SLSA GitHub Generator](https://github.com/slsa-framework/slsa-github-generator); signed via Sigstore Cosign |
| L3 | Hardened, isolated builder | Reusable workflows; non-falsifiable provenance |
| L4 | Two-party reviewed source + hermetic build | Multi-reviewer-required source repo; reproducible builds |

Generate at release time: see `/release` Step 5 (`git tag -s` + cosign sign-blob). Verify at deploy time: `cosign verify-attestation <image>` before `kubectl apply`. GitHub artifact attestations (`gh attestation verify <artefact>`) are the simplest path for GitHub-hosted projects.

## 3. Secrets Scan

Scan the codebase for hardcoded secrets:

```
// turbo
git log --diff-filter=A --name-only --pretty=format: | sort -u
```

Check for common secret patterns in source files:
- API keys (AWS, GCP, GitHub, Slack)
- Private keys (RSA, EC, SSH)
- Connection strings with credentials
- JWT tokens and bearer tokens
- Passwords in config files

**Tools** (if available):
- `gitleaks detect --source .`
- `trufflehog filesystem .`
- `detect-secrets scan`

## 4. OWASP Top 10 Review

Manual code review against OWASP Top 10 (2021):

| # | Risk | What to Check |
|---|---|---|
| A01 | Broken Access Control | Authorization checks on every endpoint, CORS policy, directory traversal |
| A02 | Cryptographic Failures | TLS enforcement, password hashing, data encryption, no weak algorithms |
| A03 | Injection | SQL/NoSQL/OS command injection, parameterized queries, input validation |
| A04 | Insecure Design | Threat model, rate limiting, business logic flaws |
| A05 | Security Misconfiguration | Default credentials, debug mode, unnecessary features, error messages |
| A06 | Vulnerable Components | Dependency audit results (Step 2) |
| A07 | Auth Failures | Brute force protection, session management, MFA |
| A08 | Data Integrity Failures | CI/CD pipeline security, deserialization, update verification |
| A09 | Logging Failures | Security event logging, no PII in logs, monitoring |
| A10 | SSRF | Server-side request validation, allowlists for external calls |

Use `code-review` skill's `security-checklist.md` for detailed checks.

## 5. Infrastructure Security (if applicable)

### Docker
- Base images from trusted registries
- No `latest` tag — pinned versions
- Non-root user in container
- No secrets in Dockerfile or image layers
- Minimal base image (distroless/alpine)

### Kubernetes
- Pods run as non-root with read-only filesystem
- Network policies restrict traffic
- Secrets in Kubernetes Secrets or external vault
- Resource limits set on all containers
- RBAC follows least-privilege

### Terraform
- No hardcoded credentials in `.tf` files
- State file encrypted and access-controlled
- Security groups follow least-privilege
- Encryption enabled for storage and databases

## 6. Report

```
## Security Scan Report

### Summary
- **Risk level**: LOW / MEDIUM / HIGH / CRITICAL
- **Scan date**: [date]
- **Scope**: [what was scanned]

### Dependency Vulnerabilities
| Package | Current | Fixed In | Severity | CVE |
|---------|---------|----------|----------|-----|
| [pkg]   | [ver]   | [ver]    | [sev]    | [id]|

### Secrets Found
- [ ] [file:line] — [type of secret] — **ACTION: Remove and rotate**

### OWASP Findings
| Risk | Status | Details |
|------|--------|---------|
| A01 Access Control | ✅/❌ | [details] |
| A02 Crypto | ✅/❌ | [details] |
| ... | ... | ... |

### Infrastructure
- Docker: [pass/fail/N/A]
- Kubernetes: [pass/fail/N/A]
- Terraform: [pass/fail/N/A]

### Recommended Actions
1. **Critical**: [action] — [deadline]
2. **High**: [action] — [deadline]
3. **Medium**: [action] — [schedule]
```

## Integration

- **Called by**: `/code-review` (security layer), `/pre-commit` (optional)
- **Escalates to**: `/security-audit` when AI/LLM components are present (LLM Top 10 coverage) or for periodic deep-audit, threat-modeling, compliance framing
- **Roles**: `Agent(software-engineer)` (security focus), `Agent(devops-engineer)` (infra scan), `Agent(devops-architect)` (supply chain security, GHAS, SBOM/SLSA)
- **Skills**: `code-review` skill (security checklist)
