---
name: plugin-skill-audit
description: Internal procedure for `/plugin-author audit`. Audit, validate, and update existing skills inside the ai-skills plugin (under `plugin/skills/`). Checks frontmatter against the agentskills.io specification, body length, progressive-disclosure structure, cross-reference integrity, eval-case wiring, and ai-skills plugin conventions. No longer slash-invocable — call `/plugin-author audit [<name> | --all] [--deep] [--strict] [--fix]` instead. Use when auditing, validating, or fixing an existing plugin skill's frontmatter, body length, progressive-disclosure structure, cross-references, or eval wiring — after editing skills under `plugin/skills/`, before merging a PR that touches them, or when a skill stops triggering as expected. Read by the `prompt-engineer` agent at task start when DEV-ing or reviewing a plugin skill (the safe-fix table and audit checks are the cached digest of upstream spec rules).
disable-model-invocation: true
---

# /plugin-skill-audit — Plugin Skill Auditor

Audit skills in `plugin/skills/<name>/` against the agentskills.io spec + best-practices and ai-skills conventions. Emits a per-skill pass/warn/fail report and optionally applies safe fixes. Counterpart to `/plugin-skill-create`; NEVER creates skills.

## When to use

- After editing skills under `plugin/skills/`, or before merging a PR that touches them
- When a skill stops triggering on prompts you expect (description audit)
- When migrating older skills to current conventions, or when `/plugin-doctor` flags frontmatter

Not for: scaffolding new skills (use `/plugin-skill-create`); Codex/Windsurf assets (`.agents/skills/asset-validation/`); whole-plugin diagnostic (`/plugin-doctor`).

## Invocation

```
/plugin-skill-audit                            # audit every skill (== --all)
/plugin-skill-audit feature-design             # audit one skill
/plugin-skill-audit feature-design --fix       # + apply safe auto-fixes
/plugin-skill-audit feature-design --check scripts  # only scripts/ checks
/plugin-skill-audit --all --strict             # warnings become failures
```

## Arguments

| Flag | Default | Effect |
|---|---|---|
| `<skill-name>` (positional) | `--all` | Audit a single skill folder under `plugin/skills/<name>/` |
| `--all` | implicit when no name given | Audit every skill under `plugin/skills/` |
| `--fix` | off | Apply only safe, deterministic fixes (see Safe-fix table). Never rewrites prose. |
| `--strict` | off | Warnings fail the run (CI-friendly) |
| `--check` | `all` | Restrict to a check group: `spec` (agentskills.io frontmatter only), `body` (size + structure), `refs` (cross-references), `eval` (eval/case + rubric wiring), `scripts` (`scripts/` agentic-use), `all` |

## Behavior

1. Resolve targets:
   - Single name: refuse if `plugin/skills/<name>/` does not exist; suggest `/plugin-skill-create <name>` if appropriate
   - `--all`: enumerate every immediate subdirectory of `plugin/skills/` containing a `SKILL.md`
2. For each target run the check groups (per `--check`):
   - **spec** — agentskills.io frontmatter spec
   - **body** — body size + progressive-disclosure structure
   - **refs** — cross-reference integrity
   - **eval** — eval-case + judge-rubric wiring
   - **scripts** — `scripts/` agentic-use checks (skipped if the skill has no `scripts/` dir)
   - **plugin** — ai-skills plugin-specific conventions (H5 trigger, `context: fork`, etc.)
3. Print a per-skill report: `name | check | status | detail`
4. If `--fix`: apply only the safe, deterministic fixes from the Safe-fix table; re-run checks to confirm
5. Append an audit-log entry to `.ai-skills-memory/plugin-skill-audit.log`
6. Exit non-zero if any check failed (or any warned in `--strict`)

## agentskills.io specification checks (group `spec`)

Source of truth: digest `prompt-engineering/skill-authoring-spec.md`; only audit verdicts below (progressive disclosure — field rules live in the digest).

Frontmatter — required fields:

