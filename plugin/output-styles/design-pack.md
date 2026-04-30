---
name: design-pack
description: Structured Markdown output style with consistent heading hierarchy for /feature-design artefacts (PRD, ARCHITECTURE, UX-FLOW, DATA-MODEL, RISKS, IMPLEMENTATION-PLAN, REVIEW-LOG). Use when emitting design pack files to <repo>/docs/features/<feature-id>/.
---

# Design Pack Output Style

Output discipline for feature-design artefacts: predictable heading hierarchy, scannable evidence-first sections, paste-ready format for git-versioned docs.

## Universal structure (every artefact)

```
# <Artefact name>

> Feature: <feature-id>
> Date: YYYY-MM-DD
> Author agent: <agent-name>
> Status: draft | reviewed | approved

## Overview
<2-3 sentences summarizing this artefact>

## <Artefact-specific sections — see per-file skeleton below>

## Open Questions
- <question 1 — assigned to: role>
- <question 2 — assigned to: role>

## References
- <link to PRD / ARCHITECTURE / etc. as relevant>
```

## Per-artefact section skeletons

### PRD.md
- Goal & success metrics
- Target users + jobs-to-be-done
- Acceptance criteria (numbered, measurable)
- Non-goals
- Constraints (regulatory, technical, business)

### ARCHITECTURE.md
- System diagram (Mermaid)
- Component responsibilities (table)
- API contracts (OpenAPI snippets or schema)
- Dependencies (internal + external)
- Non-functional requirements (latency, throughput, availability)

### UX-FLOW.md
- User journey (numbered steps with screens)
- Wireframes (Mermaid or descriptions)
- Accessibility notes (WCAG 2.2 AA targets)
- Edge cases (empty states, errors, loading)

### DATA-MODEL.md
- Entity-relationship diagram (Mermaid)
- Schema changes (forward + rollback)
- Data flow (where data originates, transforms, lands)
- Retention & PII considerations

### IMPLEMENTATION-PLAN.md
- Work packages table (WP, role, files, deps, complexity)
- Critical path
- Sequence diagram (Mermaid) for cross-service flows
- Parallelizable work streams

### RISKS.md
- Risk matrix (probability × impact, ranked)
- Per-risk mitigation owner + timeline
- Rollback strategy
- Monitoring & alerting plan

### REVIEW-LOG.md (auto-generated)
- Per-cycle: reviewer verdicts + score deltas + open issues
- Final: rubric score per dimension + pass/fail
- Token totals + agent count per wave

## Hard rules

- **Single literal H1** per file (no clever wordplay).
- **H2 sections phrased as direct topics** (not questions to the reader).
- **Tables for any 2+ entity comparisons.**
- **Mermaid for diagrams** (not ASCII art) — renders in GitHub + most viewers.
- **Open Questions section is mandatory** — list zero items if none, never omit the section.
- **Status field in front-matter block** — drives `/develop` consumption gates.

## Used by

`/feature-design` (8 artefacts in design pack), `/docs-pack` `--template architecture` mode.
