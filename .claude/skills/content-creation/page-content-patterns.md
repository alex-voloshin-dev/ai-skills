# Page Content Patterns

Proven content structures for common page types. Use alongside `Agent(content-designer)` role and `content-creation` skill. Each pattern includes section order, content requirements, and conversion elements.

## Landing Page (Product/Service)

### Structure

```
1. HERO
   ├── Headline (value proposition, ≤10 words)
   ├── Subheadline (who + what + why, 1-2 sentences)
   ├── Primary CTA button
   ├── Secondary action (link: "See how it works")
   └── Hero visual (product screenshot or illustration)

2. SOCIAL PROOF BAR
   └── "Trusted by X+ companies" + 5-8 logos (grayscale)

3. PROBLEM STATEMENT
   ├── "The challenge" heading
   ├── 3 pain points with icons
   └── Transition: "There's a better way"

4. SOLUTION / HOW IT WORKS
   ├── 3-step process with numbers + icons
   ├── Each step: title + 1-2 sentence description
   └── Optional: short demo video or animation

5. FEATURES / BENEFITS (3-4 sections)
   ├── Alternating layout: text-left/image-right, then reverse
   ├── Each: benefit headline + 2-3 sentences + visual
   └── Feature → Benefit framing ("AI-powered → Find bugs before users do")

6. SOCIAL PROOF (detailed)
   ├── 2-3 customer testimonials with photo, name, title, company
   ├── Specific results: "Reduced X by Y% in Z months"
   └── Optional: case study link

7. PRICING or COMPARISON
   ├── Clear pricing tiers (if applicable)
   ├── Feature comparison table
   └── FAQ addressing pricing objections

8. FAQ
   ├── 6-8 questions addressing top objections
   ├── JSON-LD structured data for SEO
   └── Expandable accordion format

9. FINAL CTA
   ├── Repeat value proposition (different wording)
   ├── Risk reversal: "Free trial, no credit card required"
   └── Primary CTA button (same as hero)

10. FOOTER
    ├── Navigation links, legal, contact
    └── Trust badges, certifications
```

### Content Requirements

| Section | Word Count | Key Metric |
|---|---|---|
| Hero | 20-40 words | 5-second clarity test |
| Problem | 50-100 words | Resonance with pain |
| Solution | 40-80 words | Simplicity of process |
| Each feature | 30-60 words | Benefit clarity |
| Testimonial | 30-50 words | Specificity of result |
| FAQ answer | 30-80 words | Objection addressed |
| Final CTA | 15-30 words | Urgency + risk reversal |

## SaaS Homepage

### Structure

```
1. HERO
   ├── Category-defining headline
   ├── Subheadline with audience + outcome
   ├── Primary CTA + Secondary CTA
   ├── Product screenshot (real, not mockup)
   └── Optional: animated product demo

2. LOGO BAR
   └── Customer logos + metric ("10,000+ teams trust us")

3. VALUE PILLARS (3 columns)
   ├── Each: icon + headline + 1 sentence
   └── The 3 most important differentiators

4. PRODUCT SHOWCASE (2-3 sections)
   ├── Each section: one key capability
   ├── Real product screenshots with annotations
   ├── Benefit-focused headline
   └── 2-3 supporting bullet points

5. INTEGRATION SECTION
   ├── "Works with your stack" heading
   ├── Integration logos grid
   └── Link to integrations page

6. TESTIMONIALS
   ├── Carousel or grid of customer quotes
   ├── Mix of enterprise + SMB if applicable
   └── Link to case studies page

7. SECURITY / COMPLIANCE (if B2B)
   ├── Certifications (SOC 2, GDPR, ISO 27001)
   ├── Security highlights
   └── Trust badges

8. CTA SECTION
   ├── Two paths: "Start free" + "Talk to sales"
   └── Reassurance: "No credit card required"
```

## Feature Page

### Structure

```
1. HERO
   ├── Feature name as headline
   ├── One-sentence benefit statement
   ├── CTA: "Try [feature]" or "See it in action"
   └── Feature screenshot or demo video

2. PROBLEM → SOLUTION
   ├── "Before [product]" (pain state, old way)
   ├── "With [product]" (solved state, new way)
   └── Visual: before/after comparison or workflow diagram

3. CAPABILITY DETAILS (3-5 sub-features)
   ├── Each: headline + description + screenshot
   ├── Organized by user workflow order
   └── Technical details for informed buyers

4. USE CASES
   ├── 2-3 scenarios showing the feature in context
   ├── "Perfect for..." audience segments
   └── Each with specific example

5. COMPARISON (optional)
   ├── How this feature compares to alternatives
   └── Fair, factual comparison table

6. TESTIMONIAL
   ├── Customer quote specifically about this feature
   └── Specific result attributed to this feature

7. RELATED FEATURES
   ├── Links to complementary features
   └── "Works great with..." section

8. CTA
   ├── Feature-specific call to action
   └── "Start using [feature] today"
```

