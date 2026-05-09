# Code Review Rubric

## Overview

Evaluates `/code-review` output — line-level review of a diff or PR. Six dimensions × five levels. Distinct from `code-quality.md` (cross-cutting) and `security-audit.md` (full-scope OWASP). Frame: Google eng-practices "improve code health over perfection" + Conventional Comments vocabulary.

## Dimensions

### Dimension 1: Verdict Appropriateness
APPROVE / REQUEST_CHANGES / COMMENT matches actual severity of findings.

- **Level 1:** REQUEST_CHANGES on cosmetic-only finding; or APPROVE despite blocking issue
- **Level 2:** Verdict near the right call but justification weak
- **Level 3:** Verdict matches finding severity; justification stated
- **Level 4:** Verdict + justification + reviewer's confidence level (e.g., "blocking — correctness")
- **Level 5:** All of L4 + cites reviewer-coverage caveat (e.g., "covered: logic; not covered: perf under load")

### Dimension 2: Conventional Comments Vocabulary
Uses `praise:` / `nit:` / `suggestion:` / `issue:` / `question:` / `thought:` / `chore:` plus `(blocking)` / `(non-blocking)` markers.

- **Level 1:** Generic comments ("looks good", "fix this"); no vocabulary
- **Level 2:** Mixes vocabulary with generic prose; tags inconsistent
- **Level 3:** Most comments tagged; blocking/non-blocking indicated
- **Level 4:** Every comment tagged + blocking marker explicit on issue: items
- **Level 5:** All of L4 + uses subject-decoration (e.g., `nit (typo):`) for scannability

### Dimension 3: Eng-Practices Framing
Improves code health over perfection; technical facts over personal preferences.

- **Level 1:** Personal-style demands ("I prefer X"); blocks on subjective taste
- **Level 2:** Mixes facts and preferences without distinction
- **Level 3:** Comments grounded in technical reasoning
- **Level 4:** Reasoning cites a guideline / linter rule / measured cost
- **Level 5:** All of L4 + explicit "code-health-over-perfection" framing on non-blocking suggestions

### Dimension 4: Severity Discipline
Critical / Suggestions / Nits cleanly separated; nits never block merge.

- **Level 1:** All findings same level; or nits flagged as blocking
- **Level 2:** Categories present but boundaries blur
- **Level 3:** Three buckets distinct; nits explicitly non-blocking
- **Level 4:** Buckets ordered + counts shown (e.g., "1 blocking, 2 suggestions, 3 nits")
- **Level 5:** All of L4 + per-bucket merge-policy stated ("nits may be deferred to follow-up")

### Dimension 5: Praise Inclusion
Positive feedback when warranted (per Conventional Comments principle).

- **Level 1:** Zero praise even when code clearly improves on prior state
- **Level 2:** Generic praise ("nice work") without anchoring
- **Level 3:** At least one specific praise: comment
- **Level 4:** Praise tied to a concrete behaviour (e.g., "praise: extracted helper improves testability")
- **Level 5:** All of L4 + praise distributed across reviewers when collaborative

### Dimension 6: Boundary Discipline
Stays at line-level review; defers full audits to the right tool.

- **Level 1:** Runs `npm audit` / OWASP scan inline; goes far beyond diff scope
- **Level 2:** Touches dependency-CVE territory ad-hoc
- **Level 3:** Stays in diff; mentions deferral when warranted
- **Level 4:** Explicitly defers ("dependency CVE belongs in /security-scan; flagging for follow-up")
- **Level 5:** All of L4 + names sibling skill (`/security-scan`, `/security-audit`, `/refactor`) per concern

## Scoring Logic

- **Aggregate:** average of D1–D6
- **Pass threshold:** 4.0
- **Judge model:** Sonnet (review judgement benefits from richer code context)

## Anti-Patterns (Auto-Fail)

- REQUEST_CHANGES verdict for cosmetic-only findings (nits should never block)
- "LGTM" / "looks good" / "ship it" without any technical engagement
- Runs full security audit inline instead of deferring to `/security-scan`
- Personal-style demands without technical justification
- Zero praise on a clearly improving change

## Calibration Reference

- **Known-good:** `plugin/eval/calibration/code-review/good/*`
- **Known-bad:** `plugin/eval/calibration/code-review/bad/*`
