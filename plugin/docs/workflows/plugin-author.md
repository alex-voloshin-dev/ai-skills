# /plugin-author — Plugin asset authoring & maintenance orchestrator

Single entry point for the full lifecycle of assets under `plugin/`: skills, agents, rules, hooks, JSON schemas, eval rubrics, calibration samples. Classifies the request, picks a pipeline shape, and either runs a light single-pass or spawns a DEV → REVIEW → QA team via the `Agent` tool.

## When to use

- "Add a new skill / agent / rule / hook to the plugin"
- "Audit this skill — its description doesn't trigger when I expect it to"
- "Fix the findings in this `/feedback` report" (paired with `--from <report>`)
- "Improve the rubric or calibration for skill X"
- "Refactor an oversized SKILL.md per progressive disclosure"
- "Migrate an older skill to the current agentskills.io spec"
- You don't remember which lower-level command applies — `/plugin-author` routes for you

## Not for

- Application or feature code in a target project → use [`/develop`](develop.md), [`/bugfix`](bugfix.md), [`/refactor`](refactor.md)
- Codex/Windsurf parity mirrors (those live outside `plugin/`) — handled by `review/parity-matrix.md`
- Tier 3 behavioral suites — not yet shipped
- Whole-plugin diagnostic — call `/plugin-doctor` directly

## How to invoke

```bash
/plugin-author create <name> [--type workflow|knowledge|companion] [--agent-spawn] [--ralph]
/plugin-author audit [<name> | --all] [--deep] [--strict] [--fix]
/plugin-author fix-feedback --from .ai-assets-memory/feedback/feedback-2026-05-13-0910.json
/plugin-author improve <name> [--scope description|body|rubric|calibration]
/plugin-author refactor <name>
/plugin-author migrate <name>
/plugin-author                                # no args → one clarifying question, then route
```

`--learnings` (any op) opts in to writing reusable patterns to user-global memory via `/learnings-write`. Off by default.

## What you get

- **`create`** — scaffolded asset + first DEV pass + eval-stub (rubric + calibration directories) + counts bumped in `plugin/dev/validate.py`
- **`audit`** (default) — spec/body/refs/eval/plugin-convention report; with `--fix` applies the deterministic safe-fix table
- **`audit --deep`** — adds a `prompt-engineer` deep description + security review and an `eval-judge` rubric calibration check
- **`fix-feedback`** — one WP per finding, grouped by severity and source kind; closes with a `fix-cycles/<stamp>.json` mapping every closed WP to its `finding_id`
- **`improve` / `refactor` / `migrate`** — targeted DEV → REVIEW → QA on the specified asset
- A run-log entry in `.ai-assets-memory/plugin-author/runs.log`

## The pipeline

Two shapes, chosen by the classifier:

- **SIMPLE** — single-pass, inline. Used for plain `audit` (no `--deep`) and trivial scaffolds.
- **HEAVY** — DEV → REVIEW → QA per [`@team-protocols`](../../skills/team-protocols/SKILL.md). Prefer **Path B** (Agent Teams via `TeamCreate`); fall back to **Path A** (single `Agent({...})` spawn loop) only on a documented technical block — **no silent fallback** for non-technical reasons.

Roles per asset kind:

| Asset | DEV | REVIEW |
|---|---|---|
| `plugin/skills/<name>/SKILL.md`, `plugin/agents/*.md`, `plugin/rules/*.md` | `prompt-engineer` | `prompt-engineer` (fresh, `disallowedTools: Write,Edit`) |
| `plugin/hooks/scripts/*.py` | `python-engineer` | `software-engineer` (same disallow) |
| `plugin/schemas/*.json` | `system-architect` | `software-engineer` |
| `plugin/eval/judge-rubrics/*.md`, `plugin/eval/calibration/**` | `eval-judge` | `prompt-engineer` |

QA on every WP is `qa-engineer` plus Lead-side automated post-checks: `python3 plugin/dev/validate.py`, internal audit at `--strict`, `/plugin-doctor`, and `/eval --skill <name> --tier 1` when the asset is a user-invocable workflow skill or a rubric.