## Blog Post

### Frontmatter Conventions

Blog post frontmatter varies by framework. Check project's `CLAUDE.md` for the exact format. Common fields:

| Field | Purpose | Example |
|---|---|---|
| `title` | Post title (H1) | `"How to Reduce API Latency by 80%"` |
| `description` | Meta description for SEO | `"Learn practical techniques to..."` |
| `author` | Author name or ID | `"Jane Smith"` |
| `date` / `publishedAt` | Publication date | `2025-01-15` |
| `updatedAt` | Last update date (if revised) | `2025-02-01` |
| `tags` / `categories` | Topic classification | `["performance", "api"]` |
| `image` / `cover` | Cover image path or URL | `"/blog/covers/api-latency.webp"` |
| `status` / `draft` | Publication status | `"published"` / `false` |
| `series` | Series name (if multi-part) | `"API Performance Guide"` |
| `seriesOrder` | Position in series | `1` |

**File naming**: `kebab-case.md` or `kebab-case.mdx` — derived from the URL slug.

### Structure

```
1. TITLE (H1)
   ├── Includes primary keyword naturally
   ├── Specific and compelling (not clickbait)
   └── 50-60 characters for SEO

2. META
   ├── Author, date, reading time
   ├── Category/tags
   └── Featured image with alt text

3. INTRODUCTION (2-3 paragraphs)
   ├── Hook: surprising stat, question, or pain point
   ├── Context: why this topic matters now
   └── Promise: what the reader will learn/gain

4. BODY (multiple H2 sections)
   ├── Each section: one main concept
   ├── Use H3 for sub-sections
   ├── Include: examples, data, screenshots, code blocks
   ├── Short paragraphs (2-3 sentences)
   └── Break up with lists, tables, blockquotes

5. KEY TAKEAWAYS
   ├── Bullet list of 3-5 main points
   └── Scannable summary of the article

6. CTA
   ├── Related to article topic
   ├── Natural: "Want to try this? Start free"
   └── Not aggressive — value-first

7. AUTHOR BIO
   ├── Photo, name, title
   ├── Brief expertise statement
   └── Social links

8. RELATED POSTS
   └── 3 related articles (internal links for SEO)
```

### Blog SEO Checklist

- [ ] Primary keyword in: title, H1, URL, first paragraph, meta description
- [ ] Secondary keywords in H2 headings naturally
- [ ] Internal links to 3+ other pages/posts
- [ ] External links to 1-2 authoritative sources
- [ ] Images with descriptive alt text (include keyword where natural)
- [ ] Meta description: compelling, 120-160 characters
- [ ] URL: short, descriptive, hyphenated

### Cross-Link Audit Checklist

Run this after writing a new blog post:

- [ ] **Outbound links** — minimum 3 internal links to existing blog posts or pages
- [ ] **Inbound links** — update 1-3 existing posts to link back to the new post
- [ ] **Anchor text** — descriptive, keyword-relevant (not "click here" or "read more")
- [ ] **Relevance** — every link is contextually relevant (not forced for SEO)
- [ ] **No orphaned posts** — verify no existing posts lack inbound links after restructuring
- [ ] **Broken link check** — all internal links resolve to valid pages

### Content Series Pattern

For multi-part blog series:

1. **Plan all parts before publishing** — define titles, topics, publish order
2. **Shared series metadata** — each post declares the series name and its position
3. **Navigation between parts**:
   - Link to previous part at the top: "This is Part 2 of [Series Name]. Read [Part 1: Title](/blog/part-1)"
   - Link to next part at the bottom: "Next: [Part 3: Title](/blog/part-3)"
   - For unreleased parts: "Next: Part 3 — [Topic] (coming [date])"
4. **Series landing (optional)** — a summary page linking to all parts
5. **Publishing cadence** — space parts 3-7 days apart
6. **On each publish day**:
   - Update previous part: replace "(coming [date])" with real link
   - Verify all cross-links between series parts work
   - Update series landing page if it exists

### Discovery Assets Checklist

After creating or updating a blog post:

- [ ] **Sitemap** — verify sitemap config auto-includes new blog URLs (check `sitemap.ts`, `sitemap.xml`, or equivalent)
- [ ] **robots.txt** — blog path is not disallowed
- [ ] **llms.txt** — add new post entry (if project maintains llms.txt)
- [ ] **Canonical URL** — set correctly, no duplicate content risk
- [ ] **Structured data** — `BlogPosting` JSON-LD present with `headline`, `author`, `datePublished`, `description`, `image`

## About Page

See [about-pricing-and-layout-patterns.md](about-pricing-and-layout-patterns.md) for about page, pricing page, layout-content rules, and content tone by page type.
