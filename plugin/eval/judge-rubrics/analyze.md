# Analyze Rubric

## Overview

Evaluates `/analyze` output — structured analysis of codebases, architectures, systems, products, markets, or research topics. Six dimensions × five levels. Distinct from environment-specific diagnostics (`/analyze-local`, `/analyze-prod`, `/env-analyze`) and architectural documentation (`/architecture`).

## Dimensions

### Dimension 1: Framework Selection
Picked appropriate frameworks from `analytical-frameworks.md` (5 Whys, MECE, SWOT, Five Forces, MCDA, JTBD, Fishbone, etc.) for the question type.

- **Level 1:** No framework named or applied; ad-hoc reasoning
- **Level 2:** Framework named but mismatched to question type
- **Level 3:** Appropriate framework named; loosely applied
- **Level 4:** Appropriate framework named + applied with discipline
- **Level 5:** All of L4 + secondary framework cross-checks the primary one (e.g., Fishbone alongside 5 Whys)

### Dimension 2: Evidence Quality
Claims backed by data; citations leverage the evidence-hierarchy (primary > secondary > tertiary; benchmarks > docs > opinion).

- **Level 1:** Claims unsourced; reads as opinion
- **Level 2:** Some claims sourced; many bare assertions
- **Level 3:** Most claims sourced; source quality uneven
- **Level 4:** Most claims sourced + source level (primary/secondary/tertiary) noted
- **Level 5:** All of L4 + counter-evidence considered + assumptions explicit

### Dimension 3: Decomposition (MECE)
Breakdown into investigable sub-questions is Mutually Exclusive and Collectively Exhaustive — no overlap, no gaps.

- **Level 1:** No decomposition; one undifferentiated narrative
- **Level 2:** Sub-questions overlap heavily or leave large gaps
- **Level 3:** MECE-ish decomposition; minor overlap or gaps
- **Level 4:** Clean MECE decomposition; gaps noted explicitly
- **Level 5:** All of L4 + decomposition rationale stated (why this axis, not another)

### Dimension 4: Conclusions vs Evidence
Clearly separates fact / inference / recommendation; states confidence per claim.

- **Level 1:** Facts and recommendations blended; confidence absent
- **Level 2:** Some separation; confidence implicit
- **Level 3:** Separation clear; confidence stated for headline claims only
- **Level 4:** Per-claim labelling (FACT / INFERENCE / REC) + confidence band
- **Level 5:** All of L4 + sensitivity analysis (what would change the conclusion)

### Dimension 5: Output Structure
Clear executive summary + findings + recommendations + risks; readable end-to-end without rereading.

- **Level 1:** No structure; wall of text or scattered bullets
- **Level 2:** Some sections; key parts (summary or risks) missing
- **Level 3:** All key sections present; depth uneven
- **Level 4:** All key sections present + balanced depth + scannable
- **Level 5:** All of L4 + executive summary stands alone (decision-ready in 60s)

### Dimension 6: Boundary Discipline
Defers environment-specific work to `/analyze-local`, `/analyze-prod`, or `/env-analyze`; defers architectural docs to `/architecture`.

- **Level 1:** Pretends to do environment diagnostics or architecture docs inline; ignores boundary
- **Level 2:** Boundary acknowledged but still drifts into out-of-scope work
- **Level 3:** Stays in scope; boundary not explicit
- **Level 4:** Stays in scope + names the right downstream skill for the deferred work
- **Level 5:** All of L4 + handoff payload (what to pass to `/analyze-prod` etc.) drafted

## Scoring Logic

- **Aggregate:** average of D1–D6
- **Pass threshold:** 4.0
- **Judge model:** Sonnet (analytical reasoning judgment is Sonnet-only baseline)

## Anti-Patterns (Auto-Fail)

- Recommendation without comparison or rationale ("use X" without naming alternatives)
- Frameworks referenced but not actually applied (name-dropping)
- Claims about production state without invoking `/analyze-prod` (boundary violation)
- "The whole app" scope without MECE decomposition
- Findings rest on the analyst's opinion alone (no external evidence)

## Calibration Reference

- **Known-good:** `plugin/eval/calibration/analyze/good/*`
- **Known-bad:** `plugin/eval/calibration/analyze/bad/*`
