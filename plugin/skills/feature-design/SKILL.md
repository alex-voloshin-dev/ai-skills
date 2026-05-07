---
name: feature-design
description: Convert a 1–3 sentence feature idea into a complete design pack (PRD, ARCHITECTURE, UX-FLOW, DATA-MODEL, RISKS, IMPLEMENTATION-PLAN, REVIEW-LOG). Multi-agent three-wave pipeline orchestrated by feature-design-lead. Use when starting a new feature from concept. Not for refactors (use /refactor), bugfixes (use /bugfix), or refining existing PRDs (use /develop directly).
argument-hint: "<idea, 1-3 sentences>"
---

<!-- ARCHITECTURAL NOTE (alpha.25): no `context: fork` here. Per Anthropic docs, subagents cannot spawn other subagents. The three-wave orchestration pipeline requires the `Agent` tool, which is only available in the main thread. -->


# /feature-design — Multi-Agent Design Pack

Three-wave parallel-then-sequential pipeline that turns a feature idea into a versioned design pack ready for `/develop` to execute. Orchestrated by `feature-design-lead` (the only plugin agent with `tools: Task`).

## When to use

- Starting a new feature: `/feature-design "live collaborative cursors in markdown editor"`
- Validating a customer ask: `/feature-design "subscription tier with usage metering"`

## Not for

- Internal refactors → `/refactor`
- Hotfixes → `/bugfix`
- Existing feature refinement when you already have a PRD → `/develop`

## Invocation

```
/feature-design "Users can see where teammates are typing in real-time"
/feature-design "We need to limit API calls per month for non-paying users"
```

## Output (Round 4 N6 convention exception)

Files written to **`<repo>/docs/features/<feature-id>/`** — INSIDE the target repo's `docs/`, NOT inside `.ai-assets-memory/`. Reason: design packs are intended to be VERSIONED IN GIT as project documentation, reviewed by the team, and live across many sprints.

| File | Producer | Notes |
|---|---|---|
| `PRD.md` | product-manager | Vision, success metrics, acceptance criteria |
| `MARKET-ANALYSIS.md` | marketing-strategist | Competitive snapshot, GTM angle (optional if not public-facing) |
| `ARCHITECTURE.md` | system-architect | System design, component diagram, dependency list |
| `UX-FLOW.md` | ui-ux-designer | User journeys, interaction flows, accessibility notes |
| `DATA-MODEL.md` | db-engineer | Schema, migrations, data flow (if relevant) |
| `IMPLEMENTATION-PLAN.md` | feature-design-lead | Work packages per stack, engineer role assignments, estimated effort |
| `RISKS.md` | security-engineer + qa-engineer | Identified risks, mitigation strategies, rollback plan |
| `REVIEW-LOG.md` | eval-judge | Auto-generated trace showing all review cycles and score deltas |

`<feature-id>` auto-generated from first 3 words of idea.

## Agent roster

| Agent | Model | Effort | Wave | Role |
|---|---|---|---|---|
| `feature-design-lead` | Opus | xhigh | (orchestrator) | Orchestrates waves, enforces gates, writes IMPLEMENTATION-PLAN |
| `product-manager` | inherit | medium | 1 | PRD from idea + context slice |
| `marketing-strategist` | inherit | medium | 1 | MARKET-ANALYSIS, GTM angle |
| `system-architect` | inherit | high | 1 | ARCHITECTURE skeleton |
| `ui-ux-designer` | inherit | medium | 2 | UX-FLOW + wireframes + accessibility |
| `db-engineer` | inherit | high | 2 | DATA-MODEL if schema change needed |
| `security-engineer` | sonnet | high | 2 | Security section for RISKS |
| `qa-engineer` | inherit | medium | 2 | Acceptance criteria review |
| `product-manager` (reviewer) | inherit | medium | 3 | Fresh-eyes cross-check |
| `eval-judge` | haiku | low | 3 | Score against feature-design rubric |

## Choose execution path

