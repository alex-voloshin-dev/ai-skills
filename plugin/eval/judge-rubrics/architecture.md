# Architecture Rubric

## Overview

Evaluates `/architecture` output — architectural documentation produced from a feature PRD, analysis request, or architectural initiative. Six dimensions × five levels. Distinct from `/feature-design` (whole feature pack), `/analyze` (analysis without docs), and `/develop` (implementation).

## Dimensions

### Dimension 1: Scope Identification
Correctly classified the request per Step 4 routing: Feature Design vs Architecture Analysis vs Cloud vs CI/CD vs Evolution. The output shape matches the scope.

- **Level 1:** Wrong scope (e.g., wrote a PRD when an ARD was asked); output shape mismatched
- **Level 2:** Right scope; output shape inconsistent with that scope
- **Level 3:** Right scope; output shape mostly matches
- **Level 4:** Right scope + output shape matches + scope stated explicitly at the top
- **Level 5:** All of L4 + scope-boundary statement (what is in / out of this document)

### Dimension 2: C4 Model Usage
Context + Container diagrams in native Mermaid syntax; Component diagram if scope warrants.

- **Level 1:** No diagrams, or non-Mermaid (image links / ASCII)
- **Level 2:** One diagram present; level confused (mixes Container + Component)
- **Level 3:** Context + Container present in Mermaid; clean separation
- **Level 4:** Context + Container + Component (where scope warrants) all in Mermaid + legend
- **Level 5:** All of L4 + Code-level snippet for the riskiest component + diagram numbering scheme

### Dimension 3: NFR Specification
Non-functional requirements quantified: performance budgets (p50/p99 latency, throughput), RTO/RPO, availability target, scalability ceiling. Not aspirational language.

- **Level 1:** "Should be fast / reliable / scalable" — no numbers
- **Level 2:** One NFR quantified; rest aspirational
- **Level 3:** Most NFRs quantified; some still aspirational
- **Level 4:** All NFRs quantified + measurement method per NFR
- **Level 5:** All of L4 + NFRs traced to a business reason (why p99 must be < 200ms)

### Dimension 4: ADR Discipline
Decisions captured with Context / Decision / Consequences / Alternatives — Nygard or MADR format. Each ADR has a status (proposed / accepted / superseded).

- **Level 1:** Decisions narrated as prose; no ADR structure
- **Level 2:** ADR format named; sections incomplete
- **Level 3:** ADR sections present (Context / Decision / Consequences); Alternatives thin
- **Level 4:** Full Nygard or MADR sections + Status + Date + author
- **Level 5:** All of L4 + linked ADRs (this supersedes #007; this is superseded by #014)

### Dimension 5: Tradeoff Transparency
Alternatives considered with reason for rejection — not advocacy for the chosen option only.

- **Level 1:** Only the chosen option presented; no alternatives
- **Level 2:** Alternatives named; rejected without reason
- **Level 3:** Alternatives named + reason for rejection (one-line)
- **Level 4:** Alternatives + criteria-based comparison (table or matrix) + rejection reason per criterion
- **Level 5:** All of L4 + reversibility note (when would we revisit this decision)

### Dimension 6: Template Usage
Leveraged `assets/{adr,c4-mermaid,nfr,gap-analysis,tech-debt-register}-template.md` rather than re-typing structure from scratch.

- **Level 1:** Templates ignored; structure reinvented (and worse)
- **Level 2:** One template used loosely; rest free-form
- **Level 3:** Most relevant templates used; structure preserved
- **Level 4:** All applicable templates used + cited by path + additions justified
- **Level 5:** All of L4 + template extensions captured back as a proposed template improvement

## Scoring Logic

- **Aggregate:** average of D1–D6
- **Pass threshold:** 4.0
- **Judge model:** Sonnet (architectural soundness judgment is Sonnet-only baseline)

## Anti-Patterns (Auto-Fail)

- ADR written as flowing prose without sections
- "Should be fast and reliable" with no quantified NFR
- Single-option recommendation with no alternatives considered
- C4 diagrams in non-Mermaid format (PNG link, ASCII art)
- Implementation code rather than architectural documentation (scope drift to `/develop`)

## Calibration Reference

- **Known-good:** `plugin/eval/calibration/architecture/good/*`
- **Known-bad:** `plugin/eval/calibration/architecture/bad/*`
