# SEO Audit Report — example.com (full audit)

> Date: 2026-04-30
> Scope: full site
> Role applied: seo-engineer

## Pages Reviewed: 84

## Findings

- Title tags: unique on all pages — OK
- Meta descriptions: unique on all pages — OK
- H1: one per page — OK
- robots.txt: includes `User-agent: GPTBot` and `User-agent: ClaudeBot` with `Allow: /` — OK
- sitemap.xml: 84 URLs — OK
- Canonical tags: present — OK
- Article schema: present on blog posts — OK
- LCP: 2.1s — OK
- CLS: 0.05 — OK

## Scores

- Crawlability: OK
- Indexability: OK
- On-Page SEO: OK
- Structured Data: OK
- Core Web Vitals: OK
- AI Search Readiness: OK

## Recommendation
No critical issues found. Site is in good shape for SEO.

## Why this entry exists

Captured as a known-bad sample. Failures:

- **Did not test AI bots end-to-end.** robots.txt allowlist was correct, but Cloudflare "AI Scrapers and Crawlers" managed rule was active and silently 403'd GPTBot, ClaudeBot, Perplexity-User. Audit missed this entirely. `curl -A "GPTBot" https://example.com/ -I` would have returned 403 — never run.
- **No INP measurement.** "Core Web Vitals: OK" with no INP number. INP is the 2026 CWV metric to watch and was never checked.
- **No transport-layer check.** No `curl -I --http3` evidence. HTTP/3, TLS 1.3, HSTS not verified.
- **No `Person` / `sameAs`** structured-data check. E-E-A-T signals untouched.
- **No `llms.txt` check.**
- **No GEO/AEO audit.**
- **No findings prioritized.** "OK / OK / OK" output is not actionable.
- The user shipped to production assuming the audit was clean. AI-search visibility cratered the next month.
