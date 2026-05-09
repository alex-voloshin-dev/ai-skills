# Security scan: billing-platform (Java + Maven)

## Step 2: Dependency audit

```bash
$ mvn org.owasp:dependency-check-maven:check
[INFO] One or more dependencies were identified with vulnerabilities (CVSS >= 7.0): 6
```

6 dependency CVEs identified.

## Step 3: Secrets scan

```bash
$ gitleaks detect
0 leaks.
```

## Step 4: OWASP Top 10

Reviewed authentication and access control. No findings.

## Step 5: Infrastructure

Dockerfile uses pinned base image. No findings.

Final: 6 dep CVEs. Recommend upgrading.

---

**What's wrong with this output**:

1. **No SBOM generation**. The skill's Step 2b explicitly requires SBOM (CycloneDX or SPDX) generation via Syft. SBOM is now a 2025/2026 supply-chain compliance baseline — required for US EO 14028 federal procurement, EU Cyber Resilience Act, and most enterprise security questionnaires. Output never mentions Syft / CycloneDX / SPDX.
2. **No build provenance / SLSA**. For a billing platform (financial services), SLSA L2 attestations on built artefacts is table-stakes — the build is the supply chain. Skill's Step 2c covers this.
3. **No EPSS / KEV**. Same gap as other bad samples.
4. **OWASP review claimed but not shown**. "Reviewed authentication and access control. No findings" is unverifiable. Real review would cite specific files/lines checked.
5. **Infrastructure check shallow**. "Pinned base image" is one of ~15 things to check (non-root user, read-only filesystem, no secrets in layers, distroless / alpine, .dockerignore correctness, multi-stage build, etc.).
6. **No AI/LLM detection** (skill's Step 0 / boundary).
