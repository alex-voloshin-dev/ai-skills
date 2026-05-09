# Security scan: search-service — flat CVE list

## Step 2: Dependency audit

```bash
$ npm audit
50 vulnerabilities total
```

| Package | CVE | Severity |
|---|---|---|
| lodash | CVE-2021-23337 | high |
| minimatch | CVE-2022-3517 | high |
| semver | CVE-2022-25883 | high |
| underscore | CVE-2021-23358 | high |
| axios | CVE-2021-3749 | high |
| ... 45 more "high" rows | ... | ... |

Recommend addressing all "high" severity findings before release.

---

**What's wrong with this output**:

1. **No EPSS data**. CVSS "high" alone is not a prioritization signal. EPSS estimates exploitation likelihood over the next 30 days; most CVSS-high CVEs have EPSS < 0.05 (effectively unexploited). A 50-row table with all "high" rated entries forces the team to either fix all 50 (expensive, possibly breaks things) or ignore the report (defeats the scan). Real triage requires EPSS to separate the 2-3 actually-exploited from the 47 latent.
2. **No KEV check**. CISA's Known Exploited Vulnerabilities catalogue lists CVEs confirmed in-the-wild. KEV-listed CVEs trump everything; non-KEV CVEs with EPSS < 0.1 can wait. The output never references KEV.
3. **No reachability assessment**. Many of these CVEs (e.g., lodash prototype-pollution from 2021) require attacker control over a code path the app doesn't expose. Without `osv-scanner --consider-scanning-reachable-only` (or equivalent), the report flags vulnerabilities the app isn't actually exposed to.
4. **No transitive vs direct distinction**. A vulnerability in a transitive dep one used at build-time only (e.g., a build tool) has different risk than one used in production runtime.
5. **All recommended for fix**. With 50 "high" the team will pick none — analysis paralysis.
