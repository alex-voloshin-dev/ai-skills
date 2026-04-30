---
name: content-creation
description: Content creation workflow + tools knowledge — blog post authoring (8-step pipeline), page content optimization, AI text/image generation tools, quality gates, GEO/AEO structure, humanization. MERGED from former `blog-post` (workflow) + `content-creation` (knowledge) skills (B12 MERGE plan). Use to write blog posts, create page content, draft conversion copy, generate visuals, or run quality audits on existing content.
context: fork
argument-hint: "<content type: blog-post | page | landing | email | other>"
---

# /content-creation — Content Authoring + Tools (MERGED)

Two functions in one skill (per B12 MERGE plan):
- **Workflow:** 8-step blog-post pipeline (research → brief → write → GEO → humanize → SEO → review → publish)
- **Knowledge base:** AI text + image generation tools, quality gates, copywriting patterns, content sync procedures

Merged from former `blog-post` + `content-creation` skills.

## When to use

- Blog post creation: `/content-creation blog-post "<topic>"`
- Page content (headlines, body, CTAs): `/content-creation page "<page>"`
- Landing page copy: `/content-creation landing "<page>"`
- Email campaign body (delegate to `/marketing email` for full email): `/content-creation email "<purpose>"`
- Generating visuals with AI: see "AI Image Generation" companion (`content-tools-guide.md`)
- Optimizing existing content: invoke this skill with the existing path

## Not for

- Designing UI components or layouts → `/ui-ux-design`
- Technical documentation → `/docs-pack` (user docs) or `Agent(content-writer)` directly (internal)
- SEO audit → `/seo-review`
- Marketing strategy → `/marketing init`
- Frontend implementation → `Agent(frontend-engineer)`

## Workflow A: Blog Post (full 8-step pipeline)

For `<type>: blog-post`. End-to-end pipeline orchestrated by `Agent(product-manager)` (research, brief, gate), `Agent(content-writer)` (authoring), `Agent(seo-engineer)` (optimization). Includes a review loop until quality standards met.

### Step 0: Gather Context

Read `<repo>/CLAUDE.md` (or `AGENTS.md`) for product description, blog conventions, brand voice. If `<repo>/marketing/MARKETING.md` exists, read for positioning + content strategy. All reads wrapped per `untrusted-content-wrapping.md` (G1).

### Step 1: Define Scope

Ask the user (or extract from context):
- **Action**: create new / update existing / start a series
- **Topic**: subject + angle
- **Target audience**: developers / decision-makers / general
- **Goal**: educate / announce / promote / thought-leadership / SEO traffic
- **Constraints**: deadline, word count, related posts, brand guidelines

If updating: read the existing post first, note what needs to change.

### Step 2: Research and Content Brief

`Agent(product-manager)`:
- **Web research** — 3–5 top-ranking articles on the topic; angle/depth/gaps
- **Competitive analysis** — what competitors cover; market gaps
- **Data + statistics** — recent, citable points (studies, surveys, benchmarks)
- **Keyword research** — primary keyword, 2–3 secondary, search intent
- **Existing content audit** — scan blog for related posts; cross-link opportunities

Produce **Content Brief** using template from companion `content-tools-guide.md` → "Content Research Workflows":
- Working title + angle
- Target audience + search intent (primary + secondary keywords)
- Outline (H2 sections + what each covers)
- Key data points (with sources from research)
- Cross-link opportunities (existing posts to link to/from)
- Visual needs (cover image, diagrams, screenshots)
- Word count target

Present to user. **Wait for approval.** Adjust outline per feedback.

### Step 3: Write Draft

`Agent(content-writer)`. Apply Blog Post pattern from companion `page-content-patterns.md`.