## What `/feedback` ↔ `/plugin-author` looks like

```text
/feedback  →  feedback-2026-05-13-0910.md  +  feedback-2026-05-13-0910.json  (paired, full parity)
                                                                │
                                                                ▼
/plugin-author fix-feedback --from feedback-2026-05-13-0910.json
       → parses findings (JSON preferred; --md is degraded fallback)
       → resolves asset_hint per asset-to-role-map.md
       → builds WPs grouped by (asset, owner_role); sorted by severity
       → DEV → REVIEW → QA → Lead-side post-checks for every WP
       → writes fix-cycles/<stamp>.json closing each finding_id
```

## Common questions

**Why isn't there a `/plugin-skill-create` or `/plugin-skill-audit` anymore?**
They were absorbed into `/plugin-author` to give the plugin a single entry point per domain. Both still exist on disk as internal procedure docs (`disable-model-invocation: true`) and are read by the umbrella when scaffolding or auditing assets. If you used the old commands, replace them with `/plugin-author create <name>` and `/plugin-author audit <name>`.

**Can I bypass the umbrella and write SKILL.md directly?**
You can, but you lose the eval-loop closure, the counts hygiene, the audit gate, and the parity warnings. Use `/plugin-author` so the run is auditable.

**Is `/plugin-author audit --all --deep` safe to run?**
It is opt-in: the orchestrator prints a budget warning before starting because each target spawns at least one `prompt-engineer` and one `eval-judge`. For most maintenance work, run it against a single target.

**What does the `fix-feedback` JSON contract look like?**
Schema is documented in [`plugin/skills/plugin-author/feedback-parser.md`](../../skills/plugin-author/feedback-parser.md). Every finding produced by `/feedback` carries a `finding_id`, severity, source kind, signature, count, excerpt anchors, and (often) an `asset_hint`. The umbrella refuses to invent assets — if the resolver cannot find the file, it surfaces the mismatch and skips the WP.

**Where do logs go?**
`.ai-assets-memory/plugin-author/runs.log` (one JSON line per run) and, for `fix-feedback` only, `.ai-assets-memory/plugin-author/fix-cycles/<stamp>.json` mapping every closed WP to its `finding_id`.

## Examples

### Scaffold a new skill end-to-end
```bash
/plugin-author create release-notes --type workflow --agent-spawn
```
Scaffolds `plugin/skills/release-notes/`, kicks off an interview with you, runs a first DEV pass via `prompt-engineer`, creates a stub rubric and ≥ 6 calibration samples, runs `validate.py` + `/plugin-doctor` + `/eval --tier 1`, bumps `EXPECTED_COUNTS`.

### Deep audit of a single skill
```bash
/plugin-author audit feature-design --deep
```
Lint + `prompt-engineer` description/security review per `optimizing-descriptions.md` and `security-checklist.md` + `eval-judge` rubric coverage check. One WP; budget-friendly.

### Fix every finding in a feedback report
```bash
/feedback --days 7                                           # produces both .md and .json
/plugin-author fix-feedback --from .ai-assets-memory/feedback/feedback-2026-05-13-0910.json
```
The umbrella ingests the JSON, builds one WP per finding, drives the HEAVY pipeline, writes the fix-cycle JSON, and a re-run of `/feedback` against the same window confirms the closed findings drop to count: 0.

## Related

- [`/feedback`](../../skills/feedback/SKILL.md) — produces the input for `fix-feedback`
- [`/plugin-doctor`](../../skills/plugin-doctor/SKILL.md) — whole-plugin live diagnostic
- [`/eval`](../../skills/eval/SKILL.md) — rubric-based skill quality runs
- [`/learnings-write`](../../skills/learnings-write/SKILL.md) — invoked via `--learnings` to persist patterns to user-global memory
- [team-protocols](../../skills/team-protocols/SKILL.md) — spawn payload + return contract + role selection
- Internal procedure docs: `plugin/skills/plugin-skill-create/SKILL.md`, `plugin/skills/plugin-skill-audit/SKILL.md`
