# Marketing Operation — Content Repurpose

> Date: 2026-04-24
> Operation: content-repurpose
> Role applied: content-designer
> Source: `blog/2026-04-22-postgres-vs-mysql-api-saas-2026.md`

## Context

`marketing/MARKETING.md` ICP = backend engineers at API-first SaaS. Pillar: data-layer choices. Voice: direct, opinionated, first-person. Reference blog hit 8,400 views in 48h.

## Adaptations

### X thread (delegated to social-media-manager)

8 tweets. T1 hook: "We migrated from MySQL to Postgres last quarter. Three things we learned the hard way." T2-T7: one finding per tweet (JSONB win, connection-pool surprise, replication gotcha, RLS unlock, cost delta, monitoring rewrite). T8: conversation prompt + plain-text domain reference for full write-up. 1 hashtag (#postgres) on the close.

File: `marketing/posts/2026-04-24-x-postgres-vs-mysql.md`

### LinkedIn carousel (delegated to social-media-manager)

8 slides, 1.4-1.6K char post body. Slide 1 hook = same as X T1. Slides 2-7 = one finding each with a concrete number ("9MB per connection vs 2MB"). Slide 8 = decision tree screenshot. Carousel-close prompt: "What did your migration teach you?" 4 hashtags (CamelCase).

File: `marketing/posts/2026-04-24-linkedin-postgres-vs-mysql.md`

### Email snippet (delegated to content-writer)

Newsletter section, ~180 words. Summary of the three findings + link to the blog post. CTA: "If you're considering a switch, the full decision tree is in the post."

File: `marketing/emails/2026-04-30-monthly-snippet-postgres-vs-mysql.md` (will land in next bi-weekly send).

### Reddit angle (community)

Draft for r/PostgreSQL: a comment on a relevant migration thread, value-first, links to blog as "deep dive" only at the bottom. Saved as queue item, not posted yet.

File: `marketing/community/2026-04-24-reddit-postgres-engagement.md`

## Delegation correctness check

- Social posts (X + LinkedIn) → social-media-manager (per skill contract)
- Email body → content-writer
- Blog source → already in `/content-creation` output (not re-touched)
- This op only orchestrates and saves the variant artefacts

## Calendar updates

- Marked 2026-04-24 content-repurpose complete (linked to source blog).
- Added: 2026-04-25 publish X thread (10am ET).
- Added: 2026-04-26 publish LinkedIn carousel.
- Added: 2026-04-30 newsletter send includes snippet.
- Added follow-up: monitor X thread for replies to repurpose into a follow-up community engagement.
