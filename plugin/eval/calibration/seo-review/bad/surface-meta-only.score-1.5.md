# SEO Audit: example.com

## Findings

- Title tag: present, 58 chars (OK)
- Meta description: present, 149 chars (OK)
- H1: present (OK)
- Canonical URL: set (OK)
- Open Graph: present (OK)

## Recommendations

- Title tag could be more keyword-rich
- Meta description could include a CTA

Overall: passes basic SEO.

---

**What's wrong with this output**:

A 7-step audit was requested. This output covered roughly half of step 3c (on-page tags) and stopped. Skipped:

1. **3a Crawlability** — robots.txt, sitemap.xml, internal-link graph
2. **3b Indexability** — duplicate content, canonical conflicts, hreflang errors, indexed-page count vs target
3. **3d Structured data + E-E-A-T** — JSON-LD validity, Person schema with sameAs, dateModified currency, Article/Product/FAQ schema
4. **3e Core Web Vitals + transport** — LCP, INP, CLS measurements; HTTP/3 / TLS 1.3
5. **3f AI Search Readiness** — `llms.txt` presence, schema coverage for AI engines
6. **3g AI Bot Accessibility** — robots.txt allowlist for GPTBot / ClaudeBot / Perplexity-User / Google-Extended; Cloudflare Bot Fight Mode check
7. **3h GEO/AEO** — definition-first opening, FAQ structure, off-site citation portfolio

Title-tag-and-meta-description-only audits made sense in 2010. In 2026 they cover less than 15% of what determines visibility (organic + AI-search). The audit's value is in steps 3d through 3h, which were entirely skipped.
