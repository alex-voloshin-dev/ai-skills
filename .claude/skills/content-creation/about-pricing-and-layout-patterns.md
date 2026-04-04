# About, Pricing, and Layout Patterns

Companion to `page-content-patterns.md`. Covers about page, pricing page, layout-content rules (grid symmetry, content-component alignment), and content tone guidance by page type.

## About Page

### Structure

```
1. HERO
   ├── Mission statement or brand story headline
   ├── Subheadline: what the company does and why
   └── Team photo or brand illustration

2. STORY
   ├── Origin: why the company was founded
   ├── Problem observed → solution built
   └── Authentic, specific, not generic

3. MISSION / VALUES
   ├── 3-5 core values with descriptions
   └── Show, don't tell: examples of values in action

4. TEAM
   ├── Key team members with photos, names, roles
   ├── Brief bios (expertise + human element)
   └── Link to careers page

5. NUMBERS
   ├── Key metrics: customers, team size, funding, uptime
   └── Presented as visual callouts

6. PARTNERS / INVESTORS (if applicable)
   └── Logos with brief context

7. CTA
   ├── "Join us" (careers) or "Get in touch"
   └── Matches likely visitor intent
```

## Pricing Page

### Structure

```
1. HEADER
   ├── Clear headline: "Simple, transparent pricing"
   ├── Toggle: monthly / annual (show savings)
   └── Optional: "Start free, upgrade anytime"

2. PRICING TIERS (2-4 tiers)
   ├── Each tier: name, price, description, feature list, CTA
   ├── Highlight recommended tier visually
   ├── Feature list: checkmarks for included, dashes for excluded
   └── CTA text varies: "Start free" / "Get started" / "Contact sales"

3. FEATURE COMPARISON TABLE
   ├── Detailed feature-by-feature comparison
   ├── Grouped by category
   └── Tooltips for feature explanations

4. FAQ
   ├── Billing questions: refunds, upgrades, downgrades
   ├── Feature questions: limits, overages
   └── 6-8 questions addressing pricing objections

5. SOCIAL PROOF
   ├── Customer quote about value/ROI
   └── "Trusted by X+ companies" with logos

6. ENTERPRISE
   ├── "Need more?" section for enterprise
   └── "Contact sales" CTA with benefits list

7. GUARANTEE
   ├── Money-back guarantee or free trial details
   └── Risk reversal: reduce purchase anxiety
```

## Layout-Content Rules

### Grid Symmetry

When defining card/item arrays for grid layouts, item count must be a multiple of the column count to avoid orphaned items or unbalanced rows:

| Grid Columns | CSS Class (Tailwind) | Valid Item Counts |
|---|---|---|
| 2-column | `md:grid-cols-2` | 2, 4, 6, 8 |
| 3-column | `md:grid-cols-3` | 3, 6, 9, 12 |
| 4-column | `md:grid-cols-4` | 4, 8, 12 |

**Rules**:
- When adding or removing items breaks symmetry, adjust count to the nearest valid multiple
- If the design requires an odd count, use a visually balanced layout (e.g., span-2 for the last item, or a centered last row)
- Check symmetry at **every responsive breakpoint** — 3 columns on desktop may become 2 on tablet and 1 on mobile
- Verify symmetry after every content change: count items in arrays like `features`, `benefits`, `steps`, `testimonials`, `team members`

### Content-Component Alignment

When static content files drive UI components:
- Every array length must match the grid layout that renders it
- Adding/removing items in a content file requires checking the rendering component's grid configuration
- Document the mapping between content files and components in the project's `CLAUDE.md`

## Content Tone by Page Type

| Page Type | Tone | Energy Level |
|---|---|---|
| **Landing page** | Confident, direct, benefit-focused | High |
| **Homepage** | Welcoming, authoritative, clear | Medium-high |
| **Feature page** | Informative, specific, capability-focused | Medium |
| **Blog post** | Educational, conversational, helpful | Medium |
| **About page** | Authentic, warm, human | Medium |
| **Pricing page** | Transparent, straightforward, reassuring | Low-medium |
| **Documentation** | Precise, neutral, task-oriented | Low |
| **Error page** | Empathetic, helpful, brief | Low |
