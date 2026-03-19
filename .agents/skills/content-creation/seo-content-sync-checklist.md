# SEO Content Sync Checklist

When updating page content, multiple locations must stay in sync. Missing even one creates inconsistencies between visible text, search engine metadata, and structured data. Use this checklist alongside the `content-creation` skill and related SEO/frontend workflows.

## Content Update Sync Matrix

Every page has multiple content surfaces. When updating messaging on any page, verify ALL surfaces are updated:

### Visible Content
- [ ] Static content file (e.g., `home-content.ts`, `pricing-content.ts`)
- [ ] Component props and hardcoded text in JSX/TSX
- [ ] `<NoScriptContent>` or `<noscript>` fallback text (must match visible content)

### SEO Metadata
- [ ] `metadata` export in `page.tsx` / `layout.tsx` (Next.js) or `<head>` (other frameworks)
  - `title` — matches page headline intent
  - `description` — summarizes visible page content (120–160 chars)
- [ ] OpenGraph metadata (`og:title`, `og:description`, `og:image`)
- [ ] Twitter card metadata (`twitter:title`, `twitter:description`, `twitter:image`)
- [ ] Canonical URL (if page content moved or renamed)

### Structured Data (JSON-LD)
- [ ] All JSON-LD schemas on the page match visible content
- [ ] Schema-specific fields updated:
  - `WebSite` — `name`, `description`
  - `Organization` — `name`, `description`, `sameAs`
  - `Product` / `SoftwareApplication` — `name`, `description`, `offers`
  - `FAQPage` — questions and answers match visible FAQ
  - `HowTo` — steps match visible "How it works" section
  - `BreadcrumbList` — matches actual navigation path

### Content Subsets
- [ ] If page shows a **subset** of a larger content collection (e.g., homepage shows 5 of 20 FAQs), verify:
  - Subset items exist in the full collection
  - Answers are identical in both locations
  - JSON-LD `FAQPage` contains ONLY the questions visible on that page
  - Changes to full collection reflected in subset if applicable

## Page-Specific Sync Patterns

### Homepage
Most complex — typically aggregates content from multiple sources:

| Surface | What to check |
|---|---|
| Hero | Headline, subheadline, CTA text in static content file |
| Features/benefits | Array items, icons, descriptions |
| How it works | Steps array — count, order, descriptions |
| FAQ subset | Must match full FAQ for overlapping questions |
| Testimonials | Quotes, attribution, company names |
| SEO metadata | Title, description, OG, Twitter |
| JSON-LD | WebSite, Organization, FAQPage (homepage subset only), HowTo |

### Product/Feature Pages
| Surface | What to check |
|---|---|
| Product description | Visible text matches `Product` schema `description` |
| Features list | Array items match structured data `featureList` if present |
| Pricing | Visible price matches `offers.price` in JSON-LD |
| SEO metadata | Product-specific title and description |

### FAQ Page
| Surface | What to check |
|---|---|
| Full FAQ content | All categories, all questions |
| JSON-LD FAQPage | Must contain ALL visible questions (not a subset) |
| Homepage FAQ subset | Must be a strict subset of full FAQ |

## Pre-Commit Verification

Before committing content changes, run these checks:

1. **Search for the old text** across the entire `src/` directory to find all locations
2. **Verify JSON-LD** matches visible content — parse and compare programmatically if possible
3. **Check FAQ sync** — if FAQ was modified, verify both homepage subset and full FAQ page
4. **Validate metadata** — title length (50–60 chars), description length (120–160 chars)
5. **Test OG tags** — use browser dev tools or OG preview tools to verify social sharing appearance

## Common Mistakes

| Mistake | Impact | Prevention |
|---|---|---|
| Update visible text but not JSON-LD | Google shows stale structured data | Always search for old text in all files |
| FAQ subset has different answer than full FAQ | Conflicting information on same site | Single source of truth — derive subset from full |
| OG description doesn't match page description | Social shares show wrong content | Update all metadata surfaces together |
| `<noscript>` content outdated | SEO crawlers see stale content | Include in sync checklist |
| JSON-LD FAQPage includes hidden questions | Schema markup doesn't match visible content — Google penalty risk | FAQPage schema must contain ONLY visible questions |

## Integration

- **Recommended ownership**: content design for copy changes, SEO review for metadata and structured data, frontend implementation for code-level updates
- **Skills**: `content-creation` skill (parent skill), `ui-ux-design` skill (visual audit post-change)
- **Workflows**: `/ui-ux-design` (content phase), `/seo-review` (SEO audit), `/pre-commit` (verification)
