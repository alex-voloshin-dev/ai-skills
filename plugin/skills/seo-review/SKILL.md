---
name: seo-review
description: SEO review workflow — technical SEO audit, meta tags, structured data validation, Core Web Vitals, crawlability, indexability, AI search readiness. Applies SEO Engineer role. Use when auditing a public-facing page or site for search visibility, before publishing a marketing or blog page, when traffic drops or indexing issues are suspected, when validating JSON-LD / Open Graph / canonical / sitemap setup, or as the SEO gate inside `/content-creation` and `/docs-pack`.
argument-hint: "URL or page path"
---

<!-- ARCHITECTURAL NOTE: no `context: fork`. This skill spawns `Agent(seo-engineer)` for review steps. Subagents cannot spawn other subagents (per Anthropic docs), so this skill MUST run in the main thread to retain spawn capability. -->

# SEO Review

Systematic SEO audit for public-facing pages. Checks crawlability, indexability, on-page SEO, structured data, Core Web Vitals, and AI search readiness. Applies `Agent(seo-engineer)` for all steps.

Works standalone or as a sub-workflow called by `/docs`, `/feature-dev`, or `/bugfix`.

## 1. Define Scope

Ask the user (or extract from parent workflow):

- **Target pages**: Specific URLs, page group, or entire site
- **Environment**: Local dev / staging / production
- **Review type**: Full audit / metadata only / structured data / performance / AI search
- **Constraints**: What must not change (URL structure, navigation, etc.)

## 2. Apply Roles

Apply `Agent(seo-engineer)` as primary role.

If implementation changes are needed, delegate to:

| Change Type | Delegate To |
|---|---|
| Frontend code (meta tags, JSON-LD, components) | `Agent(frontend-engineer)` |
| Content / copy improvements | `Agent(content-writer)` |
| Server config (redirects, headers, robots.txt) | `Agent(devops-engineer)` |
| Architecture changes (URL structure, routing) | `Agent(solution-architect)` |

## 3. Baseline Audit

Run automated checks before making changes.

### 3a. Crawlability

Check the following (read project files or use browser/curl):

- `robots.txt` — allows important pages, `Sitemap:` directive present
- XML sitemap — includes all indexable pages, excludes non-indexable
- No orphaned pages (all pages reachable via internal links)
- Navigation uses crawlable `<a href>` links
- No crawl traps (infinite URL parameters, calendar widgets)

### 3b. Indexability

- No accidental `noindex` on public pages
- Canonical tags point to correct URLs
- No canonical conflicts (canonical vs redirects vs internal links)
- Pages return 200 status codes (check for soft 404s)
- Critical content rendered server-side (SSR/SSG), not client-only

### 3c. On-Page SEO

For each target page:

| Element | Check |
|---|---|
| Title tag | Unique, descriptive, matches page intent |
| Meta description | Unique, compelling, relevant |
| H1 | Exactly one per page, matches topic |
| Heading hierarchy | Logical H1→H2→H3 |
| Image alt text | Descriptive for all meaningful images |
| Internal links | Present, descriptive anchor text |
| Outbound links | Qualified with `rel` attributes where needed |

### 3d. Structured Data + E-E-A-T Author Signals

- JSON-LD present where applicable:
  - `Organization` / `WebSite` on homepage
  - `Article` / `BlogPosting` on blog posts
  - `BreadcrumbList` for navigation
  - `FAQ` where genuinely useful
  - `Product`, `Review`, `HowTo` where applicable
