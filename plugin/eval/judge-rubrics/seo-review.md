# SEO Review Rubric

## Overview

Rubric for `/seo-review` audit outputs. Measures whether the 7-step audit covered crawlability, indexability, on-page, structured data + E-E-A-T, Core Web Vitals + transport, AI bot accessibility, AI search readiness, and GEO/AEO. Grounded in `plugin/skills/seo-review/SKILL.md`.

## Dimensions

### Dimension 1: Crawlability + Indexability
Checked `robots.txt`, sitemap, canonical tags, meta tags (`noindex` accidents), 200 status codes, SSR/SSG of critical content.

- **Level 1:** Skipped crawlability/indexability; no `robots.txt` or sitemap reference
- **Level 2:** `robots.txt` checked; sitemap and canonical skipped
- **Level 3:** robots + sitemap + canonical reviewed; soft-404 + SSR check missing
- **Level 4:** Full 3a + 3b coverage including soft-404 and SSR check for critical content
- **Level 5:** All of L4 + crawl-trap audit (URL params, calendar widgets) + redirect-chain inventory

### Dimension 2: Structured Data + E-E-A-T
JSON-LD validates in Rich Results Test. `Person` schema with `sameAs` on every blog post. `dateModified` current (rolling 6-month freshness window). Author byline pages crawlable.

- **Level 1:** No structured-data check
- **Level 2:** Article schema only; Person + sameAs missing
- **Level 3:** Article + Person present; sameAs incomplete or `dateModified` stale
- **Level 4:** Full schema set + `sameAs` on author + `dateModified` current + Rich Results pass
- **Level 5:** All of L4 + Organization schema reinforces publisher trust on byline page

### Dimension 3: Core Web Vitals + Transport
LCP < 2.5s, INP < 200ms, CLS < 0.1 measured per page. HTTP/3 + TLS 1.3 + HSTS verified at the edge.

- **Level 1:** No CWV numbers; no transport check
- **Level 2:** LCP only; INP and CLS skipped
- **Level 3:** All three CWV measured; transport (HTTP/3 / TLS / HSTS) skipped
- **Level 4:** All three CWV measured + HTTP/3 + TLS 1.3 + HSTS verified with `curl -I` evidence
- **Level 5:** All of L4 + INP root-cause traced to a specific JS interaction or third-party

### Dimension 4: AI Bot Accessibility
`robots.txt` allowlist verified for GPTBot, ClaudeBot, Perplexity-User, Google-Extended, OAI-SearchBot, Applebot-Extended, CCBot, meta-externalagent. CDN/WAF caveat applied (Cloudflare Bot Fight Mode, AI Scrapers managed rule). 200-vs-403 verified per UA.

- **Level 1:** AI bots not checked
- **Level 2:** `robots.txt` listed but no edge-layer (WAF) verification
- **Level 3:** `robots.txt` allowlist correct; WAF only spot-checked
- **Level 4:** Full allowlist + Cloudflare/Akamai/Fastly check + per-UA `curl -A` 200/403 evidence
- **Level 5:** All of L4 + identified silent-block rule by name (e.g. "AI Scrapers and Crawlers" managed rule) and recommended specific allow rule

### Dimension 5: AI Search Readiness + GEO/AEO
`llms.txt` present (recommended for ChatGPT/Claude/Perplexity surfacing). GEO/AEO structure audited: schema mirrors visible text, answer-first H2/H3, macro/meso/micro chunking, entity clarity, high-leverage formats (FAQ / comparison / HowTo).

- **Level 1:** No `llms.txt` check; no GEO audit
- **Level 2:** `llms.txt` checked; GEO audit absent
- **Level 3:** `llms.txt` + answer-first audit; schema-vs-visible-text mismatch unflagged
- **Level 4:** Full 3f + 3h coverage; schema-vs-visible parity verified
- **Level 5:** All of L4 + freshness window per pillar verified + citation-readiness scored

### Dimension 6: Findings Prioritized
Output sorts findings into Critical / High / Medium / Low (or equivalent) with concrete fixes per finding (file path, line, exact change). Delegation routing (frontend / content / devops) documented.

- **Level 1:** Findings listed without priority; no fixes proposed
- **Level 2:** Priority labels but vague fixes ("improve performance")
- **Level 3:** Priority + concrete fix per finding; delegation absent
- **Level 4:** Priority + concrete fix + delegated to correct role per fix type
- **Level 5:** All of L4 + verification step listed per fix (re-run Rich Results Test, re-`curl -A`)

## Scoring Logic

- **Aggregate:** average of D1–D6
- **Pass threshold:** 4.0
- **Judge model:** Sonnet (multi-dimensional technical audit)

## Anti-Patterns (Auto-Fail)

- "Mobile Optimization" listed as a separate audit section (mobile-first is universal in 2026 — folds into CWV)
- Surface-only audit: only checked title and meta description
- AI bot allowlist verified in `robots.txt` only, with no WAF/edge-layer check
- Cloudflare Bot Fight Mode silently 403'ing GPTBot and missed in the audit
- No JSON-LD validation against Rich Results Test
- Findings list without priority

## Calibration Reference

- **Known-good:** `plugin/eval/calibration/seo-review/good/*`
- **Known-bad:** `plugin/eval/calibration/seo-review/bad/*`
