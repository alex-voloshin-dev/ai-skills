# Feature Design Rubric

## Overview

Evaluates the completeness, feasibility, and handoff clarity of a `/feature-design` design pack (PRD + ARCHITECTURE + UX-FLOW + DATA-MODEL + RISKS + IMPLEMENTATION-PLAN + REVIEW-LOG). Six dimensions × five levels.

## Dimensions

### Dimension 1: Completeness
Specification covers business rationale, user stories, technical design, data model, API/UI changes, rollout strategy, success metrics.

- **Level 1:** Missing 3+ major sections (no API design, no rollout)
- **Level 2:** Missing 1–2 major sections (no rollout strategy)
- **Level 3:** All sections present, one is sparse (< 200 words)
- **Level 4:** All sections present and detailed (> 300 words each); rollout thorough
- **Level 5:** Comprehensive; includes decision trade-offs, dependencies, risk mitigation, success criteria

### Dimension 2: Internal Consistency
Statements within the spec don't contradict. Data model aligns with API. Timeline accounts for dependencies.

- **Level 1:** Multiple contradictions (API says required, data model says nullable)
- **Level 2:** One major contradiction (timeline 2 weeks but 3 major dependencies listed)
- **Level 3:** Mostly consistent; one minor discrepancy (field name inconsistency)
- **Level 4:** Fully consistent; explicit timeline accounting
- **Level 5:** Fully consistent with explicit dependency mapping + contingency handling

### Dimension 3: Traceability
Design decisions justified. Trade-offs named and explained. Assumptions stated.

- **Level 1:** No justification; reads as arbitrary
- **Level 2:** Some decisions justified; major trade-offs missing
- **Level 3:** Most decisions justified; trade-offs mentioned but not ranked
- **Level 4:** All major decisions justified; trade-offs ranked by impact; assumptions explicit
- **Level 5:** Justifications evidence-based (metrics, prior experience, standards); trade-offs include cost/benefit quantification

### Dimension 4: Handoff Clarity
Engineer or PM understands implementation steps and acceptance criteria without follow-up questions.

- **Level 1:** Unclear who implements what; no acceptance criteria
- **Level 2:** Implementation roles vague; criteria subjective
- **Level 3:** Steps clear but acceptance criteria loose ("should be fast")
- **Level 4:** Steps numbered; criteria objective ("P99 latency < 100ms")
- **Level 5:** Owner assignments + numbered steps + measurable criteria + explicit definition of done

### Dimension 5: Risk Coverage
Document identifies risks, estimates probability/impact, proposes mitigations.

- **Level 1:** No risk identification
- **Level 2:** 1–2 risks; mitigations vague
- **Level 3:** 3+ risks; each with mitigation (not all realistic)
- **Level 4:** 3+ risks; mitigations specific and realistic; contingency sketched
- **Level 5:** Risks ranked by probability/impact; mitigations detailed with owners + timelines; explicit rollback strategy

### Dimension 6: GEO-Readiness (advisory; only if public-facing)
Public docs structured for LLM extraction per `geo-content` rule.

- **Level 1:** Not applicable (internal doc)
- **Level 2:** Public docs present, not optimized (dense paragraphs, no schema)
- **Level 3:** Clear H2/H3 structure; no schema attached
- **Level 4:** Structure + schema (Organization, Article, DefinedTerm); entity-first phrasing
- **Level 5:** Excellent structure + schema + entity clarity + evidence density (stat per 150 words)

## Scoring Logic

- **Aggregate:** average of D1–D5; D6 advisory (separate score, doesn't affect overall)
- **Pass threshold:** 4.0
- **Judge model:** Haiku for routine designs; Sonnet for novel/complex domains (override in eval case)

## Anti-Patterns (Auto-Fail)

- Placeholder text ("TODO: fill in later")
- No success metrics or acceptance criteria at all
- Zero risks identified
- Mentions specific external product/company names without generalization
- Timeline absent or unrealistic

## Calibration Reference

- **Known-good:** `plugin/eval/calibration/feature-design/good/*` (B10a)
- **Known-bad:** `plugin/eval/calibration/feature-design/bad/*` (B10a)
