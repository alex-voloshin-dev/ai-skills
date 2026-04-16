---
description: Optimize public-facing text for GEO/AEO so it is extractable and citable by AI search engines (ChatGPT, Claude, Perplexity, Gemini, Google AI Overviews). Use when writing blog posts, landing pages, help articles, glossary entries, FAQ blocks, pillar guides.
---


# GEO Writer

User-facing workflow that invokes the `geo-writer` skill. Produces public-facing text that is extractable and citable by LLM-based search engines (ChatGPT, Claude, Perplexity, Gemini, Google AI Overviews).

## When to invoke

Use this workflow when writing or editing:
- Blog posts and articles
- Landing pages
- Help articles and knowledge base entries
- Glossary and definition pages
- FAQ blocks
- Pillar pages and long-form guides
- Programmatic SEO templates
- Tutorials and how-to content

## How this workflow works

1. Read `marketing/MARKETING.md` at project root for canonical brand terms, category name, metric names, audience. If absent, ask the user for these before writing.
2. Apply the `geo-writer` skill:
   - Macro structure: single literal H1, 5-9 H2 sections as standalone questions, TL;DR at end
   - Meso chunking: paragraphs 40-80 words (cap 120), sections 120-180 words, one idea per paragraph
   - Micro emphasis: 3-5 bolded quotable phrases per section, bullet lists for 3+ items, tables for 2+ entity comparisons
   - Answer-first template: first sentence of every H2/H3 fully answers the implied question in 30-60 words
   - Evidence: statistic with year, named source, or concrete example every 150-200 words
3. Insert high-leverage formats: FAQ block (4-8 Q&A), comparison table, named stats with year, direct quotes from named experts.
4. Attach JSON-LD schema: Organization + Article + Person for articles; FAQPage for Q&A; HowTo for tutorials; Product/SoftwareApplication for tool pages; DefinedTerm for glossary.
5. Run `humanizer` skill to remove AI-sounding voice patterns.
6. Run pre-publish checklist from `pre-publish-checklist.md`.

## Output format

1. Draft with macro/meso/micro structure applied
2. Checklist pass with every item reported
3. JSON-LD schema block ready to embed
4. Humanizer pass applied before final delivery
5. Follow-ups: off-site companion assets (Reddit / YouTube / LinkedIn) and freshness cadence

## Reference

Full guidance in the `geo-writer` skill (`.windsurf/skills/geo-writer/SKILL.md`) and companion resources:
- `geo-writing-guide.md` — full reference with rationale and sources
- `pre-publish-checklist.md` — copy-ready PR checklist
