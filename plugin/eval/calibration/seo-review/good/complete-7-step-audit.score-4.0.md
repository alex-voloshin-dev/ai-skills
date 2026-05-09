# SEO Audit Report — example.com (full audit)

> Date: 2026-04-30
> Scope: full site (84 pages indexable)
> Role applied: seo-engineer

## Pages Reviewed: 84

## Critical Issues (blocking indexing/ranking)

- [ ] **Cloudflare "AI Scrapers and Crawlers" managed rule active** — 403s GPTBot + ClaudeBot + Perplexity-User in production. Verified via `curl -A "GPTBot" https://example.com/ -I` returning 403. Fix: disable the managed rule OR add explicit allow rules per UA. Delegate: devops-engineer. Verification: re-run `curl -A` per UA expecting 200.
- [ ] **Canonical conflict on `/blog/api-design`** — canonical points to `/blog/api-design-guide` but internal links use `/blog/api-design`. Fix: pick one URL, 301 the other. Delegate: frontend-engineer + devops-engineer.

## High (affecting quality/performance)

- [ ] **INP regression on `/pricing`** — measured 312ms (target < 200ms). Root cause: third-party Calendly widget blocking main thread on hover. Fix: lazy-mount Calendly on click, not on page load. Delegate: frontend-engineer. Verification: PageSpeed re-run.
- [ ] **`Person` schema missing `sameAs` on 14 blog posts** — author byline pages exist but `sameAs` array empty. Fix: populate with LinkedIn + GitHub per author. Delegate: content-writer (data) + frontend-engineer (template).
- [ ] **`dateModified` stale on 9 evergreen posts** — last modified > 6 months. Fix: refresh content + bump `dateModified`. Delegate: content-writer.

## Medium (quality)

- [ ] **`llms.txt` absent** — recommended for AI-search visibility. Fix: generate and serve at `/llms.txt`. Delegate: devops-engineer.
- [ ] **2 sitemap entries return 404** — `/blog/old-post-1` and `/blog/old-post-2`. Fix: remove from sitemap or restore. Delegate: devops-engineer.

## Low (opportunities)

- [ ] **3 blog posts have answer-first opener > 100 words** — exceeds GEO 30-60 target.
- [ ] **TLS 1.2 fallback served when client requests it** — acceptable but consider TLS 1.2 minimum.

## Scores

- Crawlability: OK (robots.txt + sitemap clean apart from 2 stale entries)
- Indexability: 1 canonical conflict
- On-Page SEO: OK
- Structured Data + E-E-A-T: 14 missing `sameAs`, 9 stale `dateModified`
- Core Web Vitals + Mobile + Transport: LCP 1.9s OK, INP 312ms FAIL on /pricing, CLS 0.04 OK; HTTP/3 enabled, TLS 1.3 served, HSTS set
- AI Search Readiness: `llms.txt` missing
- AI Bot Accessibility: 403 on GPTBot, ClaudeBot, Perplexity-User (silent block via Cloudflare managed rule)
- GEO/AEO: schema-vs-visible parity OK; 3 answer-first openers over budget

## All 7 audit sub-steps applied (3a-3h)

3a Crawlability, 3b Indexability, 3c On-Page, 3d Structured Data + E-E-A-T, 3e CWV + Mobile + Transport, 3f AI Search Readiness, 3g AI Bot Accessibility, 3h GEO/AEO. Delegation table populated per fix type.
