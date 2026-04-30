# GEO/AEO Pre-Publish Checklist

Copy this block into every PR description for a new or rewritten public-facing page. Every item must pass or be explicitly waived in the PR with a justification.

```
## GEO/AEO checklist

### Structure (macro / meso / micro)
- [ ] Single H1 that literally contains the target question or topic
- [ ] 5-9 H2 sections, each phrased as a standalone question or declarative topic
- [ ] First sentence of every H2 fully answers the implied question in 30-60 words
- [ ] Paragraphs ≤ 80 words (hard cap 120)
- [ ] Sections 120-180 words per H2 block
- [ ] One idea per paragraph — no `however` / `but` / `on the other hand` joining unrelated points
- [ ] TL;DR or Key Takeaways section at the end, 3-5 bullet points
- [ ] Table of contents for articles over 1,200 words

### Evidence and entities
- [ ] At least one statistic, named source, or concrete example per 150-200 words
- [ ] All statistics include year and source link
- [ ] 3-5 quotable phrases bolded per 1,000 words
- [ ] Canonical brand terms used verbatim (from `marketing/MARKETING.md`)
- [ ] No pronoun drift — paragraphs name the entity explicitly, never `It`, `This`, `They` across sections
- [ ] Terminology consistent throughout — no synonym cycling mid-article
- [ ] All external entity first-mentions linked to canonical page (Wikipedia, official docs)

### High-leverage formats
- [ ] Comparison table included where 2+ entities compared across 2+ attributes
- [ ] FAQ block present (4-8 Q&A, each 8-20 words, answers 40-80 words self-contained)
- [ ] Numbered steps used for any process with sequential actions
- [ ] Definition + example pairs used for any concept or glossary term

### Schema / JSON-LD
- [ ] Organization + Article + Person schema attached and validated (Rich Results Test + schema.org/validator)
- [ ] FAQPage JSON-LD matches body FAQ verbatim (no duplicate marketing prose)
- [ ] HowTo schema attached for tutorials (3-8 steps)
- [ ] BreadcrumbList schema present on non-homepage URLs
- [ ] Author has dedicated page with Person JSON-LD and `sameAs` → LinkedIn + at least one other platform
- [ ] Visible human-readable author bio on the page

### Cross-linking and discovery
- [ ] Minimum 3 internal links to related pages / glossary terms
- [ ] All internal links are valid (no 404s)
- [ ] Anchor text is descriptive (never `click here` or `read more`)
- [ ] `datePublished` and `dateModified` set
- [ ] Visible "Updated on YYYY-MM-DD" line under H1
- [ ] Canonical URL correct
- [ ] Not blocked by `robots.txt` or `noindex`
- [ ] `llms.txt` updated (if the project maintains one)

### Off-site companion assets (pillar pages)
- [ ] Reddit companion post or thoughtful comment planned
- [ ] YouTube video with descriptive chapters embedded or planned
- [ ] LinkedIn long-form post planned (for B2B)
- [ ] Content calendar entry added (if project maintains one)

### Voice and polish
- [ ] `@humanizer` pass applied
- [ ] No AI-generated filler, shallow `-ing` analyses, inflated symbolism
- [ ] No burying the lede (`In this post we will explore...`)
- [ ] No opinion without a named source (`Experts say...`)
- [ ] No undated statistics
```

## Decision Gate

| Result | Action |
|---|---|
| All boxes checked | Ready to publish |
| Structure items failed | Return to GEO Writer step 2-4 (macro/meso/micro) |
| Evidence items failed | Return to research step — add stats, sources, entities |
| Schema items failed | Attach or fix JSON-LD before merge |
| Voice items failed | Route to `@humanizer` for another pass |
| Off-site companions missing | Acceptable for non-pillar; mandatory for pillar pages |
