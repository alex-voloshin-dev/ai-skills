# Marketing Rubric

## Overview

Rubric for `/marketing` Phase 2 operations (social-post, blog-post, email, trend-research, analytics, community, strategy-review, content-repurpose). Measures whether the operation aligned with `marketing/MARKETING.md`, used the right delegation, and updated tracking. Grounded in `plugin/skills/marketing/SKILL.md` + `references/abm-playbook.md`.

## Dimensions

### Dimension 1: Strategy Alignment
Operation aligned with `marketing/MARKETING.md` ICP, content pillars, channel strategy. Output references the ICP segment and pillar it serves.

- **Level 1:** No reference to MARKETING.md; generic content
- **Level 2:** ICP mentioned but pillar not identified
- **Level 3:** ICP + pillar identified; channel choice loosely aligned
- **Level 4:** ICP, pillar, channel all match MARKETING.md and decision documented
- **Level 5:** All of L4 + persona-level targeting (named persona from MARKETING.md, not just ICP)

### Dimension 2: Operation Classification
Correctly picked the operation type from the eight Phase 2 entries (social-post / blog-post / email / trend-research / analytics / community / strategy-review / content-repurpose).

- **Level 1:** Wrong operation; e.g. ran social-post when the request was strategy-review
- **Level 2:** Operation matches but cadence wrong (daily op run as monthly artefact)
- **Level 3:** Right operation, correct cadence
- **Level 4:** Right operation + correct cadence + scoped output to that operation only
- **Level 5:** All of L4 + transitions to next operation in calendar (e.g. analytics flags a content-repurpose follow-up)

### Dimension 3: Delegation Discipline
Routes correctly: social-post → `social-media-manager`, blog-post → `/content-creation`, email → `Agent(content-writer)`. Marketing skill never drafts platform-specific copy inline.

- **Level 1:** Drafted platform copy inline (X tweet, blog body) instead of delegating
- **Level 2:** Partial delegation; inline rewrites the delegated output
- **Level 3:** Delegated correctly but didn't pass MARKETING.md context
- **Level 4:** Delegated + passed ICP + pillars + voice context
- **Level 5:** All of L4 + return artefact stored under correct `marketing/` subdir per skill contract

### Dimension 4: Cadence + Measurement
Applied the Measurement Framework at the right level (vanity / engagement / pipeline / revenue). Analytics ops report pipeline + revenue, not just vanity.

- **Level 1:** Vanity metrics only; ignores pipeline + revenue
- **Level 2:** Engagement + vanity; no pipeline tie-in
- **Level 3:** Pipeline metrics surfaced; revenue absent
- **Level 4:** All four levels reviewed; recommendations weight pipeline + revenue
- **Level 5:** All of L4 + delta vs prior period + CAC/LTV trend per channel

### Dimension 5: ABM Awareness
For B2B operations, `references/abm-playbook.md` consulted: intent signals, trigger events, tier classification (Tier 1/2/3). For B2C/self-serve-only, ABM correctly skipped.

- **Level 1:** B2B operation ignores ABM; or B2C operation force-fits ABM
- **Level 2:** ABM mentioned but tier not classified
- **Level 3:** Tier classified; intent signals named generically
- **Level 4:** Tier + named intent stack (Bombora / G2 / 6sense) + trigger event + 7–14 day window
- **Level 5:** All of L4 + per-account orchestration plan with persona threading (5–8 contacts for Tier 1)

### Dimension 6: Content Calendar Update
After operation completes, modified `marketing/content-calendar.md` to mark the entry done, add follow-ups, log strategy implications.

- **Level 1:** No calendar update
- **Level 2:** Calendar mentioned in summary but file not modified
- **Level 3:** Calendar entry marked complete; no follow-ups added
- **Level 4:** Entry marked complete + new follow-ups added + cadence verified
- **Level 5:** All of L4 + MARKETING.md updated when operation reveals strategy implications

## Scoring Logic

- **Aggregate:** average of D1–D6
- **Pass threshold:** 4.0
- **Judge model:** Sonnet (strategy judgement requires reasoning)

## Anti-Patterns (Auto-Fail)

- Drafted X / LinkedIn / Threads post body inline instead of routing to `social-media-manager`
- Edited source code, infra, or non-`marketing/` files
- Analytics report stops at follower count
- ABM-style outreach plan for a pure B2C product
- Strategy-review that re-writes MARKETING.md from scratch instead of diffing against current

## Calibration Reference

- **Known-good:** `plugin/eval/calibration/marketing/good/*`
- **Known-bad:** `plugin/eval/calibration/marketing/bad/*`
