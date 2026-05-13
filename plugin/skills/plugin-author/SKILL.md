---
name: plugin-author
description: >-
  Umbrella workflow for ai-assets plugin-asset authoring and maintenance —
  creating, auditing, fixing, improving, refactoring, and migrating skills,
  agents, rules, hooks, prompts, schemas, and rubrics inside the plugin.
  Auto-classifies the request, loads the right knowledge skills
  (`@prompt-engineering`, `@context-engineering`, `@team-protocols`), and
  spawns the right subagents (`prompt-engineer`, `system-architect`,
  `python-engineer`, `software-engineer`, `qa-engineer`, `eval-judge`) via
  the `Agent` tool. Use when extending, repairing, or improving plugin
  assets, when ingesting a `/feedback` report as a fix-cycle backlog, or
  when you do not remember which lower-level command is right for the job.
argument-hint: "<create | audit | fix-feedback | improve | refactor | migrate> [target] [--from <report>] [--deep] [--learnings] [--strict]"
---

<!-- ARCHITECTURAL NOTE: no `context: fork`. As with `/develop` and `/team-bugfix`, this orchestrator runs in the main thread so it retains the `Agent` spawn primitive. Subagents cannot spawn other subagents. -->

# /plugin-author — Plugin Asset Authoring & Maintenance Orchestrator

Single entry point for the full lifecycle of assets under `plugin/`: skills, agents, rules, hooks, prompts, JSON schemas, eval rubrics, calibration samples. Classifies the request, picks a pipeline shape, and either runs a light single-pass or spawns a DEV → REVIEW → QA team via the `Agent` tool.

This skill absorbs `/plugin-skill-create` and `/plugin-skill-audit` as user-facing commands. Their SKILL.md files remain on disk as internal procedure references (read by this orchestrator) and are no longer reachable via slash invocation.

> **YOU MUST orchestrate via `Agent({...})` spawns for the HEAVY pipeline.** Inline edits of prompts, agent definitions, or rubrics by the Lead bypass the per-role review gates and violate the `team-protocols` invariant. Every role-step on the HEAVY path is an explicit `Agent({...})` call.

## When to use

"Add a new skill / agent / rule / hook"; "audit this skill — description not triggering"; "fix the findings in this `/feedback` report"; "improve rubric or calibration"; "refactor an oversized SKILL.md"; "migrate an older skill to current spec"; or when scope is unclear and you do not remember which lower-level command applies.

Not for: application/feature code (use `/develop`, `/bugfix`, `/refactor`); Codex/Windsurf parity mirrors (outside `plugin/`); Tier 3 suites (not yet shipped); plugin-wide diagnostic (`/plugin-doctor` directly).

## Operations

| Op | Trigger | Shape | DEV |
|---|---|---|---|
| `create` | "new skill", "scaffold", "add a hook" | scaffold + interview + HEAVY | per asset kind |
| `audit` | "audit", "lint a skill" | SIMPLE; `--deep` → HEAVY | `prompt-engineer` + `eval-judge` (`--deep`) |
| `fix-feedback` | `--from <path>` | HEAVY per finding | per asset kind |
| `improve` | "not triggering", "rubric is fuzzy" | HEAVY (one asset) | `prompt-engineer` or `eval-judge` |
| `refactor` | "split this SKILL.md" | HEAVY + equivalence gate | `prompt-engineer` |
| `migrate` | "update to current spec" | HEAVY per skill | `prompt-engineer` |

Full trigger-phrase table and disambiguation rules: `operation-router.md`.

## Invocation

```text
/plugin-author create <name> [--type workflow|knowledge|companion] [--agent-spawn] [--ralph]
/plugin-author audit [<name> | --all] [--deep] [--strict] [--fix]
/plugin-author fix-feedback --from .ai-assets-memory/feedback/feedback-2026-05-13-0910.json
/plugin-author improve <name> [--scope description|body|rubric|calibration]
/plugin-author refactor <name>
/plugin-author migrate <name>
/plugin-author                                # no args → one clarifying question, then route
```

`--learnings` (any op) opts in to user-global memory via `/learnings-write`. Off by default.

## Pre-flight

