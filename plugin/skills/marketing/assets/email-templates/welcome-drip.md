# Welcome Drip Sequence — 5 Emails Over 2 Weeks

Onboarding sequence for new signups. Example context throughout: a SaaS product called `Linear-style task tracker for engineering teams` (call it `Stride` for the example). Adapt copy to your actual product.

Cadence summary:

| # | Day | Goal |
|---|---|---|
| 1 | 0 | Welcome + immediate value |
| 2 | 2 | Product feature deep-dive |
| 3 | 5 | Social proof + use cases |
| 4 | 9 | Community + resources |
| 5 | 14 | Upgrade path / next step |

---

## Email 1 — Day 0: Welcome + immediate value

**Subject**: `You are in. Here is the 90-second start.`
**Goal**: confirm signup, deliver one quick win, set expectations for the rest of the sequence.

**Body** (200-400 words):

> Hey {first_name},
>
> Welcome to Stride. Your workspace is live at {workspace_url}.
>
> Most teams get to their first useful sprint in under ten minutes. Here is the shortest path:
>
> 1. Create your first project (`Cmd+N`)
> 2. Paste your existing backlog — Stride parses Markdown, Linear exports, and Jira CSVs
> 3. Hit `Plan sprint` and pick a duration
>
> That is it. The triage view and burndown chart populate themselves once you have ten or more issues.
>
> Over the next two weeks I will send four more short emails — features you probably will not find on your own, how other teams use Stride, where to ask questions, and what unlocks on the paid plans. One every few days, no spam.
>
> Hit reply if anything is broken or confusing. I read every response.

**CTA**: `Open your workspace →`

---

## Email 2 — Day 2: Feature deep-dive

**Subject**: `The keyboard shortcut that saves us 20 minutes a day`
**Goal**: surface a non-obvious feature that becomes sticky once learned.

**Body** (200-400 words):

> Hey {first_name},
>
> Most users miss this for weeks. Stride has a global command palette — `Cmd+K` from anywhere. It does what you would expect (search, jump to project, create issue) but the killer use is bulk actions:
>
> - `Cmd+K` → type `assign sprint 14 to me` → done
> - `Cmd+K` → type `move all P2 from backlog to next sprint` → done
> - `Cmd+K` → type `archive done from last sprint` → done
>
> Natural-language commands. No menu hunting. The palette also works during standup — open it, type `show my issues this sprint`, screen-share, move on.
>
> Three more shortcuts worth learning today:
>
> - `G` then `I` — jump to inbox
> - `Shift+Cmd+,` — toggle the side panel
> - `?` — open the full keyboard map
>
> Pin the keyboard map somewhere visible for the first week. Muscle memory takes about four days.

**CTA**: `Try the command palette →`

---

## Email 3 — Day 5: Social proof + use cases

**Subject**: `How Acme runs 14 squads on Stride`
**Goal**: show what `good` looks like at scale, hint at long-term value.

**Body** (200-400 words):

> Hey {first_name},
>
> Three stories from teams further along than you.
>
> **Acme (180 engineers, 14 squads).** Each squad has its own workspace, but a shared `cross-team` project sits above them. Squad leads triage there every Monday. Their VP of Engineering said the meeting got 40 minutes shorter once they stopped switching tools mid-call.
>
> **Northwind (12 engineers).** They run two-week sprints with a single project per service. Their hack: every issue starts with the service name in brackets — `[auth]`, `[billing]`, `[gateway]`. Filtering by service is one click. They tried labels first and dropped them.
>
> **Solo dev (one person).** Stride works for individuals too. The simplest setup: one project called `Now`, one called `Later`. Drag between them weekly. No sprints, no estimates.
>
> The pattern across all three: keep the structure simple, lean on filters and the command palette, do not over-configure on day one.

**CTA**: `Browse more team setups →`

---

## Email 4 — Day 9: Community + resources

**Subject**: `Where to ask the awkward questions`
**Goal**: route the user to peer support, reduce solo-tool isolation.

**Body** (200-400 words):

> Hey {first_name},
>
> If you have hit a wall, you are not the first. Three places to look:
>
> **Discord** — `discord.gg/stride`. About 2,000 active members. The `#workflow-help` channel gets answered within an hour during weekdays. Lurkers welcome.
>
> **Office hours** — every Thursday, 10am PT. Twenty minutes of demo, twenty minutes of open Q&A. Recordings posted the next day if the time does not work.
>
> **Docs and recipes** — `stride.dev/recipes` covers the patterns we see most: GitHub PR sync, Slack notifications, custom workflows, CSV import gotchas. Each recipe is a 5-minute read with copy-pasteable config.
>
> Two write-ups worth a click this week:
>
> - `Setting up sprint health metrics` — what to track, what to ignore
> - `Migrating from Jira without losing history` — the field-mapping cheat sheet
>
> If you find a gap in the docs, reply with what you searched for. We add 2-3 recipes a week based on those replies.

**CTA**: `Join the Discord →`

---

## Email 5 — Day 14: Upgrade path

**Subject**: `What unlocks on the paid plan`
**Goal**: present the upgrade as a natural next step, not a paywall ambush.

**Body** (200-400 words):

> Hey {first_name},
>
> You have been on Stride for two weeks. If you are still using it, that is the strongest signal that it is working. Here is what changes when you move to a paid plan.
>
> **Pro ($12/user/month)**:
>
> - Unlimited projects (free plan caps at three)
> - GitHub, GitLab, and Linear sync
> - Custom workflows per project
> - 90-day audit log
>
> **Team ($24/user/month)**:
>
> - Everything in Pro
> - SSO (Google, Okta, SAML)
> - Custom roles and permissions
> - Priority support, 4-hour SLA
>
> Most teams move to Pro in week three. The trigger is usually the third project — that is the cap-hit moment.
>
> Two notes:
>
> 1. Annual billing saves 20%. The savings show up at checkout, no code needed.
> 2. We do not auto-charge anything. The free plan keeps working forever if you do not upgrade.
>
> If you have decided Stride is not the fit, that is also a useful signal. Reply with what was missing — I read every one of those notes and they shape the roadmap.

**CTA**: `Compare plans →`

---

## After the sequence

Move the user into your regular newsletter list on day 15. Tag them with the sequence completion event so analytics can attribute upgrades to the drip. If they upgraded mid-sequence, skip the remaining emails and send a single `thanks for upgrading` confirmation instead.
