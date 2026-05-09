# Ideal Customer Profile (ICP) Worksheet

Combines Jobs-to-be-Done (Christensen / Klement) with April Dunford positioning. Fill it in once during `/marketing init`, revisit quarterly during `/marketing strategy-review`. Keep it in `marketing/MARKETING.md` under the `## ICP` section.

The worksheet has six sections. B2B teams complete Firmographics; B2C teams complete Demographics; mixed-motion teams complete both.

---

## 1. Firmographics (B2B)

Hard, observable attributes of the buying organization.

| Field | Your answer |
|---|---|
| **Company size** | Headcount band (1-10, 11-50, 51-200, 201-1000, 1000+) and ARR if known |
| **Industry / vertical** | Specific NAICS or SIC code, not a generic label like `tech` |
| **Geography** | Country, region, or state. Note timezone and language requirements |
| **Tech stack signals** | Tools they already use that predict fit (e.g., uses Snowflake, has a Vercel deployment, runs Kubernetes) |
| **Team structure** | Which team owns the buying decision (Platform, DevEx, Marketing Ops, RevOps). How many people sit in that team |
| **Budget authority** | Who signs the check at this size — IC, manager, director, VP, C-level |
| **Buying motion** | Self-serve, sales-assisted, full enterprise sales |

---

## 2. Demographics (B2C)

For consumer or prosumer products. Skip if pure B2B.

| Field | Your answer |
|---|---|
| **Age range** | Tight band (e.g., 28-42) — wider than that means you have not decided |
| **Income** | Household income or disposable income range |
| **Geography** | Urban / suburban / rural; specific metros if local |
| **Lifestyle markers** | Behaviors that predict purchase (cooks at home 5+ nights/week, runs 3+ times a week, travels internationally twice a year) |
| **Life stage** | Single, partnered, parenting young kids, empty nester, retired |
| **Identity / community** | Subcultures and identities they self-select into |
| **Spending priorities** | What they currently pay premium prices for |

---

## 3. Jobs-to-be-Done (JTBD)

For each primary segment, name all three jobs. The functional job alone is rarely enough to predict purchase.

### Functional job (the practical task)
> When I _____, I want to _____, so I can _____.

Example (Stride task tracker): *When I run a planning meeting, I want to triage 80 backlog issues in 20 minutes, so I can ship the sprint plan before lunch.*

### Emotional job (the internal feeling)
> I want to feel _____ and avoid feeling _____.

Example: *I want to feel in control of my team's workload and avoid feeling like a bottleneck.*

### Social job (how they want to be perceived)
> I want others to see me as _____ and not as _____.

Example: *I want my CTO to see me as someone whose squads ship predictably and not as someone who constantly asks for more headcount.*

### Current solution
What they use today. Be specific — `spreadsheets`, `Jira plus a Notion doc`, `nothing, they just remember`.

### Struggle moment
The exact moment when the current solution fails. Where, when, who else is in the room. Specificity here is the difference between an ICP and a daydream.

### Forces (Klement model)

| Force | Question | Strength (1-5) |
|---|---|---|
| **Push** | What pain pushes them off the current solution? | |
| **Pull** | What attractive thing pulls them toward yours? | |
| **Anxiety** | What worries about switching? (data loss, learning curve, peer judgment) | |
| **Habit** | What inertia keeps them on the current solution? | |

You win when push + pull > anxiety + habit. If anxiety is your top blocker, the answer is usually a free trial, a migration tool, or stronger social proof — not a feature.

---

## 4. Dunford Positioning

From *Obviously Awesome* (April Dunford). Five inputs, in order.

### 4.1 Competitive alternatives
What the customer would do if your product did not exist. Often this is `nothing`, `a spreadsheet`, or `hire a contractor` — not the named competitor you assume.

### 4.2 Unique attributes
Features or capabilities only your product has. List them as facts, not claims. `Imports from Notion in two clicks, including images` is an attribute. `Best-in-class import experience` is not.

### 4.3 Value (resulting from attributes)
Translate each attribute into the value it creates for the customer. One attribute may produce several value statements; one value may need several attributes.

