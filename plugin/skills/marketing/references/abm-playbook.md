# ABM Playbook (B2B)

Companion to `marketing` skill. Apply when the target product is B2B and the GTM motion includes named-account pursuit, intent-driven outreach, or PLG+sales hybrid expansion. Skip for pure consumer (B2C), self-serve-only (no sales touch), or single-buyer SMB plays where account-level orchestration adds no signal.

## 1. ABM 2026 reality

- ~76% of enterprise B2B organizations run a formal ABM motion in 2026 (Forrester, ITSMA-RAIN Group benchmarks), up from ~54% in 2024.
- The dominant 2026 GTM pattern is **PLG + ABM hybrid**: product-qualified usage signals route accounts into ABM tiers; ABM motion drives expansion within accounts already acquired through self-serve.
- **Signal-based GTM** (acting on intent + trigger data within 7–14 days) replaces broad-funnel spray as the default playbook for considered B2B purchases above ~$25K ACV.

## 2. Account selection (ICP tiering)

Three tiers, each with different orchestration economics:

| Tier | Account count | Touch model | Tooling | Owner |
|---|---|---|---|---|
| **Tier 1 — Strategic** | 10–50 named accounts | High-touch, multi-threaded (5–8 personas/account) | Manual research + ABM platform | Named SDR + AE pair |
| **Tier 2 — Programmatic** | 100–500 accounts | ABM platform orchestration, semi-personalized | Demandbase / 6sense / Terminus | Pooled SDR team |
| **Tier 3 — At-scale** | 1,000+ accounts | Programmatic ad targeting + nurture | Reverse-IP display, retargeting | Marketing automation |

**Selection scoring**: `ICP fit score × intent signal strength × current engagement × pipeline timing fit`. Re-score quarterly; accounts move tiers based on signal velocity.

## 3. Intent signal stacks (the 2026 standard)

Combine 2nd-party (off-site research) AND 1st-party (your-site behaviour) signals — neither alone is reliable.

| Source | Signal type | What it reveals |
|---|---|---|
| **Bombora** | 2nd-party intent topics | Which accounts are surging research on a topic across the B2B web |
| **G2 Buyer Intent** | Review-platform behaviour | Visits to comparison pages, alternatives pages, category pages |
| **TechTarget Priority Engine** | Tech-publication content engagement | Account-level reading on specific tech topics |
| **Demandbase / 6sense** | Combined 1st + 2nd-party | Intent + ABM orchestration in one platform |
| **Clearbit** (HubSpot) | Firmographic enrichment + reveal | Identifies anonymous site visitors at the account level |
| **LinkedIn Insight Tag** | First-party LinkedIn audience attribution | Account-level visit and ad-engagement data |

**Action rule**: a fresh intent surge has a 7–14 day decay window. If outreach lags by more than two weeks, treat the signal as stale.

## 4. Trigger events

Buying-window openers — outreach within the trigger window outperforms cold outreach 3–5x on response rate.

| Trigger | Window | Source |
|---|---|---|
| Funding rounds (Series A/B/C) | 30–60 days post-announcement | Crunchbase, PitchBook |
| Exec changes (new VP/CTO/CFO) | First 90 days of new exec | LinkedIn, news monitoring |
| Hiring spikes for ICP-relevant roles | Active req posted | LinkedIn Jobs, Cybersyn |
| Tech-stack changes / migrations | Detection within 30 days | BuiltWith, Wappalyzer APIs |
| M&A activity | 60–180 days post-close | News + SEC filings |
| Earnings-call mentions of relevant pain | Quarter following the call | Public-company transcripts |

## 5. ABM channel orchestration

Multi-touch, multi-channel sequences — a single channel does not break through at the enterprise level.

**Standard mix per touch sequence**: email + LinkedIn (personal outreach + sponsored InMail/ads) + reverse-IP display ads. Direct mail (Sendoso, Reachdesk) for Tier 1 only — diminishing returns below $50K ACV.

| Tier | Touches | Cadence | Personalization depth |
|---|---|---|---|
| Tier 1 | 12–15 over 30 days | Daily for 2 weeks → weekly | Per-account research, named-persona messaging |
| Tier 2 | 6–10 over 30 days | Weekly | Industry/segment templates with account-name token |
| Tier 3 | 3–5 over 60 days | Bi-weekly | Programmatic, ICP-segment-level only |

## 6. ABM measurement (different from broad-funnel)

Lead-level metrics do not work for ABM. Switch to account-level:

- **Account engagement score** = sum(touches × channel weight × recency decay)
- **Pipeline created per account** (not per lead) — count one opportunity per qualified account
- **Win rate per tier** — Tier 1 should outperform Tier 2 by 1.5–2x; if not, the tier definitions are wrong
- **Time-to-pipeline acceleration** vs a non-ABM control cohort
- **Target account penetration** = (engaged accounts in tier) / (total tier accounts)

Avoid MQL counts as a primary KPI for ABM motion — they reward volume over fit.

## 7. PLG + ABM hybrid (2026 motion)

The dominant pattern when self-serve and sales-led motions co-exist:

- **PLG signal triggers ABM motion**: 3+ users from the same domain on a paid plan, or a free-tier team approaching usage limits → enroll account in Tier 2 ABM.
- **ABM motion drives expansion within PLG-acquired accounts**: a self-serve customer's parent organization gets multi-threaded outreach for enterprise expansion.
- **PQL → AQL handoff**: product-qualified leads (PLG) get scored for account fit; high-fit accounts route to ABM, low-fit stay in PLG nurture.
- Tooling: Pocus, Endgame, Cohere — translate product usage into account-level signals consumable by sales.

## 8. Anti-patterns

- **"Spray-and-pray ABM"** — sending personalized email to 5,000 accounts is not ABM; it is templated outbound with extra steps. Real ABM is bounded by orchestration capacity per tier.
- **"Intent without context"** — buying intent data and not acting on it within the decay window is buying garbage. Operationalize routing within hours, not weeks.
- **"Single-channel ABM"** — email-only or LinkedIn-only sequences do not break through; multi-channel orchestration is the table-stakes 2026 baseline.
- **"Tier 1 too broad"** — 200 named Tier 1 accounts is a Tier 2 program with worse economics. Cap Tier 1 at what your AEs can actually multi-thread.
- **"Account engagement = success"** — engagement without sourced pipeline is a vanity metric; tie ABM ROI to opportunity creation per tier.

## Integration with `/marketing`

- Phase 1 (Init): if the project is B2B with named-account economics, `Agent(marketing-strategist)` should produce the ICP tiering and select an intent stack as part of step 3 (Define Strategy).
- Phase 2 (Execute): ABM-specific operations (account research, trigger monitoring, multi-channel sequence drafting) layer on top of `social-post`, `email`, and `community` operations — same agents, account-level scoping.
- Measurement: when ABM is in scope, `analytics` operation reports against account-level metrics from section 6, not broad-funnel KPIs.
