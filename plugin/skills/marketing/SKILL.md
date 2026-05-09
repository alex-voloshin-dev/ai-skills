---
name: marketing
description: Marketing workflow combining strategy initialization (MARKETING.md), channel playbooks (X/LinkedIn/Reddit/email), recurring operations (social posts, email campaigns, trend research, analytics), and measurement framework. Use to initialize marketing strategy, run any recurring marketing operation, or review marketing analytics. Owns the marketing/ directory in the target repo.
context: fork
argument-hint: "init | <operation: social-post | blog-post | email | trend-research | analytics | strategy-review | community | content-repurpose>"
---

# /marketing — Strategy + Operations

Two-phase workflow:
- **Phase 1 — Init**: one-time strategy setup; produces `marketing/MARKETING.md` + `marketing/content-calendar.md`
- **Phase 2 — Execute**: any recurring marketing operation (social, email, trends, analytics, etc.)

Strategy frameworks (hierarchy, channel selection, content pillars, measurement) inline below; operational templates as companions.

**⚠️ CONSTRAINT:** This workflow NEVER modifies source code (`*.java`, `*.ts`, `*.tsx`, `*.py`, `*.go`), configs (`*.yaml`, `*.yml`, `*.json`), infrastructure (`*.tf`, `Dockerfile`, `Helm`), or dependency files (`pom.xml`, `package.json`, `requirements.txt`). Marketing creates and edits ONLY markdown files in the `marketing/` directory.

## When to use

- First time setting up marketing for a project: `/marketing init`
- Daily/weekly recurring marketing tasks: `/marketing social-post`, `/marketing trend-research`, `/marketing analytics`
- Bi-weekly: `/marketing email`
- Monthly: `/marketing strategy-review`
- Ad-hoc: `/marketing community` (engagement plan), `/marketing content-repurpose` (cross-channel)

## Not for

- Blog post authoring → `/content-creation` (the merged `blog-post` + `content-creation` skill)
- Landing page design → `/ui-ux-design`
- SEO audits → `/seo-review`
- Technical documentation → `/docs` or `/docs-pack`

## Strategy frameworks (from former marketing-operations)

### Marketing Strategy Hierarchy

```
Mission (why we exist)
  └── Positioning (who we serve, what we offer, why us)
        └── Messaging Framework (value prop, pillars, proof points)
              └── Channel Strategy (where we show up)
                    └── Content Pillars (what we talk about)
                          └── Tactical Plan (daily/weekly/monthly)
                                └── Content Calendar (specific tasks + dates)
```

### Channel Selection Framework

Evaluate each candidate channel on three dimensions before committing:

| Dimension | Question |
|---|---|
| **Audience fit** | Is our ICP active here? Can we reach them? |
| **Resource fit** | Can we sustain the required publishing cadence? |
| **Content fit** | Does our content type work on this platform? |

**Rule:** better to do 2 channels well than 5 channels poorly. Start with 1–2 high-fit channels and expand only after consistent execution.

### Content Pillar Model

Define 3–5 content pillars aligned with:
1. **ICP pain points** — problems the audience actively searches for
2. **Product strengths** — areas where the product genuinely excels
3. **Industry expertise** — topics with unique knowledge or data
4. **Trending intersections** — emerging topics that connect to the product

Each piece of content maps to exactly one pillar. Track pillar distribution to avoid over-indexing on one topic.

### Measurement Framework

