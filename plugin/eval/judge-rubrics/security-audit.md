# Security Audit Rubric

## Overview

Evaluates `/security-audit` output — OWASP Top 10 (Web 2021) + GenAI/LLM Top 10 (2025) coverage per G3. Six dimensions × five levels. **No effort estimate** is part of audit output (Q2: user/PM owns sizing).

## Dimensions

### Dimension 1: Completeness
All requested `--scope` areas covered; no silent skips.

- **Level 1:** Multiple requested scopes skipped
- **Level 2:** One scope skipped without acknowledgement
- **Level 3:** All scopes touched; some shallow
- **Level 4:** All scopes covered with depth
- **Level 5:** All of L4 + scope-extension recommendations for related areas

### Dimension 2: OWASP Coverage (G3)
OWASP Top 10 Web (2021) categories AND OWASP GenAI/LLM Top 10 (2025) categories systematically addressed where applicable.

- **Level 1:** OWASP not referenced; ad-hoc audit
- **Level 2:** OWASP categories listed; coverage uneven
- **Level 3:** Web Top 10 covered; GenAI Top 10 absent (or vice versa)
- **Level 4:** Both Top 10s covered; per-category status (covered/N-A) documented
- **Level 5:** All of L4 + version of each Top 10 cited (e.g., "OWASP Web Top 10 2021 / OWASP GenAI Top 10 2025")

### Dimension 3: Accuracy
Findings are real issues (not false positives); benign matches identified and dismissed with rationale.

- **Level 1:** Many false positives; report low signal
- **Level 2:** Several false positives; not dismissed
- **Level 3:** Few false positives; dismissed
- **Level 4:** Few false positives; dismissed with rationale
- **Level 5:** All of L4 + false-positive examples shown for transparency

### Dimension 4: Clarity
Each finding explains the risk + impact + reproduction context.

- **Level 1:** Findings cryptic; no context
- **Level 2:** Findings stated; impact missing
- **Level 3:** Risk + impact stated; reproduction unclear
- **Level 4:** Risk + impact + reproduction
- **Level 5:** All of L4 + threat-model context (who can exploit, prerequisites)

### Dimension 5: Prioritization
Severity correctly assessed (CRITICAL > HIGH > MEDIUM > LOW); justification per finding.

- **Level 1:** All findings same severity; no prioritization
- **Level 2:** Severity assigned but unjustified
- **Level 3:** Severity assigned + brief justification
- **Level 4:** Severity assigned + justified per CVSS-like reasoning
- **Level 5:** All of L4 + likelihood × impact matrix shown

### Dimension 6: Remediation Guidance
Mitigations are specific and testable; suggested owner role.

- **Level 1:** No mitigations
- **Level 2:** Mitigations are vague ("improve auth")
- **Level 3:** Mitigations specific; owner suggested
- **Level 4:** Mitigations specific + testable + owner suggested + before-merge gate noted
- **Level 5:** All of L4 + automated test cases proposed for each fix

## Scoring Logic

- **Aggregate:** average of D1–D6
- **Pass threshold:** 4.0
- **Judge model:** Sonnet (security-soundness judgment is Sonnet-only baseline per `02-EVAL-FRAMEWORK.md`)

## Anti-Patterns (Auto-Fail)

- Output INCLUDES effort estimates (per Q2 — user/PM owns sizing; security agent does not)
- CRITICAL finding without immediate-action recommendation
- Hardcoded credentials surfaced but not redacted in the report itself
- GenAI/LLM Top 10 ignored when target includes any AI/LLM component
- "No issues found" verdict without showing what was checked

## Calibration Reference

- **Known-good:** `plugin/eval/calibration/security-audit/good/*`
- **Known-bad:** `plugin/eval/calibration/security-audit/bad/*`
