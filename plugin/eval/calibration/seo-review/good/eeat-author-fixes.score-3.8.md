# SEO Audit Report — example.com/blog (E-E-A-T author signals)

> Date: 2026-04-29
> Scope: blog section (62 posts)
> Role applied: seo-engineer
> Audit type: structured data + E-E-A-T

## Pages Reviewed: 62

## Critical Issues

- [ ] **`Person` schema missing entirely on 41 of 62 blog posts** — Article schema present, author absent. Fix: add `Person` block to JSON-LD per post template. Delegate: frontend-engineer.

## High

- [ ] **`sameAs` array empty on 21 posts** — Person block present but no external profile links. Without sameAs, search engines can't disambiguate the author. Fix: populate per author (LinkedIn, GitHub, X, personal site). Delegate: content-writer (data gathering) + frontend-engineer (template).

  Example fix for posts by Priya Rao:
  ```json
  "author": {
    "@type": "Person",
    "name": "Priya Rao",
    "url": "https://example.com/authors/priya-rao",
    "sameAs": [
      "https://linkedin.com/in/priyarao",
      "https://github.com/priyarao",
      "https://x.com/priyarao_dev"
    ]
  }
  ```

- [ ] **`dateModified` matches `datePublished` on 38 posts** — implies content has never been refreshed. Six are evergreen pillar posts that should rotate within a 6-month window. Fix: review and refresh, then bump `dateModified` independently. Delegate: content-writer.

- [ ] **Author byline page `/authors/priya-rao` returns `noindex`** — accidentally blocked. Fix: remove `noindex` meta. Delegate: frontend-engineer.

## Medium

- [ ] **`Organization` schema absent from author byline pages** — recommended to reinforce publisher trust. Fix: add `Organization` block to byline template. Delegate: frontend-engineer.

- [ ] **3 author byline pages have only 1 post listed** — thin author signal. Recommend grouping low-volume authors under a "Guest contributors" page or seeding more posts.

## Verification per fix

- After fixes land, re-run [Rich Results Test](https://search.google.com/test/rich-results) on a sample of 5 posts.
- Confirm Person + Organization both validate.
- Spot-check 3 author byline pages return 200, not 404 or 403, and serve indexable HTML.

## Scores

- Structured Data + E-E-A-T: 41 posts missing Person, 21 missing sameAs, 38 with stale dateModified, 1 byline noindex'd
- Other dimensions: out of scope for this audit (separate full audit Q3)

## Sub-steps applied
3d only (audit type was scoped to structured data + E-E-A-T per user request).