Per `@team-protocols` "Two Paths" section: this skill supports Path A (Subagents) and Path B (Agent Teams). **Path B is the default preference** — visual team panel + Shift+↓ + per-role transcript. The 3-wave pipeline maps to a shared task list with `dependsOn` enforcing wave gates structurally.

**Detection is implicit, not explicit.** No Bash env-var check. Go to Path B Step 1 (team creation) directly; if it fails technically ("Agent Teams not enabled" or equivalent), silently fall back to Path A and continue.

**Invalid reasons to downgrade Path B → Path A** (do NOT use these): "design waves are mostly sequential", "Path A is simpler", "tmux/iTerm2 not available", "Windows host". Path B's value is UX even for sequential work — and Agent Teams supports `in-process` display mode that works in any terminal (Windows included) with NO extra setup. tmux is needed ONLY for optional split-pane display. The ONLY valid Path A trigger is a hard technical block at Path B Step 1 (team-creation natural language returns "Agent Teams not enabled" or equivalent — typically `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` env var unset).

**No silent fallback for non-technical reasons.** Either Path B Step 1 actually fails → silent Path A fallback, OR Path B works → stay on Path B (defaulting to `teammate-mode in-process` if tmux/iTerm2 uncertain).

## Step 0 — ATTEMPT Path B FIRST (literal, mandatory)

Before reading the Path A section below, you MUST attempt Path B Step 1 (jump straight to "Path B — Agent Teams" further down). Do NOT pre-emptively pick Path A based on:

- absence of CLAUDE.md / git repo
- single-stack project
- "small" or "simple" feature
- Windows host
- "no tmux available"
- pipeline being mostly sequential
- the fact that Path A appears earlier in this document

The ONLY way to land on Path A is: try Path B Step 1's natural-language team-creation, get back a literal "Agent Teams not enabled" / "experimental flag not set" / equivalent technical error, THEN fall back. Announcing "going Path A because empty project / Windows / no git" is a violation of this protocol.

When you announce the chosen path to the user, the FIRST sentence MUST be either:
- "Attempting Path B (Agent Teams) team-create..." (then either Path B works, or you receive the technical error and fall back)
- (after fallback) "Agent Teams API returned: <verbatim error>. Falling back to Path A."

Saying "I'll proceed via Path A" without the above sequence is forbidden.

## Pipeline (Path B — Agent Teams, PREFERRED — try this FIRST)

Per `@team-protocols` "Dual-Path Detection → Path B" section. The Lead drives via natural language; each role-teammate is a full Claude Code session.

### Step 1 — create the team

```text
Create an agent team named "<feature-slug>-design-team" with these teammates, each using subagent definitions from the ai-assets plugin:

Wave 1 (parallel drafts):
- "pm" (ai-assets:product-manager) — PRD.md author
- "marketing" (ai-assets:marketing-strategist) — MARKET-ANALYSIS.md author (skip if not public-facing)
- "sysarch" (ai-assets:system-architect) — ARCHITECTURE.md author

Wave 2 (parallel domain reviews):
- "ux" (ai-assets:ui-ux-designer) — UX-FLOW.md + wireframes (reads wave-1 PRD + ARCHITECTURE)
- "db" (ai-assets:db-engineer) — DATA-MODEL.md (reads wave-1 PRD + ARCHITECTURE)
- "sec" (ai-assets:security-engineer) — security section in RISKS.md (reads all wave-1)
- "qa-design" (ai-assets:qa-engineer) — acceptance criteria review (reads PRD + ARCHITECTURE)

Wave 3 (sequential cross-check):
- "pm-review" (ai-assets:product-manager) — fresh PM-reviewer reading all wave-1 + wave-2 outputs → feedback.md
- "sysarch-review" (ai-assets:system-architect) — architecture-review.md
- "judge" (ai-assets:eval-judge) — scores against feature-design.md rubric → REVIEW-LOG.md

Use **teammate-mode `in-process`** by default (works in any terminal including Windows without WSL — no tmux/iTerm2 required). Pick `tmux` split-pane mode ONLY if the user has explicitly indicated tmux or iTerm2 is available and they prefer it. If unsure: `in-process` is the safe choice.
```