| Attribute | Value to customer |
|---|---|
| Imports from Notion in two clicks | Saves 1 hour per project migration |
| | Removes the engineer-handoff bottleneck |
| Natural-language command palette | Onboarding takes 4 days instead of 4 weeks |

### 4.4 Best-fit customer characteristics
Working backward from the value, who cares about it most? This is your ICP filter — sharper than firmographics alone.

> *Engineering teams of 12-180, already using GitHub, currently on Jira or Linear, where the team lead does the planning and feels the friction personally.*

### 4.5 Market category we win in
The frame of reference where you are the obvious choice. Choose carefully — categories carry their own competitive set and buyer expectations.

> *Engineering-native task tracker* — not `project management` (loses to Asana), not `agile tool` (loses to Jira on enterprise breadth).

---

## 5. ABM Signals (2026)

Account-Based Marketing buying signals. For B2B teams running outbound or named-account motion.

### Trigger events (account-level changes that predict buying readiness)
- **Funding announcements** — Series A/B/C rounds. New budget, new tooling appetite. Source: Crunchbase, PitchBook, Dealroom
- **Executive changes** — new CTO, VP Eng, Head of Marketing. New leaders rebuild stacks in the first 90 days. Source: LinkedIn Sales Navigator, TheirStack
- **Hiring spikes** — `now hiring 5 platform engineers` signals platform team scale-up. Source: LinkedIn job posts, Ashby, Greenhouse public boards
- **Tech stack changes** — adoption of complementary tooling (e.g., a new data warehouse implies new analytics needs). Source: BuiltWith, HG Insights, Wappalyzer
- **Public commitments** — quarterly earnings calls naming a strategic priority your product solves
- **M&A activity** — acquirer or acquired both go through tooling consolidation within 6 months

### Intent signals (account-level research behavior)
- **Bombora** — third-party content consumption topics. Use `surge` flag (significant uptick vs baseline)
- **G2 / TrustRadius / Capterra** — category page visits, comparison page visits, review submissions on competitors
- **TechTarget Priority Engine** — known buyer research on specific topics
- **Your own first-party intent** — repeat anonymous visits to pricing/docs from the same company IP, content downloads from a known account, demo requests that ghost

Score accounts on signal recency × signal strength × ICP fit. Re-rank weekly.

---

## 6. ICP Scorecard (Tier A / B / C)

Tier accounts so the team knows where to spend the most expensive time (live demos, custom decks, exec sponsorship).

### Scoring formula

```
ICP score = (firmographic_fit * 0.3)
          + (jtbd_fit * 0.3)
          + (intent_signal * 0.2)
          + (trigger_event * 0.2)
```

Each input scored 0-100. Composite score determines tier.

### Tier definitions

| Tier | Score range | Treatment |
|---|---|---|
| **A** | 80-100 | 1:1 ABM. Custom outreach, named SDR, exec-to-exec intro path, custom demo. Cap at 25-50 accounts so the team can actually serve them |
| **B** | 60-79 | 1:few ABM. Industry-segmented campaigns, semi-personalized outreach, standard demo with role-relevant slides |
| **C** | 40-59 | 1:many. Self-serve funnel, automated nurture, gated content, webinar invites |
| **Out** | 0-39 | Disqualify or park. Do not let weak-fit accounts drain rep time |

### Sample weighting tweaks
- Early-stage product (under $1M ARR): weight `jtbd_fit` higher (0.4) since you cannot afford to win deals that will churn
- Mature product with low ACV: weight `firmographic_fit` higher (0.4) since efficiency matters more than fit nuance
- Dense outbound motion: add `reachability` as a fifth input (0.1) — accounts where you have warm intros or clear contact paths

---

## How to use this worksheet

1. Fill it in during `/marketing init` (Phase 1, Step 3) before writing positioning or messaging
2. Pressure-test by interviewing 5+ best-fit current customers — do their answers match what you wrote?
3. Cross-link from `marketing/MARKETING.md → ## ICP` to this file
4. Review quarterly in `/marketing strategy-review`. The ICP usually drifts faster than founders expect, especially in the first 18 months