Read `CLAUDE.md` + `plugin/.claude-plugin/plugin.json`. Load Path B tools: `ToolSearch(select:TeamCreate,TaskCreate,TaskUpdate,SendMessage,TeamDelete,TaskStop,Monitor)`. Treat `@prompt-engineering`, `@context-engineering`, `@team-protocols` as knowledge — never spawn them. Refuse `create` / `fix-feedback` / `improve` / `refactor` / `migrate` on a dirty working tree touching the target asset. `audit` without `--fix` is always allowed.

## Classify

Apply `operation-router.md`. If two operations match, pick the broader; pass the narrower as a flag (`audit --fix`). If `--from <path>` is present, the operation is always `fix-feedback`. If ambiguous, ask ONE clarifying question — never silently pick.

For `fix-feedback`, prefer `<path>.json` (machine-readable parity counterpart of `<path>.md`) per `feedback-parser.md`. If only `.md` exists, warn and call `scripts/parse_feedback_report.py --md` (degraded path).

## Build the plan

- `create` / `improve`: 1–3 WPs typically.
- `audit`: one WP per target (each `--all --deep` skill = one WP).
- `fix-feedback`: one WP per finding; group by severity (H first), then by source kind so related findings batch onto the same subagent.
- `refactor` / `migrate`: 2–4 WPs (extract → reference → rewire → re-validate).

Wave sizing per `team-protocols/lead-protocol.md`: if >6 WPs, split into waves of 3–6, foundations first. After each wave clears the pipeline, print a checkpoint and auto-continue unless the user pauses within 60 s.

Asset-kind → DEV-role (full table in `asset-to-role-map.md`):

| Asset under `plugin/` | DEV subagent |
|---|---|
| `skills/<name>/SKILL.md` (frontmatter + body + refs) | `ai-assets:prompt-engineer` |
| `agents/<name>.md` | `ai-assets:prompt-engineer` |
| `rules/<name>.md` | `ai-assets:prompt-engineer` |
| `hooks/scripts/<name>.py` | `ai-assets:python-engineer` |
| `schemas/<name>.json` | `ai-assets:system-architect` |
| `eval/judge-rubrics/<name>.md` | `ai-assets:eval-judge` |
| `eval/calibration/<name>/*.md` | `ai-assets:eval-judge` |
| `eval/config.json`, `eval/cases/*` | `ai-assets:system-architect` |

REVIEW (every WP, `disallowedTools: ["Write", "Edit"]`): fresh `ai-assets:prompt-engineer` for prompt assets; `ai-assets:software-engineer` for code/schema assets. One reviewer — no co-review.

QA (every WP): `ai-assets:qa-engineer` for behavioral checks plus Lead-side post-checks (`validate.py`, internal audit per `plugin-skill-audit/SKILL.md`, `/plugin-doctor`, `/eval --skill <name> --tier 1` when applicable).

## Pipeline shape

**SIMPLE.** Used for `audit` without `--deep` and trivial scaffolds. Run inline by reading the absorbed procedure docs (`plugin-skill-create/SKILL.md`, `plugin-skill-audit/SKILL.md`). No subagent spawn.

**HEAVY.** Used for `create` (with interview + first DEV pass), `audit --deep`, `fix-feedback`, `improve`, `refactor`, `migrate`. DEV → REVIEW → QA per `@team-protocols`. Prefer Path B (Agent Teams); fall back to Path A only on a documented technical block at `TeamCreate` per `team-protocols/path-selection-rules.md` — **no silent fallback** for non-technical reasons (sequential WPs, "simpler", tmux absence are all invalid Path A triggers). The Path B `TeamCreate` natural-language prompt, file-channel backstop, `Monitor` wiring, and Path A three-step spawn loop are documented in `develop/SKILL.md` — apply verbatim with team name `plugin-author-<op>-<stamp>`.

Every `Agent({...})` `prompt` MUST embed a full G7 spawn payload (all six fields: `trace_id`, `subagent_role`, `goal`, `constraints`, `allowed_tools`, `budget`). See `team-protocols/g7-contracts.md`. The `subagent-start-budget.py` hook blocks the third malformed payload in a session — never paste a prose-only prompt.

## Mandatory gates per WP (HEAVY)

WP DONE only after all of: DEV G7 envelope `status=success`; Reviewer `verdict: approved`; QA `qa_verdict: pass`; Lead-side post-checks (`validate.py` exit 0, internal audit `--strict`, `/plugin-doctor` clean, `/eval --skill <name> --tier 1` for user-invocable workflow skills/rubrics). On any failure, requeue with failure attached as `constraints` and re-spawn DEV — Lead never patches inline. Max 3 cycles per WP, then escalate.