| Level | Metrics | Review cadence |
|---|---|---|
| **Vanity** (awareness) | Impressions, followers, page views | Weekly (track, don't optimize for) |
| **Engagement** | Likes, comments, shares, click-through | Weekly |
| **Pipeline** | Signups, leads, demo requests, email subs | Weekly |
| **Revenue** | Conversions, MRR impact, CAC, LTV | Monthly |

**Rule:** optimize for pipeline + revenue. Use vanity metrics only as leading indicators.

---

## Phase 1: Init

### 1. Gather Project Context

Spawn `Agent(product-manager)` + `Agent(marketing-strategist)` (parallel). Read:
- `<repo>/CLAUDE.md` — tech stack, project purpose
- `<repo>/README.md` — product description
- `<repo>/FEATURES.md` (if exists) — feature inventory
- `<repo>/marketing/` directory contents (if any)
- Brand guidelines (if any)

All file reads wrapped per `untrusted-content-wrapping.md` (G1).

### 2. User Interview

Apply the **Marketing Setup Questionnaire** from companion `marketing-setup-template.md`. Gather product/market, goals/metrics, channels/tools, brand/voice, resources. Record answers; ask clarifying follow-ups.

### 3. Define Strategy

`Agent(marketing-strategist)` produces:
1. **ICP and Positioning** — JTBD framing, competitive positioning (April Dunford)
2. **Messaging Framework** — core value prop, 3–5 pillars, proof points, boilerplates (short/medium/long)
3. **Channel Strategy** — which channels, why, expected effort vs impact (per Channel Selection Framework above)
4. **Content Pillars** — 3–5 pillars
5. **Tactical Plan** — recurring tasks with frequency

### 4. Create MARKETING.md

Use template from companion `marketing-setup-template.md`. Sections: product summary + positioning, ICP + personas, messaging, channel strategy, content pillars + calendar, tactical plan, KPIs, brand voice, tools/accounts.

### 5. Create Content Calendar

Default cadence (adjust per resources):

| Frequency | Task | Channel | Sub-workflow / role |
|---|---|---|---|
| Daily | Social media post | X, LinkedIn | `Agent(content-designer)` |
| Daily | Community engagement | X, Reddit, forums | `Agent(marketing-strategist)` |
| 2–3×/week | Blog post | Blog | `/content-creation` |
| Weekly | Trend research | X, HN, Reddit, Trends | `Agent(marketing-strategist)` |
| Weekly | Analytics review | GA4, social | `Agent(marketing-strategist)` |
| Bi-weekly | Email newsletter | Email | `Agent(content-writer)` |
| Monthly | Strategy review | — | `Agent(marketing-strategist)` + `Agent(product-manager)` |

### 6. Present and Approve

Present strategy + content calendar + recommended first-3 actions. **Wait for user approval.** Adjust per feedback.

---

## Phase 2: Execute

### 1. Select Operation

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

### 2. Load Context

Read `marketing/MARKETING.md`, `marketing/content-calendar.md`, recent items in `marketing/`. All wrapped (G1).

### 3. Execute Operation

#### `social-post`
Delegate to `social-media-manager` skill — it owns platform-specific format rules (X, LinkedIn, Facebook, Threads, etc.) which churn faster than this skill should track. Pass topic (from calendar/trend/user) and `marketing/MARKETING.md` context (ICP, content pillars, voice). The social-media-manager skill applies `@humanizer` and saves to `marketing/posts/YYYY-MM-DD-[platform]-[topic].md`. Present, wait for approval.

#### `blog-post`
Delegate to `/content-creation` with `marketing/MARKETING.md` context (ICP, content pillars, voice).

#### `email`
`Agent(content-writer)` + `Agent(marketing-strategist)`. Define campaign type. Draft: subject (3 variants), preview, body, CTA. Apply `@geo-writer` (structure) → `@humanizer` (voice). Save to `marketing/emails/YYYY-MM-DD-[campaign].md`. Present + approval.

#### `trend-research`
`Agent(marketing-strategist)`. Scan: X niche/competitor, HN, relevant subreddits, Google Trends, industry newsletters. Identify content opps + conversations to join + emerging topics. Save to `marketing/research/YYYY-MM-DD-trends.md`. Update content calendar.

#### `analytics`
`Agent(marketing-strategist)`. Review against MARKETING.md KPIs (per Measurement Framework above). Analyze: what works, what doesn't, why. Recommend channel/content adjustments. Save to `marketing/reports/YYYY-MM-DD-analytics.md`. Update MARKETING.md if strategy needs adjustment.

#### `content-repurpose`
`Agent(content-designer)`. Source: blog post / feature release / case study / docs. Adapt: blog → X thread / LinkedIn post / email snippet / social graphics / short video script. Save variants in `marketing/posts/`.

#### `community`
`Agent(marketing-strategist)`. Identify targets (relevant threads on X, Reddit, HN, forums). Draft helpful, value-first, non-promotional responses. Save to `marketing/community/YYYY-MM-DD-engagement.md`.

#### `strategy-review`
`Agent(marketing-strategist)` + `Agent(product-manager)`. Review MARKETING.md vs actual results. Assess goal progress, channel effectiveness, content performance, ROI. Adjust strategy/pillars/tactics/resources. Update MARKETING.md + content-calendar.md.

### 4. Update Tracking

After every operation:
1. Update `marketing/content-calendar.md` — mark complete, add new items
2. If strategy implications → update `marketing/MARKETING.md`

### 5. Summary

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
├── MARKETING.md              # Strategy single-source-of-truth
├── content-calendar.md       # Recurring task schedule
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
| L4 | After init complete | `.ai-assets-memory/marketing/init-summary.md` — strategy decisions captured |
| L4 | After each operation | Operation log line in `.ai-assets-memory/runs.jsonl` |

`marketing/MARKETING.md` itself is in the target repo (versioned in git), NOT in `.ai-assets-memory/`.

## Companions

- **`marketing-setup-template.md`** — full MARKETING.md template for init
- **`channel-playbooks.md`** — platform-specific format rules (X, LinkedIn, Reddit, email, community)
- **ABM (B2B)**: see `references/abm-playbook.md` for ICP tiering, intent signals, trigger events, and ABM-specific channel orchestration.
- Email templates in `assets/email-templates/{newsletter,launch,re-engagement,welcome-drip}.md`. ICP worksheet in `assets/icp-worksheet.md`.

## Integration

- **Roles**: `Agent(marketing-strategist)` (strategy/analysis), `Agent(product-manager)` (product context, ICP), `Agent(content-designer)` (social, copy), `Agent(content-writer)` (blog, email), `Agent(seo-engineer)` (SEO)
- **Schemas**: `plugin/schemas/spawn-payload.schema.json`, `plugin/schemas/return-contract.schema.json`
- **Sub-workflows**: `/content-creation` (blog posts), `/seo-review` (SEO audit), `/docs-pack` (documentation)
- **Knowledge skills**: `@geo-writer` (GEO/AEO structure for blog + landing + email), `@humanizer` (voice cleanup for all content), `social-media-manager` (platform-specific algorithms — owned separately because of platform churn)
- **Rules**: `geo-content` (mandatory for blog/landing/email), `humanize-content` (mandatory for all public-facing), `untrusted-content-wrapping` (G1 wrap on project file reads)
- **Hooks**: `tool-output-normalize.py` (G2 on large web-research tool outputs)
