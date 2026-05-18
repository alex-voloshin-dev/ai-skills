# Content Quality Gates, Series Pattern & Memory Writes

Binding detail for the `/content-creation` workflow, moved out of `SKILL.md`
for progressive disclosure. **Behavior is identical to the prior single-file
form — nothing here is optional.** `SKILL.md` instructs you to *Read this file
and apply verbatim* at the quality-gate stage of every content type and before
publishing a series; the instructions below are the enforcement contract.

## Content Quality Gates (apply to every content type)

Eight gates — each must pass before publish:

1. **Accuracy** — claims verifiable, stats cited, pricing/screenshots current, legal claims reviewed
2. **Brand alignment** — voice + tone + terminology per guidelines; no off-brand humor/slang
3. **Conversion** — value prop above-fold, one primary CTA per section, benefits-focused, social proof near decision points
4. **Accessibility** — descriptive alt text, video captions, 4.5:1 contrast, readable at 200% zoom, no color-only meaning
5. **SEO + content sync** — unique title + meta, H1→H2→H3 hierarchy, descriptive internal anchors, structured data, surfaces in sync (`seo-content-sync-checklist.md`)
6. **Legal + ethics** — no fabricated testimonials, no misleading before/after, AI images reviewed for artifacts/bias, attribution for third-party, license compliance, no dark patterns
7. **GEO/AEO structure** (mandatory for public-facing) — macro/meso/micro applied, answer-first, entity consistent, high-leverage formats, schema identified, `geo-content` rule satisfied
8. **Humanization** (mandatory) — `@humanizer` scan; no AI vocabulary, promotional inflation, chatbot artifacts, em-dash overuse, filler/hedging; anti-AI audit; sounds natural read aloud

## Content Series Pattern (blog)

When creating a multi-part series:

1. Plan all parts upfront — titles, topics, order in the brief (Step 2)
2. Cross-link between parts — each post links prev + next
3. Teaser for upcoming parts at end of each
4. Draft all parts before publishing the first — ensures consistency + cross-links work
5. Stagger publishing 3–7 days apart
6. On publish day: update previous part's teaser to real link

## Memory writes

| Layer | When | Shape |
|---|---|---|
| L4 | After draft complete | `.ai-skills-memory/content/<slug>/draft-summary.md` (per piece, for trend tracking) |
| L4 | After publish | Run-log line in `.ai-skills-memory/runs.jsonl` |

Blog post output goes to the project's blog directory (NOT to
`.ai-skills-memory/`) per project conventions.
