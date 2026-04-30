# GEO Readiness Rubric

## Overview

Cross-cutting rubric: public-facing content structured for LLM extraction per `geo-content` rule. Applied to feature-design (public artefacts), docs-pack (public-facing audience), content-creation, marketing.

## Dimensions

### Dimension 1: Answer-First Structure
First sentence of every H2/H3 fully answers the implied question in 30–60 words.

- **Level 1:** Sections open with preamble ("In this section we will explore…")
- **Level 2:** Some sections answer-first; many bury the lede
- **Level 3:** Most sections answer-first; one or two preamble openers
- **Level 4:** Every section answer-first; 30–60 word lead sentences
- **Level 5:** All of L4 + lead sentence is bolded for extraction

### Dimension 2: Entity Clarity
Canonical brand terms used verbatim; no pronoun drift; H2s phrase entities/topics.

- **Level 1:** Pronoun drift across paragraphs ("It does X. They do Y. This is the result.")
- **Level 2:** Some entity inconsistency
- **Level 3:** Entities mostly consistent; minor drift
- **Level 4:** Entities consistent throughout; H2s phrase as entity/topic
- **Level 5:** All of L4 + every external entity first-mention is linked to canonical page

### Dimension 3: Evidence Density
At least one statistic, named source, or concrete example per 150–200 words.

- **Level 1:** Pure assertion; no evidence
- **Level 2:** Sparse evidence
- **Level 3:** Evidence present but not at every section
- **Level 4:** ≥ 1 stat/source/example per 150–200 words
- **Level 5:** All of L4 + each statistic includes year + source link

### Dimension 4: Schema Presence
Schema.org JSON-LD attached for the appropriate types (Article, FAQPage, HowTo, Organization, Person).

- **Level 1:** No schema
- **Level 2:** Minimal schema (Organization only)
- **Level 3:** Article + Person + Organization
- **Level 4:** All of L3 + FAQPage if FAQ block exists OR HowTo if tutorial
- **Level 5:** All of L4 + validates in Google Rich Results Test + schema.org/validator

### Dimension 5: Macro/Meso/Micro Structure
Single literal H1 + 5–9 H2 sections + paragraphs 40–80 words + bolded quotable phrases (3–5 per 1000 words).

- **Level 1:** Walls of text; no clear hierarchy
- **Level 2:** H1 + H2s present; no chunking discipline
- **Level 3:** H1 + 5–9 H2s; paragraph length adequate
- **Level 4:** All of L3 + paragraph length 40–80 words + bolded quotable phrases
- **Level 5:** All of L4 + TL;DR section + comparison table or HowTo where natural

## Scoring Logic

- **Aggregate:** average of D1–D5
- **Pass threshold:** 4.0
- **Judge model:** Haiku (structural pattern matching)

## Anti-Patterns (Auto-Fail)

- "In this post we will explore..." opening
- Pronoun-only paragraph opener for an entity introduced 2+ paragraphs prior
- Statistics without year or source
- Public-facing content without ANY schema
- Paragraph > 120 words

## Calibration Reference

- **Known-good:** `plugin/eval/calibration/geo-readiness/good/*`
- **Known-bad:** `plugin/eval/calibration/geo-readiness/bad/*`
