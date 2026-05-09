# Content Creation Rubric

## Overview

Rubric for `/content-creation` outputs (blog post, page, landing, email). Measures whether the 8-step pipeline was applied end-to-end and the resulting artefact meets the eight Quality Gates. Grounded in `plugin/skills/content-creation/SKILL.md`.

## Dimensions

### Dimension 1: Pipeline Completeness
All 8 steps applied: research → brief → write → GEO → humanize → SEO → review → publish. Roles routed correctly (PM → writer → @humanizer → SEO → PM).

- **Level 1:** Single-pass output; no brief, no GEO, no humanizer; one role end-to-end
- **Level 2:** Brief + draft only; GEO + humanizer skipped
- **Level 3:** Most steps applied; humanizer or SEO step missing
- **Level 4:** All 8 steps applied; correct role routing
- **Level 5:** All of L4 + review-loop iterated and Decision Gate routing documented

### Dimension 2: GEO/AEO Discipline
Definition-first opening (≤80 words), FAQ schema where useful, comparison/HowTo structure for matching intent, off-site portfolio note in Step 8 (Reddit/YouTube/Quora). Anchored in `geo-content` rule.

- **Level 1:** No definition-first; no schema; no high-leverage formats
- **Level 2:** Definition exists but >120 words; schema absent
- **Level 3:** Definition-first present; schema partial (Article only)
- **Level 4:** ≤80-word definition opener + Article + Person + FAQPage/HowTo schema + off-site note in summary
- **Level 5:** All of L4 + comparison table for vs-style intent + cross-link plan back to canonical entity page

### Dimension 3: Humanization
Passes the `@humanizer` audit. No AI vocabulary, sycophancy, em-dash overuse, rule-of-three rhythm, inflated symbolism.

- **Level 1:** Multiple AI tells; reads obviously machine-generated
- **Level 2:** Some AI vocabulary or chatbot artefacts
- **Level 3:** Mostly clean; a few residual phrases
- **Level 4:** No AI vocabulary, no chatbot artefacts; reads natural
- **Level 5:** All of L4 + sentence rhythm varied + concrete imagery + reads aloud well

### Dimension 4: Voice Consistency
Matches brand voice from `marketing/MARKETING.md` (or project CLAUDE.md). No off-tone humour, no slang violating the guide, no terminology drift.

- **Level 1:** Off-brand throughout; ignores MARKETING.md
- **Level 2:** Voice drifts in 2+ sections
- **Level 3:** Voice broadly aligned; terminology slips
- **Level 4:** Voice + terminology + tone consistent with MARKETING.md
- **Level 5:** All of L4 + voice carries personality consistent with team-member byline

### Dimension 5: Quality Gates
Eight gates from SKILL.md applied: accuracy, brand alignment, conversion, accessibility, SEO+sync, legal+ethics, GEO/AEO, humanization. Output documents which gate(s) passed.

- **Level 1:** No gate documentation; obvious gate failures (broken claims, missing alt text)
- **Level 2:** 2–3 gates passed; rest skipped
- **Level 3:** 5–6 gates passed
- **Level 4:** All 8 gates documented as passed
- **Level 5:** All of L4 + each gate cites the artefact line proving compliance

### Dimension 6: Templates Usage
Leveraged `assets/jsonld-templates/` and brand frontmatter from companions. Frontmatter complete (title, slug, status, date, author, tags, canonical).

- **Level 1:** No frontmatter; raw markdown body only
- **Level 2:** Partial frontmatter; no JSON-LD template
- **Level 3:** Frontmatter complete; JSON-LD hand-rolled (not from template)
- **Level 4:** Frontmatter complete + JSON-LD from `assets/jsonld-templates/`
- **Level 5:** All of L4 + canonical URL set + `dateModified` separate from `datePublished`

## Scoring Logic

- **Aggregate:** average of D1–D6
- **Pass threshold:** 4.0
- **Judge model:** Sonnet (multi-dimensional structural + voice judgement)

## Anti-Patterns (Auto-Fail)

- "Click here to learn more" or other placeholder CTA in published copy
- Single 800+ word paragraph with no headings
- Repeated keyword phrase 10+ times in the body (stuffing)
- Definition-first opening longer than 120 words
- No JSON-LD on a published blog post
- Frontmatter missing `status`, `date`, or `slug`

## Calibration Reference

- **Known-good:** `plugin/eval/calibration/content-creation/good/*`
- **Known-bad:** `plugin/eval/calibration/content-creation/bad/*`