## Eval-loop closure

`create` / `improve` touching a user-invocable workflow skill or a rubric MUST close with: rubric present (`plugin/eval/judge-rubrics/<name>.md`, 5 dimensions), calibration ≥ 6 samples (`plugin/eval/calibration/<name>/{good,bad}/`), `/eval --skill <name> --tier 1` pass. Spawn `ai-assets:eval-judge` to author or tune the rubric when missing or when Spearman drifts.

`audit --deep` additionally spawns `ai-assets:prompt-engineer` per target for description (`prompt-engineering/optimizing-descriptions.md`) and security (`prompt-engineering/security-checklist.md`, OWASP LLM Top 10) review. `--all --deep` is opt-in and prints a budget warning before starting.

## Hard rules

- **Plugin scope only.** Touch nothing outside `plugin/`. Codex/Windsurf mirrors get a parity-reminder warning at end of run — never auto-edit them.
- **English-only assets** per repo CLAUDE.md.
- **Eval-first** for any prompt-modifying op (`prompt-engineer` agent rule: never change a prompt/tool/schema without defining how to measure impact).
- **G7 spawn payloads required** on every `Agent({...})` call.
- **Never auto-rewrite prose.** Inherit safe-fix table from `plugin-skill-audit/SKILL.md`; every prose change goes through DEV → REVIEW → QA, never regex.
- **Never rename a skill** automatically — refuse and ask.
- **Counts are part of every closure.** Add/hide a skill/agent/rubric/sample → bump `EXPECTED_COUNTS` in `plugin/dev/validate.py` in the same change set.
- **Memory L4 by default.** L5 only with `--learnings` via `/learnings-write`.
- **Never silently delete an absorbed skill.** Preserve its SKILL.md with `disable-model-invocation: true` and a description pointing to this skill.

## Failure modes

Ambiguous classification → ask one question. `fix-feedback` missing `.json` → warn, `--md` fallback, mark WPs `provenance: md-fallback`. Wave overflow → split per `lead-protocol.md`. Gate failure → requeue with failure as `constraints`; max 3 cycles; then escalate. `TeamCreate` error → Path A fallback, verbatim error. Spawn-budget exhausted → surface hook diagnostic.

## Memory writes

- L4 every run: append `{ts, op, target, wps, gate_results, fix_cycle_ref?}` to `.ai-assets-memory/plugin-author/runs.log`.
- L4 on `fix-feedback`: write `.ai-assets-memory/plugin-author/fix-cycles/<feedback-stamp>.json` mapping every closed WP to its `finding_id` so future `/feedback` runs detect "this finding was fixed".
- L5 only with `--learnings`: delegate to `/learnings-write` — never write `~/.claude/ai-assets/learnings.md` directly.

## Integration

- **Reads (procedure docs)**: `plugin-skill-create/SKILL.md`, `plugin-skill-audit/SKILL.md` (both `disable-model-invocation: true` after this skill ships).
- **Reads (knowledge)**: `@prompt-engineering`, `@context-engineering`, `@team-protocols`, `@subagent-spawn`.
- **Reads (project)**: `CLAUDE.md`, `plugin/.claude-plugin/plugin.json`, `plugin/dev/validate.py` `EXPECTED_COUNTS`.
- **Spawns**: `ai-assets:prompt-engineer`, `ai-assets:system-architect`, `ai-assets:python-engineer`, `ai-assets:software-engineer`, `ai-assets:qa-engineer`, `ai-assets:eval-judge`.
- **Writes (assets)**: under `plugin/skills/`, `plugin/agents/`, `plugin/rules/`, `plugin/hooks/`, `plugin/eval/`, `plugin/schemas/`.
- **Writes (logs)**: `.ai-assets-memory/plugin-author/runs.log`, `.ai-assets-memory/plugin-author/fix-cycles/`.
- **Companions**: `/plugin-doctor`, `/eval`, `/feedback` (produces input for `fix-feedback`), `/learnings-write`.
- **Supporting docs**: `operation-router.md`, `feedback-parser.md`, `asset-to-role-map.md`, `scripts/parse_feedback_report.py`.
- **Eval (planned in review pass 2)**: `plugin/eval/judge-rubrics/plugin-author.md`, `plugin/eval/calibration/plugin-author/{good,bad}/`, `plugin/eval/cases/plugin-author/`.