- `name` — `fail` if not 1–64 chars / not lowercase a–z+digits+hyphens / leading-trailing or consecutive (`--`) hyphen / not equal to the parent directory name (mismatch is always `fail`, never `--fix`)
- `description` — `fail` if not 1–1024 chars or empty; **CRITICAL fail if it contains the `TODO` token**; `warn` if missing what+when, trigger keywords, or imperative "Use when…" phrasing (see `prompt-engineering/optimizing-descriptions.md`)

Frontmatter — optional fields permitted by spec:

- `license` — name or path to a bundled license
- `compatibility` — spec cap 1–500 chars; `warn` if > 500 chars OR if present without an actual runtime/environment requirement; absent is fine
- `metadata` — string→string map (warn on non-string values)
- `allowed-tools` — space-separated tool list (experimental; warn if used)

ai-skills-tolerated (not upstream): `context: fork` (slash-invocable), `argument-hint` (`/help` hint), `disable-model-invocation: true` (knowledge-only). Any field outside {spec-optional ∪ ai-skills-tolerated} → `warn`.

## Body checks (group `body`)

- ≤ 5000 tokens AND ≤ 500 lines (digest recommended) — `warn` beyond, `fail` beyond 1.5×; ≤ 12000 chars (ai-skills rule) — `fail` beyond
- First H1 present, matching `# /<name>` or `# <Title>`
- Recommended sections present (`warn` if missing): When to use, Invocation, Arguments (if `argument-hint`), Behavior, Failure modes, Integration
- Long templates moved to sibling files (`warn` if an inline fenced block > 80 lines)
- Procedures over declarations (`warn` if body reads as one concrete answer, not reusable steps)

## Cross-reference checks (group `refs`)

Per relative reference in `SKILL.md`:

- File-path refs (`scripts/`, `references/`, `assets/`) resolve under the skill dir; `@<skill-name>` resolves to an existing `plugin/skills/<name>/`; eval-rubric / hook / schema paths resolve under their roots
- No absolute user-machine paths (`/home/...`, `C:\Users\...`) — `fail`
- Reference depth ≤ 1 level from `SKILL.md` (digest best-practice) — `warn` if deeper

## Eval-wiring checks (group `eval`)

- `plugin/eval/cases/<name>/` has ≥1 case stub — `warn` if missing for a `context: fork` skill
- `plugin/eval/judge-rubrics/<name>.md` exists when referenced in `plugin/eval/config.json` — `fail` otherwise
- Case JSON parses with required fields (`case_id`, `skill`, `input`, `expected`); `judge_rubric` path resolves; `judge_model` ∈ {`haiku`, `sonnet`, `opus`}

## Script checks (group `scripts`; part of `all`; skipped if no `scripts/` dir)

Selectable via `--check scripts`; runs inside `all`. Per file under `scripts/` (digest "Using scripts in skills"):

- Referenced from `SKILL.md` & resolves under the skill dir — `fail` if dangling; unreferenced — `warn`
- No interactive / TTY-blocking read or prompt — `warn`
- `--help`/usage path documented — `warn` if absent
- Structured data → stdout, diagnostics → stderr — `warn` if mixed
- Documented exit codes; `--dry-run` for destructive ops; idempotent — `warn` if absent
- Predictable output size (summary default / `--offset` / `--output`) — `warn` if unbounded
- Pinned inline deps (PEP 723 / `npm:`+semver / `bundler/inline`) — `warn` on missing/floating; runtime prerequisite in `SKILL.md` or `compatibility` — `warn` if neither

## Plugin-convention checks (group `plugin` — runs as part of `all`)

- Description carries the H5 `Use when …` pattern and is third-person — `warn` otherwise
- `context: fork` for a slash command; `disable-model-invocation: true` only with no `context: fork`
- No project-specific assumptions banned by `plugin/rules/global-package-rules.md`; English-only
- Sibling resource files referenced from `SKILL.md` ≥ once — `warn` on orphans

