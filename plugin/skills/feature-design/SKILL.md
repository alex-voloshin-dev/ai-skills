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

**Invalid reasons to downgrade Path B → Path A** (do NOT use these): "design waves are mostly sequential", "Path A is simpler". Path B's value is UX even for sequential work. The ONLY valid Path A trigger is a hard technical block at Path B Step 1.

**No silent fallback for non-technical reasons.** Either Path B Step 1 actually fails → silent Path A fallback, OR Path B works → stay on Path B.

## Pipeline (Path A — Subagents, default)

```
┌─ Context load: /context-load --for <role> for each Wave-1/2 agent
│  (shrinks per-agent input vs full project dump)
│
├─ WAVE 1 (parallel, independent drafts; 50K tokens each):
│  ├─ product-manager          → PRD.md
│  ├─ marketing-strategist     → MARKET-ANALYSIS.md (skip if not public-facing)
│  └─ system-architect         → ARCHITECTURE.md
│
├─ Gate: all wave-1 files exist & parseable (lead checks)
│
├─ WAVE 2 (parallel, domain reviews; reads wave-1 outputs):
│  ├─ ui-ux-designer (reads ARCHITECTURE + PRD)     → UX-FLOW.md + wireframes
│  ├─ db-engineer (reads ARCHITECTURE + PRD)        → DATA-MODEL.md
│  ├─ security-engineer (reads all wave-1)          → security section in RISKS.md
│  └─ qa-engineer (reads PRD + ARCHITECTURE)        → acceptance criteria review
│
├─ Gate: all wave-2 files exist & complete (lead checks)
│
├─ WAVE 3 (sequential, cross-check + eval):
│  ├─ product-manager-reviewer (fresh subagent, reads all w1+w2)  → feedback.md
│  ├─ system-architect (reviewer role, reads all)                 → architecture-review.md
│  └─ eval-judge (scores against feature-design.md rubric)        → REVIEW-LOG.md
│
├─ Gate: rubric score ≥ 4.0 AND all dimensions ≥ 3 → proceed; else → RALF
│
├─ RALF (if rubric not met):
│  │  Oracle: judge:feature-design.md (min_score 4.0)
│  │  Kill-on: regex:RUBRIC_FAILED_3X (three consecutive failures, same issue)
│  │  Caps: 5 iter / 250K tokens / 60 min (overridable in userConfig)
│  │  On failure: re-prompt Wave 2 agents with reviewer feedback
│  └─ (loop back to WAVE 3)
│
└─ Lead writes IMPLEMENTATION-PLAN.md (maps PRD requirements → work packages → engineer roles)
   Memory write: L4 designs/<feature-id>.md (summary + decisions)
   Final report: TodoList check + token totals + handoff hint to `/develop`
```

## Pipeline (Path B — Agent Teams, when `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`)

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

Use teammate-mode in-process if no tmux/iTerm2 is available.
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

## G7 spawn payloads

Every spawn embeds a structured payload per `plugin/schemas/spawn-payload.schema.json`. Lead validates returns against `plugin/schemas/return-contract.schema.json` (via `subagent-stop-learnings.py` hook).

Trace IDs follow pattern `wf-<YYYYMMDD>-<feature-id>-spawn-<seq>`. Allows span tracing across all 9+ spawns per design.

## Eval rubric

Pointer: `plugin/eval/judge-rubrics/feature-design.md` (B10 deliverable).

Six dimensions × 5 levels:

1. **Completeness** — all required artefacts present with depth
2. **Internal consistency** — no cross-doc contradictions, coherent vision
3. **Traceability** — requirements map to components map to test cases
4. **Handoff clarity** — engineer can begin work without back-and-forth
5. **Risk coverage** — identified, scored, mitigations specified
6. **GEO/marketing readiness** (if public-facing) — passes geo-audit + humanizer standards

Pass: avg ≥ 4.0, no dimension < 3.

## RALF wiring

- **Oracle:** `judge:feature-design.md` (min_score 4.0)
- **Kill-on:** `regex:RUBRIC_FAILED_3X`
- **Caps:** 5 iter / 250K tokens / 60 min — overridable in userConfig
- **State:** `<repo>/.ai-assets-memory/ralph/<run-id>/`

## Memory writes

| Layer | When | Shape |
|---|---|---|
| L4 | After Wave 1 complete | `.ai-assets-memory/designs/<feature-id>/wave1-summary.md` — high-level decisions per agent |
| L4 | After RALF complete | `.ai-assets-memory/designs/<feature-id>/final.md` — trace of rubric scores + converged design |
| L4 (committed, opt-in) | Before handoff | `.ai-assets-memory/.committed/designs/<feature-id>.md` — finalized snapshot for team review |

## Failure modes

- **Wave 1 or 2 subagent timeout:** lead retries once with explicit error context. If persistent, escalates to user with "narrow scope" instruction
- **Rubric score oscillates:** RALF detects same-issue-3X pattern, kills loop, writes diagnostic suggesting design ambiguity
- **Oracle (judge) crashes:** treat as `ORACLE_ERROR`; kill loop; surface full diagnostic from eval-judge stderr
- **Budget hit mid-RALF:** hard pause; prompt user to confirm continuation, raise budget, or abort

## Observability events

Written to `<repo>/.ai-assets-memory/sessions/<sid>/runs.jsonl` by `task-event-log.py` + `subagent-start-budget.py` + `subagent-stop-learnings.py` hooks:

- `workflow_start` — feature-design + idea hash
- `context_load` × 9 — per-agent context slice tokens
- `wave_start` (1, 2, 3)
- `agent_spawned` × N — per agent + model + tokens budget
- `agent_returned` — tokens in/out, duration
- `ralf_iter` — iteration N, oracle result, kill-on check
- `workflow_end` — final status (`SUCCESS` / `RALF_FAILED_BUDGET` / `RALF_FAILED_ITER`)

## Integration

- **Orchestrator agent**: `feature-design-lead` (Opus, `tools: Task`, only plugin agent allowed to spawn)
- **Schemas**: `plugin/schemas/spawn-payload.schema.json`, `plugin/schemas/return-contract.schema.json`
- **Companions**: `/context-load` (per-role context slices), `/subagent-spawn` (G7 payload helper), `/ralph` (RALF segment)
- **Followed by**: `/develop` (consumes IMPLEMENTATION-PLAN.md to execute work packages)
- **Rules**: `subagent-isolation` (G7 + bounded recursion + sequential code-mod gate), `untrusted-content-wrapping` (G1 wrap on subagent returns + project file reads), `ralph-budget` (caps), `geo-content` (if public-facing — applied during MARKET-ANALYSIS step), `humanize-content` (applied to all public-facing copy), `memory-discipline` (memory writes per layer)
- **Hooks**: `tool-output-wrap.py` + `tool-output-normalize.py` (G1+G2 on tool outputs), `subagent-start-budget.py` (G7 spawn validation + budget enforcement), `subagent-stop-learnings.py` (G7 return validation)
