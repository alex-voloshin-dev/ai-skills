# Security scan: orders-api

## Step 2: Dependency audit

```bash
$ npm audit
found 23 vulnerabilities (4 low, 12 moderate, 7 high)
```

23 vulnerabilities. Recommend running `npm audit fix --force` to resolve.

Done.

---

**What's wrong with this output**:

1. **`npm audit` over-reports**. It treats every transitive dep as a target, ignoring reachability (whether the vulnerable code path is actually reachable from your code). `osv-scanner --lockfile=package-lock.json` is the modern primary — it cross-checks the OSV database which is more comprehensive and has fewer false positives.
2. **No EPSS / KEV prioritization**. "23 vulnerabilities" is meaningless without knowing which are actually exploitable. KEV-listed CVEs need to be blocked; EPSS ≥ 0.5 is critical; everything else can be batched. The skill explicitly enumerates this prioritization.
3. **`npm audit fix --force` is a footgun**. It can downgrade or upgrade transitive deps to versions that break your runtime. The recommendation should be: identify the specific CVEs that matter, upgrade the specific packages, run tests.
4. **No SBOM mention** (Syft / CycloneDX).
5. **No SLSA / supply-chain awareness**.
6. **No secrets scan** (Step 3).
7. **No OWASP Top 10 review** (Step 4).
8. **No infra security check** (Step 5).
9. **No AI/LLM detection** (Step 0).

Output covers ~10% of what /security-scan is supposed to do.
