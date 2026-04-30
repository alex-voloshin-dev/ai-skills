# Docs Pack Rubric

## Overview

Evaluates `/docs-pack` output — user-facing documentation pack (README, API reference, runbook, examples). Five dimensions × five levels.

## Dimensions

### Dimension 1: Completeness
All key concepts documented per template (api-reference / user-guide / runbook / architecture).

- **Level 1:** Major template sections missing
- **Level 2:** All sections present; several sparse
- **Level 3:** All sections present and adequate
- **Level 4:** All sections present and thorough; covers edge cases
- **Level 5:** All of L4 + index/navigation aids + glossary

### Dimension 2: Clarity
Examples are runnable; explanations are unambiguous.

- **Level 1:** Examples don't run; explanations vague
- **Level 2:** Examples run with hidden setup; explanations need work
- **Level 3:** Examples run; explanations clear with one or two ambiguities
- **Level 4:** Examples runnable + self-contained; explanations precise
- **Level 5:** All of L4 + each example tested + included as a code snippet AND in a tested fixture

### Dimension 3: Accuracy
Documentation matches actual code behavior.

- **Level 1:** Multiple inaccuracies; docs and code disagree
- **Level 2:** One major inaccuracy
- **Level 3:** Minor inaccuracies
- **Level 4:** Accurate; verified by SME
- **Level 5:** Accurate + verified by SME + automated parity check (e.g., docstring-extracted from source)

### Dimension 4: Organization
Logical flow; easy to navigate; correct heading hierarchy.

- **Level 1:** No clear order; mixed concerns per page
- **Level 2:** Some order; weak hierarchy
- **Level 3:** Clear order; H1→H2→H3 hierarchy correct
- **Level 4:** Clear order + cross-links between pages + breadcrumbs
- **Level 5:** All of L4 + landing page maps user journey + per-page TL;DR

### Dimension 5: Style Consistency (and GEO if public-facing)
Follows `docs` skill style guide; for public-facing docs, satisfies `geo-content` rule (passes geo-readiness check separately).

- **Level 1:** Inconsistent voice / formatting / heading style
- **Level 2:** One or two style drifts
- **Level 3:** Consistent style; public-facing docs lack GEO structure
- **Level 4:** Consistent style + public-facing docs pass GEO structure
- **Level 5:** All of L4 + `@humanizer` pass + matching schema attached to public-facing docs

## Scoring Logic

- **Aggregate:** average of D1–D5
- **Pass threshold:** 4.0
- **Judge model:** Haiku default; Sonnet for API references with complex schemas

## Anti-Patterns (Auto-Fail)

- Examples reference functions that don't exist
- "TODO" or placeholder text remaining
- API surface documented as something other than what the code does
- Public-facing docs without `geo-content` compliance
- "How it works" sections that omit the critical setup step

## Calibration Reference

- **Known-good:** `plugin/eval/calibration/docs-pack/good/*`
- **Known-bad:** `plugin/eval/calibration/docs-pack/bad/*`
