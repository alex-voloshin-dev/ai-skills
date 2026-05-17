# asset-to-role-map.md — what we're editing → which DEV / REVIEW subagent

This table is the authoritative mapping `/plugin-author` uses to pick subagents when building a work package.

- **DEV** — chosen per asset kind from the table below.
- **REVIEW** — `ai-skills:prompt-engineer` (fresh instance, `disallowedTools: ["Write", "Edit"]`) for prompt assets (SKILL.md, agents, rules, rubrics, calibration); `ai-skills:software-engineer` (same disallow) for code and schema assets. One reviewer per WP — no co-review.
- **QA** — `ai-skills:qa-engineer` for behavioral checks, with Lead-side automated post-checks (`validate.py`, internal audit, `/plugin-doctor`, `/eval --tier 1`) regardless of asset kind.

## Primary table

| Asset path / pattern under `plugin/` | DEV subagent | Why |
|---|---|---|
| `skills/<name>/SKILL.md` — frontmatter | `ai-skills:prompt-engineer` | Description, trigger keywords, third-person, imperative phrasing are prompt-engineering concerns (`prompt-engineering/optimizing-descriptions.md`). |
| `skills/<name>/SKILL.md` — body (procedures, behavior, when-to-use) | `ai-skills:prompt-engineer` | Body is an instructive prompt + workflow spec. For very broad rewrites, co-review with `ai-skills:system-architect`. |
| `skills/<name>/<reference>.md` (operation-router, feedback-parser, role-cards, …) | `ai-skills:prompt-engineer` | Sibling reference docs are loaded into prompt context — same engineering surface. |
| `skills/<name>/scripts/<file>.py` | `ai-skills:python-engineer` | Python code, not prompt. |
| `skills/<name>/scripts/<file>.sh` | `ai-skills:devops-engineer` | Shell automation. |
| `agents/<name>.md` | `ai-skills:prompt-engineer` | Agent definition = system prompt. |
| `rules/<name>.md` | `ai-skills:prompt-engineer` | Rule = guardrail prompt. |
| `hooks/scripts/<name>.py` | `ai-skills:python-engineer` | Python hook scripts. |
| `hooks/scripts/_lib.py`, shared helpers | `ai-skills:python-engineer` | Shared Python utility. |
| `hooks/hooks.json` | `ai-skills:system-architect` | Wiring config — system-level contract. |
| `schemas/<name>.json` (G7 spawn / return, etc.) | `ai-skills:system-architect` | JSON Schema = inter-component contract. |
| `eval/judge-rubrics/<name>.md` | `ai-skills:eval-judge` | Rubric — specialist asset for LLM-as-judge; requires calibration. |
| `eval/calibration/<name>/{good,bad}/*.md` | `ai-skills:eval-judge` | Calibration samples shape the rubric's behavior. |
| `eval/cases/<name>/*.json` | `ai-skills:system-architect` | Tier-3 case spec — contract surface. |
| `eval/config.json` | `ai-skills:system-architect` | Runner config — schema-bound. |
| `docs/workflows/<name>.md`, `docs/concepts/<name>.md` | `ai-skills:content-writer` | User-facing technical docs — diátaxis/style-guide concerns. |
| `dev/validate.py`, `dev/*` | `ai-skills:python-engineer` | Developer tooling. |
| `.claude-plugin/plugin.json` | `ai-skills:system-architect` | Plugin manifest — userConfig schema + versioning. |
| `.claude-plugin/marketplace.json` | `ai-skills:system-architect` | Marketplace manifest. |

## Multi-asset WPs (one DEV per WP)

`/plugin-author` does NOT co-review (one reviewer per WP — see header). When a single user request spans more than one asset kind (e.g. "add a hook AND wire it into a SKILL.md"), split it into **separate WPs** by asset boundary, each with its own DEV from the table and the matching REVIEW role:

| Cross-boundary change | WP 1 (DEV) | WP 2 (DEV) | Order |
|---|---|---|---|
| SKILL.md body + new hook script | `python-engineer` (hook) | `prompt-engineer` (SKILL.md cites the hook) | hook first; SKILL.md follows |
| SKILL.md body + new G7 schema field | `system-architect` (schema) | `prompt-engineer` (SKILL.md cites the schema) | schema first |
| Rubric + calibration sample addition | `eval-judge` (rubric) | `eval-judge` (calibration) | rubric first; samples follow |
| Doc page describes new skill behavior | `prompt-engineer` (skill) | `content-writer` (doc) | skill catches up first; doc lands second |

The per-file sequential gate from `team-protocols/spawn-pattern.md` applies across the WPs too — never run two writers against the same file in parallel.

## Edge cases

- **Renames** (e.g., `skills/old-name/` → `skills/new-name/`): refused by `/plugin-author`. Rename is a behavior change; the user runs it manually and then asks `/plugin-author audit <new-name>`.
- **Deletions**: refused. Deletion is irreversible; require explicit user confirmation outside the orchestrator.
- **Asset has no match** in the table above: route to `ai-skills:system-architect` by default and emit a WARN that the table needs a new row.
- **Asset lives outside `plugin/`**: refuse — `/plugin-author` is plugin-only. Print the parity-matrix workflow as the right destination.

## Why these defaults

- Skills, agents, rules are **prompts**. The dedicated `prompt-engineer` agent applies `prompt-engineering`, `optimizing-descriptions`, and the OWASP LLM Top 10 security checklist on every edit. Using a generic engineer here loses the eval-first discipline.
- Hooks are Python code with no prompt surface. `python-engineer` owns Python tooling, dependency management, and the hook lifecycle.
- Rubrics + calibration samples are the LLM-as-judge contract. Only `eval-judge` is calibrated against the score-band consistency drill — any other role would produce uncalibrated rubrics.
- Schemas + config.json are pure contracts. `system-architect` owns versioning, backward compatibility, and impact analysis.

## Update procedure

When a new asset kind is added under `plugin/` (e.g., a new top-level directory like `prompts/` or `tools/`), add a row to the Primary table in the same PR that introduces it. `/plugin-author audit asset-to-role-map.md` (a self-audit) is part of the closure for any structural change.