### Step 2 — populate the shared task list with wave gates

Wave-2 tasks `dependsOn` all wave-1 tasks. Wave-3 tasks `dependsOn` all wave-2 tasks. The dependency graph enforces the wave gates structurally — no manual gate-checking needed.

### Step 3 — drive and monitor

- Wave-1 teammates self-claim their task immediately and work in parallel.
- When all wave-1 tasks complete, wave-2 teammates auto-claim. The user uses Shift+↓ to peek into any role's transcript.
- Wave-3 runs sequentially because the three tasks share `dependsOn` chains pm-review → sysarch-review → judge.
- If `judge` returns rubric score < 4.0 or any dimension < 3 → Lead inserts wave-2 follow-up tasks ("re-prompt with feedback") and re-points wave-3 dependencies. RALF caps from `ralph-budget.md` apply (5 iter / 250K tokens / 60 min).

### Step 4 — finalize + cleanup

After rubric passes: Lead writes IMPLEMENTATION-PLAN.md in main thread (not a teammate task), records L4 memory write, then asks: "Clean up the team."

## Pipeline (Path A — Subagents fallback, only if Path B Step 1 returned a technical error)

Three-wave pipeline with parallel Wave-1 / Wave-2 spawns and a sequential Wave-3 cross-check + eval. The full wave-by-wave ASCII tree (per-agent context-load, gate checks between waves, RALF retry hookup, and the final IMPLEMENTATION-PLAN.md handoff) lives in [`wave-protocol.md`](./wave-protocol.md). Load it when actually executing Path A.

## G7 spawn payloads

Every spawn embeds a structured payload per `plugin/schemas/spawn-payload.schema.json`. Lead validates returns against `plugin/schemas/return-contract.schema.json` (via `subagent-stop-learnings.py` hook).

Trace IDs follow pattern `wf-<YYYYMMDD>-<feature-id>-spawn-<seq>`. Allows span tracing across all 9+ spawns per design.

## Eval, RALF, memory, observability

The 6-dimension eval rubric (pass: avg ≥ 4.0, no dimension < 3), RALF caps (5 iter / 250K tokens / 60 min, kill-on `regex:RUBRIC_FAILED_3X`), memory-write layers (L4 wave1-summary + L4 final + opt-in L4 committed), failure modes (timeouts, oscillation, oracle crashes, budget hits), and observability events written to `runs.jsonl` all live in [`eval-and-ralf.md`](./eval-and-ralf.md). Load it when running the Wave-3 → RALF retry loop, validating rubric scores, or diagnosing why a design didn't converge.

## Integration

- **Orchestrator agent**: `feature-design-lead` (Opus, `tools: Task`, only plugin agent allowed to spawn)
- **Schemas**: `plugin/schemas/spawn-payload.schema.json`, `plugin/schemas/return-contract.schema.json`
- **Companions**: `/context-load` (per-role context slices), `/subagent-spawn` (G7 payload helper), `/ralph` (RALF segment)
- **Followed by**: `/develop` (consumes IMPLEMENTATION-PLAN.md to execute work packages)
- **Rules**: `subagent-isolation` (G7 + bounded recursion + sequential code-mod gate), `untrusted-content-wrapping` (G1 wrap on subagent returns + project file reads), `ralph-budget` (caps), `geo-content` (if public-facing — applied during MARKET-ANALYSIS step), `humanize-content` (applied to all public-facing copy), `memory-discipline` (memory writes per layer)
- **Hooks**: `tool-output-wrap.py` + `tool-output-normalize.py` (G1+G2 on tool outputs), `subagent-start-budget.py` (G7 spawn validation + budget enforcement), `subagent-stop-learnings.py` (G7 return validation)
