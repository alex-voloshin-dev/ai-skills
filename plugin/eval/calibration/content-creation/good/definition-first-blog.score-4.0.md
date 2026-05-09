---
title: "What is server-side rate limiting?"
slug: server-side-rate-limiting
status: published
date: 2026-04-30
dateModified: 2026-04-30
author: jordan-park
tags: [api-reliability, infrastructure]
canonical: https://example.com/blog/server-side-rate-limiting
---

# What is server-side rate limiting?

> Updated 2026-04-30

Server-side rate limiting is a control on a backend service that caps how many requests a client can make over a fixed window — usually expressed as requests per second per API key. It protects upstream resources (databases, third-party APIs, paid LLM endpoints) from runaway traffic, accidental loops, and abuse, and it sits at the edge or in the API gateway so the protected service never sees the excess load.

## When you need it

Three signals say the protection belongs server-side, not client-side: a paid downstream call (LLMs, payment APIs, geocoding), a shared database that a single tenant could starve, or a public endpoint that strangers can hit without auth. If two of those apply, ship the limit before the feature.

## Common algorithms

**Token bucket** — each key holds a bucket of N tokens; each request takes one; tokens refill at R per second. Bursty workloads handle gracefully because the bucket absorbs spikes up to N. This is the default for most public APIs.

**Leaky bucket** — fixed drain rate; excess requests queue or drop. Smooths traffic but rejects bursts that token bucket would accept.

**Sliding window** — tracks a rolling count over the last 60 seconds in Redis. More accurate than fixed windows; slightly heavier on storage.

## FAQ

**How do I pick a per-key limit?** Start with p99 of legitimate traffic plus 50% headroom. Watch the 429 rate for two weeks; tune up if real customers hit it, tune down if abuse leaks through.

**Should I return 429 or 503?** 429 (Too Many Requests). It tells clients to back off; 503 tells them the service is broken.

**What header do I send?** `Retry-After` with seconds, plus `RateLimit-Limit` and `RateLimit-Remaining` per the IETF draft.

---

```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "What is server-side rate limiting?",
  "datePublished": "2026-04-30",
  "dateModified": "2026-04-30",
  "author": {
    "@type": "Person",
    "name": "Jordan Park",
    "sameAs": ["https://linkedin.com/in/jordanpark", "https://github.com/jpark"]
  },
  "mainEntity": {
    "@type": "FAQPage",
    "mainEntity": [
      {"@type": "Question", "name": "How do I pick a per-key limit?", "acceptedAnswer": {"@type": "Answer", "text": "Start with p99 of legitimate traffic plus 50% headroom..."}}
    ]
  }
}
```

## Pipeline notes (for reviewer)

- Steps 1-8 applied (PM brief, writer draft, geo-writer pass, humanizer pass, seo-engineer review, PM gate). Two review rounds.
- Quality Gates 1-8 all checked off.
- Step 8 off-site portfolio: cross-posted summary to r/devops + a YouTube short referencing this URL.
