# Security scan: orders-api (Node.js)

## Step 2: Dependency audit

Stack: Node.js + pnpm. Primary tool: `osv-scanner`.

```bash
$ npx osv-scanner --lockfile=pnpm-lock.yaml -L ./
Scanning dir ./
Found 1247 packages.

Vulnerabilities:
- CVE-2024-21536  high   semver-regex@4.0.5  -- ReDoS
- CVE-2024-37890  high   ws@8.13.0           -- HTTP request smuggling
- CVE-2025-58751  high   axios@1.6.2         -- SSRF
```

## Severity classification (EPSS + KEV)

| CVE | EPSS | KEV? | Tier | Action |
|---|---|---|---|---|
| CVE-2024-21536 | 0.05 | ❌ | Medium | Track; upgrade in next maintenance |
| CVE-2024-37890 | 0.18 | ❌ | High | Fix before next release |
| CVE-2025-58751 | 0.62 | ✅ | **Block** | Fix before merge |

EPSS scores fetched from `https://api.first.org/data/v1/epss?cve=...`; KEV catalogue from CISA.

## Step 3: Secrets scan

```bash
$ gitleaks detect --source . --no-git
0 leaks found
```

## Step 4: OWASP Top 10 — line-level review

Touched in this PR: `src/api/v2/orders.ts`. A01 / A03 / A07 each reviewed against `code-review/security-checklist.md`. No issues.

## Step 5: AI/LLM check

```bash
$ grep -rE "anthropic|openai|langchain" package.json
(no matches)
```

No LLM components detected → /security-audit escalation not needed.

## Recommendation

Block CVE-2025-58751 (axios SSRF, KEV). Fix CVE-2024-37890 before next release. Track the rest.

## Score rationale

osv-scanner used (4), EPSS+KEV applied (5), secrets clean (4), OWASP reviewed at line level (4). Avg 4.0.
