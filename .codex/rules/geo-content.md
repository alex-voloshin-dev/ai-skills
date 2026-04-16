
# GEO/AEO Content Standard

Every piece of text intended for public publication and potential AI citation MUST pass through the `geo-writer` skill before finalization.

GEO (Generative Engine Optimization) and AEO (Answer Engine Optimization) are complementary to classic SEO, not replacements. Classic SEO traffic is projected to drop ~25% by end of 2026 as AI engines answer users directly. Content that is not structured for LLM extraction is invisible to the next generation of search.

## Scope

This rule applies to:
- Blog posts and articles
- Landing pages and marketing pages
- Help articles and knowledge base entries
- Glossary and definition pages
- FAQ blocks (standalone or embedded)
- Pillar pages and long-form guides
- Programmatic SEO templates
- Public documentation intended to rank or be cited
- Tutorials and how-to content

This rule does NOT apply to:
- Internal technical documentation (ADRs, design docs, internal READMEs)
- Code comments, docstrings, commit messages, PR descriptions
- Configuration files, AI asset files (rules, skills, workflows)
- UI microcopy (buttons, tooltips, error messages) — this follows the `humanize-content` rule only
- Social media posts — the `social-media-manager` skill owns platform-specific optimization; `geo-writer` applies only to LLM-quotable framing

## Requirements

1. **Apply `geo-writer` before finalization** — structural and schema optimization must happen before the text is presented as ready to publish.
2. **Read `marketing/MARKETING.md`** — use the project's canonical brand terms, category name, metric names, and audience verbatim. Do not invent variants. If absent, ask the user for canonical brand form, category name, and metric names before writing.
3. **Answer-first structure** — the first sentence of every H2/H3 fully answers the implied question in 30-60 words. No preamble.
4. **Macro/meso/micro structure** — single literal H1, 5-9 H2 sections, paragraphs 40-80 words (cap 120), sections 120-180 words, one idea per paragraph, 3-5 bolded quotable phrases per 1,000 words.
5. **Evidence per 150-200 words** — every non-trivial claim needs a statistic with year, named source, or concrete example.
6. **Entity-first, never pronoun-first** — paragraphs name the entity explicitly. No `It`, `This`, `They` referring to entities from earlier sections.
7. **High-leverage formats** — include at least one of: comparison table, FAQ block with matching JSON-LD, HowTo numbered steps, definition + example pairs.
8. **Schema attached** — Organization + Article + Person for articles; FAQPage for any Q&A block; HowTo for tutorials; Product/SoftwareApplication for tool pages; DefinedTerm for glossary. Validate in Rich Results Test and schema.org/validator.
9. **Freshness signals** — `datePublished` and `dateModified` set. Visible `Updated on YYYY-MM-DD` line under H1 on refresh.
10. **Run pre-publish checklist** — see `geo-writer` skill `pre-publish-checklist.md`. Every item must pass or be explicitly waived.

## Pairing with `humanize-content`

`geo-writer` and `humanizer` are complementary and both mandatory for public-facing text. `geo-writer` optimizes structure for extraction. `humanizer` optimizes voice. Run order: draft → `geo-writer` structure pass → `humanizer` voice pass → final checklist.

## Anti-Patterns (always block)

- Burying the lede (`In this post we will explore...`)
- Pronoun drift (paragraphs starting with `It`, `This`, `They` across sections)
- Walls of text (paragraphs over 120 words)
- Opinion without a named source (`Experts say`, `studies show` with no citation)
- Undated statistics
- Terminology drift mid-article
- Duplicate FAQ body + schema
- Missing schema on articles

## Integration

- **Skill**: `geo-writer` (companion resources: `geo-writing-guide.md`, `pre-publish-checklist.md`)
- **Paired rule**: `humanize-content`
- **Brand context source**: `marketing/MARKETING.md` at project root