## Safe-fix table (`--fix`)

| Finding | Auto-fix |
|---|---|
| `name` missing → derived from folder name | Insert `name: <folder>` |
| `name` mismatch with folder name | Refuse — fail (renaming a skill is a behavior change, not a safe fix) |
| Trailing whitespace in frontmatter | Strip |
| Mixed line endings | Normalize to LF |
| Missing final newline | Append |
| `description` > 1024 chars | Refuse — needs human edit |
| `compatibility` > 500 chars | Refuse — needs human edit |
| UTF-8 BOM at file start | Strip (deterministic) |
| Missing recommended section (When to use, etc.) | Insert empty heading placeholder with TODO marker |
| Orphan resource file | Refuse — leaves an inline comment listing the orphan |
| Any `scripts/` finding (interactive, missing `--help`, exit codes, deps) | Refuse — script behavior is never auto-fixed (conservative discipline) |

`--fix` never rewrites prose, rephrases descriptions, or moves content between files.

## Report format

```
plugin-skill-audit report — target: <name|--all>; fix=<on|off>; strict=<on|off>
<skill-name>
  spec pass  name=<name>, description=<len>/1024
  body warn  body=<chars>/12000; <lines> lines
  refs pass  3 references resolved
  eval warn  no eval/cases/<name>/ stub
  plugin pass
summary: N audited | P pass | W warn | F fail
```

When `--fix` runs, a second block lists every applied fix with the line range touched.

## Hard rules

- **Never rewrite skill prose** — fixes limited to the Safe-fix table
- **Never rename a skill** — `name`↔folder mismatch is always a fail, never a fix
- **Never invent eval cases** — only check they exist and parse
- **Plugin-only scope** — `plugin/skills/` only (`.agents/skills/` → `asset-validation/`)
- **Spec source of truth** is the digest `prompt-engineering/skill-authoring-spec.md` (+ `optimizing-descriptions.md`) — update the digest, never re-inline here
- **English-only** per repo CLAUDE.md

## Failure modes

- **Target not found:** report path; if name looks new, suggest `/plugin-skill-create <name>`
- **Network unavailable:** fall back to cached digest, surface a `warn`
- **Unparseable YAML frontmatter:** `fail` with the line number; refuse any `--fix`
- **`--fix` vs uncommitted changes:** refuse, ask for a clean working tree

## Memory writes

| Layer | When | Shape |
|---|---|---|
| L4 | After every run | Append a JSON line to `.ai-skills-memory/plugin-skill-audit.log` — ts, target, counts, fixes |

## Integration

- **Status**: internal procedure for `/plugin-author audit`. Not slash-invocable. The umbrella reads it directly; `ai-skills:prompt-engineer` pre-reads it before any plugin-asset DEV/REVIEW pass.
- **Reachable via**: `/plugin-author audit [<name> | --all] [--deep] [--strict] [--fix] [--check spec|body|refs|eval|scripts|all]`
- **Reads**: `plugin/skills/<name>/SKILL.md`, sibling resource files, `plugin/eval/cases/<name>/`, `plugin/eval/judge-rubrics/<name>.md`, `plugin/eval/config.json`, `plugin/.claude-plugin/plugin.json`
- **Writes**: stdout report; `.ai-skills-memory/plugin-skill-audit.log`; (only with `--fix`) safe-fix-table edits.
- **Companion**: `plugin/skills/plugin-skill-create/SKILL.md`. **Whole-plugin diagnostic**: `/plugin-doctor`.
- **Spec reference (cached, offline source of truth)**: `prompt-engineering/skill-authoring-spec.md` , `prompt-engineering/optimizing-descriptions.md` — mirroring https://agentskills.io/specification + /skill-creation/{best-practices,optimizing-descriptions,using-scripts}
- **Codex/Windsurf analog**: `.agents/skills/asset-validation/` + `.codex/checklists/codex-asset-review.md` (parity-tracked in `review/parity-matrix.md`).
