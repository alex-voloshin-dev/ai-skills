# Plan Rubric

## Overview

Evaluates `/plan` output — a per-service / per-role implementation plan derived from a PRD or feature brief. Output is consumed by `/develop`, so handoff fidelity matters. Six dimensions × five levels.

## Dimensions

### Dimension 1: Architecture Grounding
Read `ARCHITECTURE.md` and `CLAUDE.md` (or equivalents) before decomposing. Plan reflects the actual service topology, not a generic template.

- **Level 1:** No architecture read; generic plan
- **Level 2:** Skimmed CLAUDE.md only; missed service boundaries
- **Level 3:** Read both; structure mostly aligned with one inconsistency
- **Level 4:** Read both; plan cites specific services / modules / roles by name
- **Level 5:** All of L4 + flagged architecture gaps the feature exposes (with proposed update)

### Dimension 2: Work-Package Decomposition
Work packages (WPs) carved per service or per role with clear boundaries. Not a flat file-by-file checklist.

- **Level 1:** File-level todo list; no WP structure
- **Level 2:** WPs by feature area but cross-cut services
- **Level 3:** Mostly per-service WPs; one WP entangled
- **Level 4:** Each WP is single-service / single-role; entry+exit interface stated
- **Level 5:** All of L4 + walking-skeleton WP-1 (thinnest end-to-end path) is explicit

### Dimension 3: Dependency Graph
`dependsOn` edges between WPs are correct — no cycles, no missing edges, parallelizable WPs marked.

- **Level 1:** No dependency info
- **Level 2:** Linear list implied as sequential; no graph
- **Level 3:** Graph present; one missing edge or one weak edge
- **Level 4:** Graph correct; cycles absent; parallel branches marked
- **Level 5:** All of L4 + critical-path highlighted; slack on non-critical WPs noted

### Dimension 4: Estimation Methodology
Three-point estimation (best / likely / worst) or story points with a defined scale. Not bare T-shirt sizes without rubric.

- **Level 1:** No estimates, or T-shirt sizes (S/M/L/XL) with no methodology
- **Level 2:** Single-point estimate per WP without methodology
- **Level 3:** Three-point or story points used; methodology implicit
- **Level 4:** Three-point estimates per WP with methodology cited (PERT / Fibonacci with anchors)
- **Level 5:** All of L4 + confidence interval and assumptions per estimate

### Dimension 5: Multi-Reviewer Pass
Product-manager + solution-architect + system-architect feedback was collected and reflected. Conflicts resolved per declared priority order.

- **Level 1:** No reviewer pass; single-author plan
- **Level 2:** One reviewer only
- **Level 3:** Two reviewers; conflicts unresolved
- **Level 4:** All three reviewers; feedback applied; conflicts resolved with rationale
- **Level 5:** All of L4 + REVIEW-LOG with disposition per comment (accepted / declined / deferred)

### Dimension 6: DoR / DoD per WP
Definition of Ready (entry criteria) and Definition of Done (acceptance criteria) explicit per WP.

- **Level 1:** Neither DoR nor DoD per WP
- **Level 2:** DoD only, vague ("works")
- **Level 3:** DoD per WP; DoR missing or implicit
- **Level 4:** DoR + DoD per WP; both objective and testable
- **Level 5:** All of L4 + DoD includes verification commands / test names

## Scoring Logic

- **Aggregate:** average of D1–D6
- **Pass threshold:** 4.0
- **Judge model:** Sonnet (architecture + estimation reasoning)

## Anti-Patterns (Auto-Fail)

- T-shirt sizes only with no methodology
- No reviewer pass at all
- Dependency cycle in the WP graph
- Plan written without reading ARCHITECTURE.md when one exists
- DoD missing on any WP

## Calibration Reference

- **Known-good:** `plugin/eval/calibration/plan/good/*`
- **Known-bad:** `plugin/eval/calibration/plan/bad/*`
