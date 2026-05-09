# Security Scan Rubric

## Overview

Evaluates `/security-scan` — fast dependency + secrets + OWASP Top 10 sweep. Distinct from `/security-audit` (deep, includes GenAI/LLM Top 10). For AI/LLM components, the scan must escalate to `/security-audit` per G3. Six dimensions × five levels.

## Dimensions

### Dimension 1: SCA Coverage
Software-Composition-Analysis tooling appropriate for the stack ran cleanly: `osv-scanner`, `pip-audit`, `npm audit`, `cargo audit`, or equivalent.

- **Level 1:** No dependency scan
- **Level 2:** One tool tried; failed silently
- **Level 3:** One tool ran; results shown without classification
- **Level 4:** Stack-correct tool ran (e.g., osv-scanner for monorepo); results classified by severity
- **Level 5:** All of L4 + cross-checked with a second source (e.g., osv-scanner + GHSA advisory lookup)

### Dimension 2: Secrets Scan
Secrets-scanning tool ran on tracked + git history: `gitleaks`, `trufflehog`, `detect-secrets`, or equivalent. Findings classified (true positive / false positive / placeholder).

- **Level 1:** No secrets scan
- **Level 2:** Tool ran; findings dumped without classification
- **Level 3:** Findings classified; no rotation guidance for true positives
- **Level 4:** Tool ran on tracked + history; findings classified; rotation steps for true positives
- **Level 5:** All of L4 + pre-commit hook proposed to prevent recurrence

### Dimension 3: OWASP Top 10 Review
OWASP Web Top 10 (2021) categories systematically addressed where applicable to the codebase.

- **Level 1:** OWASP not referenced
- **Level 2:** Categories listed; coverage uneven
- **Level 3:** Most categories addressed; one or two skipped silently
- **Level 4:** All ten categories addressed; per-category status (covered / N-A with reason)
- **Level 5:** All of L4 + 2021 version cited explicitly + mapping to specific code locations

### Dimension 4: EPSS / KEV Prioritization
Known-Exploited-Vulnerabilities (CISA KEV) flagged as immediate-action; EPSS ≥ 0.5 marked high priority. Severity is not flat-CVSS only.

- **Level 1:** All findings stamped same severity; no EPSS / KEV
- **Level 2:** CVSS used; KEV / EPSS not consulted
- **Level 3:** KEV checked; EPSS missing
- **Level 4:** KEV-listed CVEs blocked; EPSS ≥ 0.5 marked critical; reachability noted where known
- **Level 5:** All of L4 + reachability analysis (is the vulnerable code path actually called?)

### Dimension 5: SBOM Mention
SBOM generation suggested in CycloneDX or SPDX format via Syft, cdxgen, or equivalent. Not required to generate, but must be flagged for the release pipeline.

- **Level 1:** No SBOM mention
- **Level 2:** SBOM mentioned without format
- **Level 3:** SBOM + format named (CycloneDX or SPDX)
- **Level 4:** SBOM + format + tool (Syft) + integration point (CI / release pipeline)
- **Level 5:** All of L4 + sample command shown; signing (cosign) noted

### Dimension 6: LLM Escalation
For any AI/LLM component (anthropic SDK, openai SDK, langchain, vector DB), escalated to `/security-audit` so the GenAI/LLM Top 10 (2025) is run. G3 boundary.

- **Level 1:** AI/LLM components present; not detected
- **Level 2:** Detected; ignored (no escalation)
- **Level 3:** Detected; escalation suggested as future work
- **Level 4:** Detected; explicit handoff to `/security-audit`; LLM Top 10 categories listed
- **Level 5:** All of L4 + scoped escalation (only the LLM-touching modules) so audit budget stays tight

## Scoring Logic

- **Aggregate:** average of D1–D6
- **Pass threshold:** 4.0
- **Judge model:** Sonnet (security judgment is Sonnet-only baseline per `02-EVAL-FRAMEWORK.md`)

## Anti-Patterns (Auto-Fail)

- LLM components present and `/security-audit` escalation skipped
- All CVEs flagged at same severity with no EPSS / KEV
- No secrets scan attempted
- SBOM never mentioned
- `npm audit` accepted as the sole SCA source for a JS/TS repo (must be cross-checked with osv-scanner or equivalent)

## Calibration Reference

- **Known-good:** `plugin/eval/calibration/security-scan/good/*`
- **Known-bad:** `plugin/eval/calibration/security-scan/bad/*`
