---
name: marketing
description: Use this skill when running any daily/weekly/monthly marketing task in a project that already has marketing/MARKETING.md — the recurring marketing operations dispatcher for social posts, blog posts, email campaigns, trend research, analytics, content repurposing, community engagement, and strategy review. For first-time strategy setup, use /marketing-init.
context: fork
argument-hint: "<operation: social-post | blog-post | email | trend-research | analytics | strategy-review | community | content-repurpose>"
---

# /marketing — Recurring Operations

Dispatcher for recurring marketing operations against an existing `marketing/MARKETING.md`. For one-time strategy setup, use `/marketing-init`. Strategy frameworks (hierarchy, channel selection, content pillars, measurement) live in `@marketing-strategy` — load when an operation needs to reason about them.

**⚠️ CONSTRAINT:** This workflow NEVER modifies source code (`*.java`, `*.ts`, `*.tsx`, `*.py`, `*.go`), configs (`*.yaml`, `*.yml`, `*.json`), infrastructure (`*.tf`, `Dockerfile`, `Helm`), or dependency files (`pom.xml`, `package.json`, `requirements.txt`). Marketing creates and edits ONLY markdown files in the `marketing/` directory.

## When to use

- Daily: `/marketing social-post`, `/marketing community`
- 2–3×/week: `/marketing blog-post` (delegates to `/content-creation`)
- Weekly: `/marketing trend-research`, `/marketing analytics`
- Bi-weekly: `/marketing email`
- Monthly: `/marketing strategy-review`
- Ad-hoc: `/marketing content-repurpose`

## Not for

- First-time strategy setup → `/marketing-init`
- Blog post authoring → `/content-creation` (used by the `blog-post` operation below)
- Landing page design → `/ui-ux-design`
- SEO audits → `/seo-review`
- Technical documentation → `/docs` or `/docs-pack`

## Pre-flight check

Read `marketing/MARKETING.md`. If it does not exist, refuse and surface: "No `marketing/MARKETING.md` found — run `/marketing-init` first to set up strategy." Do NOT attempt any operation without strategy context.

## Step 1 — Select Operation

| Operation | Description | Cadence |
|---|---|---|
| `social-post` | Draft posts per platform | Daily |
| `blog-post` | Delegates to `/content-creation` | 2–3×/week |
| `email` | Email campaign / newsletter | Bi-weekly |
| `trend-research` | Trends + content opps | Weekly |
| `analytics` | Metrics review + adjustment | Weekly |
| `content-repurpose` | Cross-channel adaptation | As needed |
| `community` | Engagement response plan | Daily |
| `strategy-review` | Monthly strategy check | Monthly |

## Step 2 — Load Context

Read `marketing/MARKETING.md`, `marketing/content-calendar.md`, recent items in `marketing/` for the operation type (e.g. last 3 posts for `social-post` continuity). All wrapped per `untrusted-content-wrapping.md` (G1).

## Step 3 — Execute Operation

### `social-post`

Delegate to the `social-media-manager` skill — it owns platform-specific format rules (X, LinkedIn, Facebook, Threads, Bluesky) which churn faster than this skill should track. Pass topic (from calendar / trend / user) and `marketing/MARKETING.md` context (ICP, content pillars, voice). The social-media-manager skill applies `@humanizer` and saves to `marketing/posts/YYYY-MM-DD-[platform]-[topic].md`. Present, wait for approval.

### `blog-post`

Delegate to `/content-creation` with `marketing/MARKETING.md` context (ICP, content pillars, voice). `/content-creation` owns the 8-step pipeline + GEO/AEO + humanizer.

### `email`

`Agent(content-writer)` + `Agent(marketing-strategist)`. Define campaign type (newsletter / launch / re-engagement / welcome-drip — pick template from `assets/email-templates/`). Draft: subject (3 variants for A/B), preview, body, CTA. Apply `@geo-writer` (structure) → `@humanizer` (voice). Save to `marketing/emails/YYYY-MM-DD-[campaign].md`. Present + approval.

### `trend-research`

`Agent(marketing-strategist)`. Scan: X niche/competitor accounts, HN front page + relevant subreddits, Google Trends, industry newsletters. Identify content opportunities + conversations to join + emerging topics. Map opportunities to pillars from `@marketing-strategy` Content Pillar Model. Save to `marketing/research/YYYY-MM-DD-trends.md`. Update `marketing/content-calendar.md` with picked opportunities.

### `analytics`