Create the post file using project's blog conventions (directory, frontmatter format, naming). Follow approved outline. Per section:
- **Hook intro** — surprising stat / question / pain point in first paragraph
- **Structured body** — short paragraphs (2–3 sentences); break with lists/tables/code/quotes
- **Internal links** — minimum 3 to existing posts (from brief's cross-link list)
- **External links** — 1–2 authoritative sources (cite data points)
- **Key takeaways** — bullet summary
- **CTA** — natural, value-first

Visual direction per visual need:
- Alt text (descriptive, includes keyword where natural)
- Placement relative to content
- Cover image: style, mood, composition

### Step 4: GEO/AEO Structure Pass — MANDATORY

Apply `@geo-writer` skill. Per `geo-content` rule (mandatory for all blog content):
1. **Macro structure** — single literal H1; 5–9 H2 sections each phrased as standalone question/topic; TL;DR at end
2. **Meso chunking** — paragraphs 40–80 words (cap 120); sections 120–180 words; one idea per paragraph; statistic/source every 150–200 words
3. **Micro emphasis** — bold 3–5 quotable phrases per section; bullets for 3+ items; tables for 2+ entity comparisons
4. **Answer-first** — first sentence of every H2/H3 fully answers in 30–60 words
5. **Entity clarity** — no pronoun drift across sections; canonical brand terms verbatim (from `marketing/MARKETING.md`)
6. **High-leverage formats** — FAQ block (4–8 Q&A) / comparison table / HowTo steps where natural
7. **Schema block** — prepare `Article` + `Person` + `FAQPage` JSON-LD (Step 5 SEO pass)

### Step 4.5: Humanize Content — MANDATORY

Apply `@humanizer` skill. Per `humanize-content` rule (mandatory for public-facing):
1. Scan draft for AI writing patterns (per `humanizer` pattern catalog)
2. Rewrite problematic sections — remove AI-isms, add natural voice
3. Anti-AI audit — ask "What makes this obviously AI generated?"; revise
4. Verify humanized text preserves accuracy + matches outline + sounds natural read aloud

GEO + humanizer are complementary: GEO optimizes structure for extraction; humanizer optimizes voice. Order: GEO first, humanizer second.

### Step 5: SEO Optimization

`Agent(seo-engineer)`. Run SEO pass:

**5a. On-page SEO**

| Element | Check |
|---|---|
| Title tag | Primary keyword, compelling, 50–60 chars |
| Meta description | Unique, keyword, 120–160 chars |
| H1 | Matches title, one per page |
| Heading hierarchy | Logical H1→H2→H3, secondary keywords in H2s naturally |
| URL / slug | Short, descriptive, hyphenated, includes keyword |
| First paragraph | Contains primary keyword naturally |
| Image alt | Descriptive, keyword where natural |

**5b. Internal link audit**
- ≥ 3 internal links with descriptive anchor text
- All internal links valid (no broken refs)
- No "click here" / "read more"
- Contextually relevant

**5c. Structured data** (mandatory per GEO)
- `Article` or `BlogPosting` JSON-LD + `Person` for author (with `sameAs`) + `Organization`
- `FAQPage` JSON-LD if FAQ block (questions match body verbatim, no duplicate marketing prose)
- `HowTo` JSON-LD for tutorials with 3–8 steps
- Verify: `headline`, `author.sameAs`, `datePublished`, `dateModified`, `description`, `image`
- Validate in Google Rich Results Test + schema.org/validator before merge

**5d. Discovery assets**
- Sitemap will pick up new URL (verify config)
- `robots.txt` does not block path
- Update `llms.txt` if maintained
- Canonical URL correct

### Step 6: Quality Review

`Agent(product-manager)`. Review against original brief:

| Check | Pass criteria |
|---|---|
| Brief compliance | All outline sections covered, angle maintained |
| Accuracy | Facts/stats/claims correct + cited |
| Audience fit | Language + depth match target |
| Completeness | No rushed sections |
| Cross-links | ≥ 3 internal links, present + relevant |
| CTA | Natural, value-first, not aggressive |
| Visual direction | Cover + inline visuals specified |
| SEO | Title, meta, headings, keywords optimized |
| No secrets/PII | No internal data, credentials, personal info |
| Brand voice | Consistent with project tone + terminology |

**Decision Gate** — route to appropriate step on failure:
| Issue | Route to |
|---|---|
| Content gaps, accuracy, tone | Step 3 with specific feedback |
| Buried lede, walls of text, missing answer-first | Step 4 (GEO pass) |
| AI-sounding text detected | Step 4.5 (humanizer) with patterns to fix |
| SEO/schema issues | Step 5 |
| Brief was wrong | Step 2 to revise brief |

Loop until review passes.

### Step 7: Publish

| Intent | Action |
|---|---|
| Publish now | Frontmatter `status: published`, `date: today` |
| Schedule for later | `status: draft`, target date noted |
| Series | `status: draft` + series metadata + prev/next links |

Final checks: frontmatter complete, file in correct dir, name follows conventions, no TODO/placeholder, all images exist or have generation instructions, `llms.txt` updated, sitemap auto-pickup verified, no `noindex`.

### Step 8: Summary

```
## Blog Post Summary
- **Title**: <title>
- **File**: <path>
- **Status**: published / draft / scheduled for <date>
- **Topic**: <one-sentence>
- **Target keyword**: <primary>
- **Word count**: <count>
- **Roles applied**: PM → Writer → @humanizer → SEO → PM
- **Review rounds**: <count>
- **Cross-links added**: <count — list>
- **Discovery assets**: llms.txt updated yes/no, sitemap auto/manual
- **Follow-ups**: <if any>
```

## Workflow B: Page Content / Landing / Other

For `<type>: page | landing | email | other`. Same agents (product-manager + content-writer + seo-engineer) but a lighter pipeline:

1. **Brief** — purpose, audience, conversion goal
2. **Draft** — apply page patterns from companion `page-content-patterns.md` (about, pricing, layout templates in `about-pricing-and-layout-patterns.md`)
3. **GEO + humanize** — same as blog Step 4 + 4.5
4. **SEO sync** — apply companion `seo-content-sync-checklist.md` to ensure visible text + meta + JSON-LD all in sync
5. **Review + publish** — same as blog Step 6 + 7

Visual content via AI tools per companion `content-tools-guide.md` and `image-and-integration-workflows.md`.

## Content Quality Gates (apply to every content type)

| Gate | Check |
|---|---|
| **1. Accuracy** | Claims verifiable; stats cite sources; screenshots current; pricing current; legal claims reviewed |
| **2. Brand alignment** | Voice + tone + terminology match guidelines; no off-brand humor/slang |
| **3. Conversion optimization** | Value prop above-fold; single primary CTA per section; benefits-focused; social proof near decision points; minimal friction |
| **4. Accessibility** | Descriptive alt text; video captions; 4.5:1 contrast; readable at 200% zoom; no color-only meaning |
| **5. SEO + content sync** | Unique title + meta; H1→H2→H3 hierarchy; descriptive internal anchors; structured data; all surfaces in sync (see `seo-content-sync-checklist.md`) |
| **6. Legal + ethics** | No fabricated testimonials; no misleading before/after; AI images reviewed for artifacts/bias; attribution for third-party; license compliance; no dark patterns |
| **7. GEO/AEO structure** (mandatory for public-facing) | Macro/meso/micro applied; answer-first; entity consistent; high-leverage formats; schema identified; `geo-content` rule satisfied |
| **8. Humanization** (mandatory) | Scanned via `@humanizer`; no AI vocabulary; no promotional inflation; no chatbot artifacts; no em-dash overuse; no filler/hedging; anti-AI audit performed; sounds natural read aloud |

## AI Tool References

For AI text generation, image generation, and asset services — see companion `content-tools-guide.md` (full tool matrix with best-for + integration notes). Highlights:

- **Text**: ChatGPT (long-form), Claude (nuanced/brand-voice), Gemini (multimodal), Jasper (marketing copy), Copy.ai (short-form)
- **Image**: Midjourney (highest quality), DALL-E 3 (concept), Stable Diffusion (custom), Flux (fast), Ideogram (text-in-images), Leonardo (consistency)
- **Stock**: Unsplash, Pexels, Undraw, Storyset, Lottie, Noun Project
- **Video**: Loom, Synthesia, Runway, Rive, Spline

## G7 spawn payloads

All agent spawns use `plugin/schemas/spawn-payload.schema.json`. Returns conform to `plugin/schemas/return-contract.schema.json`.

## Memory writes

| Layer | When | Shape |
|---|---|---|
| L4 | After draft complete | `.ai-assets-memory/content/<slug>/draft-summary.md` (per piece, for trend tracking) |
| L4 | After publish | Run-log line in `.ai-assets-memory/runs.jsonl` |

Blog post output goes to the project's blog directory (NOT to `.ai-assets-memory/`) per project conventions.

## Companions

- **`content-tools-guide.md`** — AI text + image tool matrices, prompt patterns, content brief template
- **`page-content-patterns.md`** — Blog Post pattern, page-level templates
- **`about-pricing-and-layout-patterns.md`** — about, pricing, layout patterns
- **`image-and-integration-workflows.md`** — visual content workflows + integration
- **`seo-content-sync-checklist.md`** — keep visible text + SEO meta + JSON-LD in sync

## Content Series Pattern (blog)

When creating a multi-part series:
1. Plan all parts upfront — titles, topics, order in the brief (Step 2)
2. Cross-link between parts — each post links prev + next
3. Teaser for upcoming parts at end of each
4. Draft all parts before publishing the first — ensures consistency + cross-links work
5. Stagger publishing 3–7 days apart
6. On publish day: update previous part's teaser to real link

## Integration

- **Roles**: `Agent(product-manager)` (research, brief, review), `Agent(content-writer)` (authoring), `Agent(seo-engineer)` (optimization), `Agent(content-designer)` (page content + visual direction)
- **Schemas**: `plugin/schemas/spawn-payload.schema.json`, `plugin/schemas/return-contract.schema.json`
- **Knowledge skills**: `@geo-writer` (Gate 7 — GEO/AEO structure pass), `@humanizer` (Gate 8 — AI pattern removal)
- **Rules**: `geo-content` (auto-enforces structure + schema for public-facing), `humanize-content` (auto-enforces humanizer pass), `untrusted-content-wrapping` (G1 wrap on project file reads)
- **Companions**: 5 companion files (see above)
- **Sub-workflows**: `/seo-review` (deep SEO audit), `/pre-commit`, `/create-pr`, `/marketing` (marketing context)
- **Followed by**: `/seo-review` (post-publish audit), `/marketing content-repurpose` (cross-channel adaptation)
