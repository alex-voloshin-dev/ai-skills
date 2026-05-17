# /feature-design — Multi-agent design pack from a feature idea

Turn a 1–3 sentence idea into a versioned design pack that engineers can execute.

## When to use

- Starting a new feature: `/feature-design "Users can save posts to read later"`
- Validating a customer ask: `/feature-design "Subscription tier with usage metering"`

## Not for

- Internal refactors → use [`/refactor`](refactor.md)
- Hotfixes → use [`/bugfix`](bugfix.md)
- Existing feature refinement when you already have a PRD → use [`/develop`](develop.md) directly

## How to invoke

```bash
/feature-design "<idea>"
```

The idea is 1–3 sentences from the user/customer perspective. No design assumptions. Examples:

```bash
/feature-design "Users can see where teammates are typing in real-time"
/feature-design "We need to limit API calls per month for non-paying users"
/feature-design "Allow team admins to bulk-disable accounts via CSV upload"
```

## What you get

A complete design pack written to `<repo>/docs/features/<feature-id>/` (versioned in git per Round 4 N6 convention exception):

| File | Producer agent | Contents |
|---|---|---|
| `PRD.md` | product-manager | Vision, success metrics, acceptance criteria |
| `MARKET-ANALYSIS.md` | marketing-strategist | Competitive snapshot, GTM angle (skip if internal) |
| `ARCHITECTURE.md` | system-architect | System design, components, dependencies |
| `UX-FLOW.md` | ui-ux-designer | User journeys, interactions, accessibility |
| `DATA-MODEL.md` | db-engineer | Schema, migrations, data flow |
| `IMPLEMENTATION-PLAN.md` | feature-design-lead | Work packages → engineer roles → effort |
| `RISKS.md` | security-engineer + qa-engineer | Risks, mitigations, rollback |
| `REVIEW-LOG.md` | eval-judge | Review cycles + score deltas (auto-generated) |

`<feature-id>` is generated from the first 3 words of your idea.

## How it works (3 waves)

1. **Wave 1 (parallel)**: PRD + MARKET-ANALYSIS + ARCHITECTURE drafts — independent, ~50K tokens each
2. **Wave 2 (parallel)**: UX + DATA-MODEL + security review + acceptance criteria review — read wave-1 outputs
3. **Wave 3 (sequential)**: cross-check by fresh PM reviewer + system-architect review + eval-judge scoring against the rubric

If the rubric score is < 4.0, RALF kicks in (5 iter / 250K tokens / 60min cap) — re-prompts wave-2 agents with reviewer feedback until pass.

## Cost expectations

- **Tokens**: 150–300K typical for a small feature; 500K+ for novel/complex domains where the rubric oscillates
- **Time**: 5–15 minutes for typical features; up to 60 min if RALF runs the full 5 iterations
- **Models**: Opus orchestrator (`feature-design-lead`); Sonnet for the 6 specialist agents; Haiku for `eval-judge`

If you hit the session-aggregate cap (`ralph_session_token_budget`), the workflow pauses and asks before continuing. Adjust via `/plugin configure ai-skills`.

## Common questions

**Can I skip MARKET-ANALYSIS for internal features?**
Yes — pass `--internal` (the marketing-strategist returns a one-line "N/A — internal" stub).

**What if a wave-1 agent crashes?**
The `feature-design-lead` retries once with explicit error context. Persistent failures escalate to you with "narrow scope" instructions.

**Can I edit the output and re-run RALF?**
Yes — edit any of the 7 markdown files and re-invoke `/feature-design` with `--resume <feature-id>`. The `eval-judge` re-scores; RALF picks up from where it left off.

**Why does the rubric oscillate sometimes?**
Usually means the design has genuine ambiguity. After 3 same-issue failures the loop kills with `RUBRIC_FAILED_3X` — you'll see the diagnostic suggesting design clarification.

**Where does the design pack go in git?**
`<repo>/docs/features/<feature-id>/`. By convention these are tracked and reviewed by the team. Run `git add docs/features/<feature-id>/` when you're ready to commit.

## Examples

### Internal feature
```bash
/feature-design "Add a job queue for background webhook processing" --internal
```
Skips MARKET-ANALYSIS. Output focuses on architecture + data + risk.

### Public-facing feature
```bash
/feature-design "Per-team usage analytics dashboard"
```
MARKET-ANALYSIS produced; UX-FLOW emphasizes accessibility; eval-judge runs the GEO-readiness dimension separately for any public-facing copy.

### Feature with significant data work
```bash
/feature-design "Audit log of all data access for SOC2 compliance"
```
DATA-MODEL produced (compliance-grade); RISKS emphasizes data retention + access control; security-engineer participates in wave 2.

## Related

- [`/develop`](develop.md) — consumes IMPLEMENTATION-PLAN.md to execute work packages
- [`/plan`](../workflows/feature-design.md) — lighter-weight planning when you already have a PRD
- [Memory](../concepts/memory.md) — design summaries are written to L4 + optionally `.committed/`
- [Eval](../concepts/eval.md) — `eval-judge` and the `feature-design.md` rubric
- [RALF](../concepts/ralf.md) — the iteration loop on rubric failures