- Structured data matches visible page content (no misleading markup)
- Validate with [Rich Results Test](https://search.google.com/test/rich-results)

E-E-A-T author signals (Experience, Expertise, Authoritativeness, Trustworthiness — see [Google's helpful content guidance](https://developers.google.com/search/docs/fundamentals/creating-helpful-content)):

- `Person` schema on every blog post with `sameAs` linking to author's LinkedIn, Wikipedia, personal site, or X profile
- `dateModified` current — refresh evergreen content within rolling 6 months
- Author byline pages exist, are crawlable (not `noindex`), and link from each post
- `Organization` schema on author pages reinforces publisher trust

### 3e. Core Web Vitals + Mobile + Modern Transport

Mobile-first indexing is universal in 2026 — mobile checks fold into CWV.

| Metric | Target | Tool |
|---|---|---|
| LCP (Largest Contentful Paint) | < 2.5s | PageSpeed Insights |
| INP (Interaction to Next Paint) | < 200ms | PageSpeed Insights |
| CLS (Cumulative Layout Shift) | < 0.1 | PageSpeed Insights |

Mobile rendering:

- Responsive across viewports, no horizontal scroll
- Tap targets ≥ 48×48px, body font ≥ 16px
- No intrusive interstitials

Modern transport baseline (verify with `curl -I --http3` or browser devtools):

- HTTP/3 (QUIC) enabled at the edge
- TLS 1.3 served (TLS 1.2 acceptable as fallback; 1.0/1.1 disabled)
- HSTS header set on production hostnames

### 3f. AI Search Readiness

- Pages crawlable and well-structured (SSR/SSG, semantic HTML)
- Content is clear, factual, and authoritative
- Structured data present and accurate
- `llms.txt` present — recommended for AI-search visibility as an active discovery signal for AI engines (format: [llmstxt.org](https://llmstxt.org/)). Google still does not honor it, but ChatGPT, Claude, and Perplexity surface it.
- Pages indexed and snippet-eligible (prerequisite for AI features)

### 3g. AI Bot Accessibility

The most-broken 2026 SEO/GEO surface: AI crawlers silently 403'd by CDN/WAF rules. Verify `robots.txt` allows current AI bots and that the edge layer (Cloudflare, Akamai, Fastly) is not blocking them.

Required `robots.txt` allowlist:

```
User-agent: GPTBot
User-agent: ClaudeBot
User-agent: Perplexity-User
User-agent: Google-Extended
User-agent: OAI-SearchBot
User-agent: Applebot-Extended
User-agent: CCBot
User-agent: meta-externalagent
Allow: /
```

CDN/WAF check — Cloudflare "Bot Fight Mode" and the "AI Scrapers and Crawlers" managed rule are the most common silent blockers. Either disable the rule or add explicit allow rules per AI bot UA string.

Verify each bot returns 200, not 403:

```bash
curl -A "GPTBot" https://example.com/ -I
curl -A "ClaudeBot" https://example.com/ -I
curl -A "Perplexity-User" https://example.com/ -I
curl -A "Google-Extended" https://example.com/ -I
```

Bot UA references (sources change — re-check on audit):

- OpenAI GPTBot — [platform.openai.com/docs/bots](https://platform.openai.com/docs/bots)
- Anthropic ClaudeBot — [docs.anthropic.com/en/docs/agents-and-tools/web-search-tool/bot-info](https://docs.anthropic.com/en/docs/agents-and-tools/web-search-tool/bot-info)
- Google-Extended — [developers.google.com/search/docs/crawling-indexing/overview-google-crawlers](https://developers.google.com/search/docs/crawling-indexing/overview-google-crawlers)
- Perplexity — [docs.perplexity.ai/guides/bots](https://docs.perplexity.ai/guides/bots)

### 3h. GEO/AEO Audit

Apply `@geo-writer` skill to audit extractability for AI engines (ChatGPT, Claude, Perplexity, Gemini, Google AI Overviews):

- **Schema coverage** — `Article` or `BlogPosting` + `Person` with `sameAs` + `Organization` on blog pages; `FAQPage` where FAQ present; `HowTo` for tutorials; `Product` / `Review` on commercial pages. JSON-LD must mirror visible text (no marketing-only prose in schema).
- **Answer-first structure** — each H2/H3 opens with a self-contained 30-60 word answer. No buried ledes.
- **Macro/meso/micro chunking** — single H1, 5-9 H2 sections phrased as questions or topics, paragraphs 40-80 words, bold anchors every section.
- **Entity clarity** — canonical brand terms used verbatim, no pronoun drift, entity mentions in first 100 words.
- **High-leverage formats** — FAQ blocks (4-8 Q&A), comparison tables (2+ entities), HowTo steps (3-8 numbered actions) where natural.
- **Freshness signals** — `dateModified` present and recent; `datePublished` set; content updated within the pillar's freshness window.
- **Citation-ready** — stats/claims attributed to named sources with outbound links where appropriate.

The `geo-content` rule enforces these for public-facing text. Use `pre-publish-checklist.md` from `@geo-writer` for the full checklist.

## 4. Present Findings

Compile audit results:

```
## SEO Audit Report

### Pages Reviewed: [count]

### Critical Issues (blocking indexing/ranking)
- [ ] [issue] — [affected page] — [fix]

### Warnings (affecting quality/performance)
- [ ] [issue] — [affected page] — [fix]

### Opportunities (improvements)
- [ ] [opportunity] — [affected page] — [recommendation]

### Scores
- Crawlability: [OK / issues found]
- Indexability: [OK / issues found]
- On-Page SEO: [OK / issues found]
- Structured Data + E-E-A-T: [OK / missing / errors]
- Core Web Vitals + Mobile + Transport: [LCP: Xs, INP: Xms, CLS: X.XX, HTTP/3: y/n, TLS 1.3: y/n]
- AI Search Readiness: [OK / opportunities]
- AI Bot Accessibility: [200 per bot / 403 found on: bot list]
- GEO/AEO: [OK / opportunities]
```

Wait for user to review and approve which fixes to implement.

## 5. Implement Fixes

For approved fixes:

1. **Metadata changes** (title, description, OG tags) — implement directly or delegate to `Agent(frontend-engineer)`
2. **Structured data** (JSON-LD) — implement directly or delegate to `Agent(frontend-engineer)`
3. **Content changes** — delegate to `Agent(content-writer)`
4. **Server config** (redirects, headers) — delegate to `Agent(devops-engineer)`
5. **Performance fixes** (image optimization, lazy loading, critical CSS) — delegate to `Agent(frontend-engineer)`

Follow `Agent(seo-engineer)` standards for all changes. No black-hat techniques.

## 6. Verify

Re-run relevant checks from Step 3 for changed pages:

- [ ] Fixed issues no longer present
- [ ] No new issues introduced
- [ ] Structured data validates (Rich Results Test)
- [ ] Pages still indexable (no accidental noindex)
- [ ] Core Web Vitals within targets
- [ ] No broken links introduced

## 7. Summary

```
## SEO Review Summary
- **Scope**: [pages/environment reviewed]
- **Issues found**: [critical: X, warnings: X, opportunities: X]
- **Fixes applied**:
  - [fix 1] — [page]
  - [fix 2] — [page]
- **Delegated to**: [roles involved]
- **Verification**: [pass/fail per check]
- **Monitoring**: [what to watch — Search Console, PageSpeed, etc.]
- **Follow-ups**: [items for future attention]
```

## Integration

- **Roles**: `Agent(seo-engineer)` (primary), `Agent(frontend-engineer)` (implementation), `Agent(content-writer)` (content fixes)
- **Skills**: `@geo-writer` (GEO/AEO audit — step 3h), `@humanizer` (applied when content fixes are needed)
- **Rules**: `geo-content` (enforces GEO structure and schema on public-facing text), `humanize-content` (enforces humanizer pass)
- **Called by**: `/feature-dev` (SEO-relevant features), `/docs` (public content)
