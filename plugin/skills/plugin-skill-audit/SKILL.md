---
name: plugin-skill-audit
description: Internal procedure for `/plugin-author audit`. Audit, validate, and update existing skills inside the ai-assets plugin (under `plugin/skills/`). Checks frontmatter against the agentskills.io specification, body length, progressive-disclosure structure, cross-reference integrity, eval-case wiring, and ai-assets plugin conventions. No longer slash-invocable — call `/plugin-author audit [<name> | --all] [--deep] [--strict] [--fix]` instead. Read by the `prompt-engineer` agent at task start when DEV-ing or reviewing a plugin skill (the safe-fix table and audit checks are the cached digest of upstream spec rules).
disable-model-invocation: true
---

# /plugin-skill-audit — Plugin Skill Auditor

Audit one or many skills in `plugin/skills/<name>/` against (1) the agentskills.io specification (https://agentskills.io/specification + best-practices) and (2) ai-assets plugin conventions. Produces a per-skill report with pass/warn/fail findings and, optionally, applies safe automatic fixes.

This skill is the audit/update counterpart to `/plugin-skill-create` (which scaffolds new skills). It NEVER creates new skills — for new skills, use `/plugin-skill-create`.

## When to use

- After editing one or more skills under `plugin/skills/`
- Before merging a PR that touches plugin skills
- When a skill stops triggering on prompts you expect (description audit)
- When migrating older skills to current conventions
- When `/plugin-doctor` reports skill-frontmatter issues and you want a deeper look

Not for: scaffolding new skills (use `/plugin-skill-create`); validating Codex/Windsurf assets (those use `.agents/skills/asset-validation/`); whole-plugin diagnostic (use `/plugin-doctor`).

## Invocation

```
/plugin-skill-audit                                 # audit every skill under plugin/skills/
/plugin-skill-audit --all                           # explicit equivalent
/plugin-skill-audit feature-design                  # audit one skill
/plugin-skill-audit feature-design --fix            # audit + apply safe auto-fixes
/plugin-skill-audit feature-design --check spec     # only frontmatter spec checks
/plugin-skill-audit --all --strict                  # warnings become failures
```

## Arguments

| Flag | Default | Effect |
|---|---|---|
| `<skill-name>` (positional) | `--all` | Audit a single skill folder under `plugin/skills/<name>/` |
| `--all` | implicit when no name given | Audit every skill under `plugin/skills/` |
| `--fix` | off | Apply only safe, deterministic fixes (see Safe-fix table). Never rewrites prose. |
| `--strict` | off | Warnings fail the run (CI-friendly) |
| `--check` | `all` | Restrict to a check group: `spec` (agentskills.io frontmatter only), `body` (size + structure), `refs` (cross-references), `eval` (eval/case + rubric wiring), `all` |

## Behavior

1. Resolve targets:
   - Single name: refuse if `plugin/skills/<name>/` does not exist; suggest `/plugin-skill-create <name>` if appropriate
   - `--all`: enumerate every immediate subdirectory of `plugin/skills/` containing a `SKILL.md`
2. For each target run the check groups (per `--check`):
   - **spec** — agentskills.io frontmatter spec
   - **body** — body size + progressive-disclosure structure
   - **refs** — cross-reference integrity
   - **eval** — eval-case + judge-rubric wiring
   - **plugin** — ai-assets plugin-specific conventions (H5 trigger, `context: fork`, etc.)
3. Print a per-skill report: `name | check | status | detail`
4. If `--fix`: apply only the safe, deterministic fixes from the Safe-fix table; re-run checks to confirm
5. Append an audit-log entry to `.ai-assets-memory/plugin-skill-audit.log`
6. Exit non-zero if any check failed (or any warned in `--strict`)

## agentskills.io specification checks (group `spec`)

Source of truth: https://agentskills.io/specification (fetched at audit time when network is available; otherwise applies the cached rules below).

Frontmatter — required fields:

- `name`
  - 1–64 characters
  - lowercase a–z, digits, hyphens only
  - must NOT start or end with a hyphen
  - must NOT contain consecutive hyphens (`--`)
  - MUST equal the parent directory name
- `description`
  - 1–1024 characters (hard limit per spec)
  - non-empty
  - **MUST NOT contain `TODO` token** (CRITICAL fail) — guards against unedited scaffolds from `/plugin-skill-create`
  - SHOULD describe both what the skill does AND when to use it
  - SHOULD include trigger keywords agents pattern-match against
  - SHOULD use imperative phrasing ("Use when…")
  - SHOULD focus on user intent, not implementation internals

Frontmatter — optional fields permitted by spec:

- `license` — name or path to bundled license
- `compatibility` — 1–500 chars, environment requirements
- `metadata` — string→string map
- `allowed-tools` — space-separated tool list (experimental; warn if used)

Frontmatter — Claude-Code-specific fields used by ai-assets (NOT in upstream spec but tolerated):

- `context: fork` — marks the skill as user-invocable via slash command
- `argument-hint` — argument hint shown in `/help`
- `disable-model-invocation: true` — knowledge-only skill

Any field NOT in the union of {spec optional, ai-assets tolerated} → warn.

## Body checks (group `body`)

- Body length ≤ 5000 tokens AND ≤ 500 lines (agentskills.io recommended) — warn beyond, fail beyond 1.5×
- Body length ≤ 12000 characters (ai-assets project rule) — fail beyond
- First H1 heading present and matches `# /<name>` or `# <Title>` form
- Recommended sections present (warn if missing): When to use, Invocation/Usage, Arguments (if `argument-hint`), Behavior, Failure modes, Integration
- Templates and long reference material moved out of `SKILL.md` into sibling files (warn if a single fenced code block > 80 lines remains inline)
- Procedures over declarations (heuristic: warn if body reads like a single concrete answer for one specific input rather than reusable steps)

## Cross-reference checks (group `refs`)

For every relative reference in `SKILL.md`:

- File-path references (`scripts/foo.py`, `references/REFERENCE.md`, `assets/template.md`) resolve under the skill directory
- `@<skill-name>` mentions resolve to an existing `plugin/skills/<name>/`
- `plugin/eval/judge-rubrics/<name>.md` reference resolves (if eval-wired)
- Hook script paths resolve under `plugin/hooks/scripts/`
- Schema paths resolve under `plugin/schemas/`
- No absolute user-machine paths (`/home/...`, `C:\Users\...`) — fail
- Reference depth ≤ 1 level from `SKILL.md` (agentskills.io best-practice) — warn if deeper

## Eval-wiring checks (group `eval`)

Optional but recommended for user-invocable workflow skills:

- `plugin/eval/cases/<name>/` exists with at least one case stub — warn if missing for a `context: fork` workflow skill
- `plugin/eval/judge-rubrics/<name>.md` exists when the skill is referenced in `plugin/eval/config.json` — fail otherwise
- Case JSON parses; required fields present (`case_id`, `skill`, `input`, `expected`)
- `judge_rubric` path resolves
- `judge_model` is one of {`haiku`, `sonnet`, `opus`}

## Plugin-convention checks (group `plugin` — runs as part of `all`)

- Description includes the H5 trigger pattern (`Use when …` or equivalent imperative)
- Description is third-person (no "I", "we", "you" narrating the skill itself)
- `context: fork` set when skill is intended as a slash command (heuristic: name maps to a workflow under `plugin/skills/`)
- `disable-model-invocation: true` only when paired with absence of `context: fork` (knowledge skill)
- Body avoids project-specific assumptions banned by `plugin/rules/global-package-rules.md`
- English-only (per repo CLAUDE.md)
- Resource files in the same skill folder are referenced from `SKILL.md` at least once (warn on orphans)

## Safe-fix table (`--fix`)

| Finding | Auto-fix |
|---|---|
| `name` missing → derived from folder name | Insert `name: <folder>` |
| `name` mismatch with folder name | Refuse — fail (renaming a skill is a behavior change, not a safe fix) |
| Trailing whitespace in frontmatter | Strip |
| Mixed line endings | Normalize to LF |
| Missing final newline | Append |
| `description` > 1024 chars | Refuse — needs human edit |
| Missing recommended section (When to use, etc.) | Insert empty heading placeholder with TODO marker |
| Orphan resource file | Refuse — leaves an inline comment listing the orphan |

`--fix` is conservative by design. It will never rewrite prose, rephrase descriptions, or move content between files.

## Report format

```
plugin-skill-audit report
==========================
target: <skill-name | --all>
mode:   <check-group>; fix=<on|off>; strict=<on|off>

<skill-name>
  spec      pass  name=<name>, description=<len>/1024 chars
  body      warn  body=<chars>/12000; <lines> lines
  refs      pass  3 references resolved
  eval      warn  no eval/cases/<name>/ stub
  plugin    pass

summary: N skills audited | P pass | W warn | F fail
```

When `--fix` runs, a second block lists every applied fix with the line range touched.

## Hard rules

- **Never rewrite skill prose** — automated fixes are limited to the Safe-fix table
- **Never rename a skill** automatically — `name` ↔ folder mismatch is always a fail, not a fix
- **Never invent eval cases** — only check that they exist and parse; case authoring stays a human task
- **Plugin-only scope** — `plugin/skills/` only. For `.agents/skills/` use `.agents/skills/asset-validation/`
- **Spec source of truth** is https://agentskills.io/specification — when the spec changes, update the cached rules in this skill
- **English-only** per repo CLAUDE.md

## Failure modes

- **Target not found:** report path; if name looks new, suggest `/plugin-skill-create <name>`
- **Network unavailable for live spec fetch:** fall back to cached rules, surface a warn
- **`SKILL.md` YAML frontmatter unparseable:** fail with the line number; refuse to apply any `--fix`
- **`--fix` would conflict with uncommitted changes:** refuse and ask for a clean working tree

## Memory writes

| Layer | When | Shape |
|---|---|---|
| L4 | After every audit run | Append one JSON line to `.ai-assets-memory/plugin-skill-audit.log` — timestamp, target, counts (pass/warn/fail), fixes applied |

## Integration

- **Status**: internal procedure document for `/plugin-author audit`. Not slash-invocable (frontmatter `disable-model-invocation: true`). The umbrella reads this file directly; `ai-assets:prompt-engineer` pre-reads it before any plugin-asset DEV or REVIEW pass (the safe-fix table + check groups are the cached digest of the upstream spec).
- **Reachable via**: `/plugin-author audit [<skill-name> | --all] [--deep] [--strict] [--fix] [--check spec|body|refs|eval|all]`
- **Reads**: `plugin/skills/<name>/SKILL.md`, sibling resource files, `plugin/eval/cases/<name>/`, `plugin/eval/judge-rubrics/<name>.md`, `plugin/eval/config.json`, `plugin/.claude-plugin/plugin.json`
- **Writes**: stdout report; `.ai-assets-memory/plugin-skill-audit.log`; (only with `--fix`) targeted edits per the safe-fix table.
- **Companion procedure**: `plugin/skills/plugin-skill-create/SKILL.md` — scaffold rules applied by `/plugin-author create`.
- **Whole-plugin diagnostic**: `/plugin-doctor`.
- **Spec reference**: https://agentskills.io/specification , https://agentskills.io/skill-creation/best-practices , https://agentskills.io/skill-creation/optimizing-descriptions , https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices
- **Codex/Windsurf analog**: `.agents/skills/asset-validation/` + `.codex/checklists/codex-asset-review.md` (parity-tracked in `review/parity-matrix.md`).