`Agent(marketing-strategist)`. Review against MARKETING.md KPIs (per `@marketing-strategy` Measurement Framework — pipeline + revenue prioritized over vanity). Analyze: what works, what doesn't, why. Recommend channel/content adjustments. Save to `marketing/reports/YYYY-MM-DD-analytics.md`. Update MARKETING.md if strategy needs adjustment (rare — flag for the next `strategy-review`).

### `content-repurpose`

`Agent(content-designer)`. Source: blog post / feature release / case study / docs. Adapt: blog → X thread / LinkedIn post / email snippet / social graphics / short video script. Save variants in `marketing/posts/` with a shared `[source-id]` suffix so attribution is traceable.

### `community`

`Agent(marketing-strategist)`. Identify targets (relevant threads on X, Reddit, HN, forums) per ICP + pillars in MARKETING.md. Draft helpful, value-first, non-promotional responses. Save to `marketing/community/YYYY-MM-DD-engagement.md`.

### `strategy-review`

`Agent(marketing-strategist)` + `Agent(product-manager)`. Full top-down audit per `@marketing-strategy` Hierarchy — review MARKETING.md vs actual results. Assess goal progress, channel effectiveness, content performance, ROI. Adjust strategy/pillars/tactics/resources. Update MARKETING.md + content-calendar.md.

## Step 4 — Update Tracking

After every operation:

1. Update `marketing/content-calendar.md` — mark complete, add new items
2. If strategy implications surfaced → flag in MARKETING.md "Open questions" section for next `strategy-review`

## Step 5 — Summary

```
## Marketing Operation Summary

- **Operation**: <name>
- **Roles applied**: <list>
- **Materials created**: <file paths + descriptions>
- **Status**: draft / published / scheduled
- **Next scheduled**: <from calendar>
- **Follow-ups**: <if any>
```

## Directory Structure (target repo)

```
marketing/
├── MARKETING.md              # Strategy single-source-of-truth (produced by /marketing-init)
├── content-calendar.md       # Recurring task schedule (produced by /marketing-init)
├── posts/                    # Social posts: YYYY-MM-DD-[platform]-[topic].md
├── emails/                   # YYYY-MM-DD-[campaign-name].md
├── research/                 # YYYY-MM-DD-trends.md
├── reports/                  # YYYY-MM-DD-analytics.md
└── community/                # YYYY-MM-DD-engagement.md
```

## G7 spawn payloads

All agent spawns use structured payloads per `plugin/schemas/spawn-payload.schema.json`. Returns conform to `plugin/schemas/return-contract.schema.json`.

## Memory writes

| Layer | When | Shape |
|---|---|---|
| L4 | After each operation | Operation log line in `.ai-skills-memory/runs.jsonl` |

`marketing/MARKETING.md` itself is in the target repo (versioned in git), NOT in `.ai-skills-memory/`.

## Companions

- **`marketing-setup-template.md`** — MARKETING.md template (shared with `/marketing-init`)
- **`channel-playbooks.md`** — platform-specific format rules (X, LinkedIn, Reddit, email, community)
- **ABM (B2B)**: see `references/abm-playbook.md` for ICP tiering, intent signals, trigger events, and ABM-specific channel orchestration
- Email templates in `assets/email-templates/{newsletter,launch,re-engagement,welcome-drip}.md`. ICP worksheet in `assets/icp-worksheet.md`.

## Integration

- **Roles**: `Agent(marketing-strategist)` (strategy/analysis), `Agent(product-manager)` (product context, ICP), `Agent(content-designer)` (social, copy), `Agent(content-writer)` (blog, email), `Agent(seo-engineer)` (SEO)
- **Knowledge**: `@marketing-strategy` (frameworks), `@geo-writer` (GEO/AEO for blog + email), `@humanizer` (voice for all public-facing), `social-media-manager` (platform-specific algorithms)
- **Schemas**: `plugin/schemas/spawn-payload.schema.json`, `plugin/schemas/return-contract.schema.json`
- **Sub-workflows**: `/content-creation` (blog posts), `/seo-review` (SEO audit), `/docs-pack` (documentation)
- **Predecessor**: `/marketing-init` (creates MARKETING.md + content-calendar.md before any operation can run)
- **Rules**: `geo-content` (mandatory for blog/landing/email), `humanize-content` (mandatory for all public-facing), `untrusted-content-wrapping` (G1 wrap on project file reads)
- **Hooks**: `tool-output-normalize.py` (G2 on large web-research tool outputs)
