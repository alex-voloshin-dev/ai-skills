---
name: ai-assets
description: Create, modify, validate, and analyze Codex-native AI assets such as AGENTS.md files, shared skills, roles, rules, operations, templates, and checklists.
codex-roles:
  - prompt-engineer
---

# AI Assets

Use this skill when building or maintaining the Codex half of this repository. Treat every asset as live prompt surface and preserve semantic parity with `.claude/` without copying Claude-only runtime primitives directly.

## 1. Determine Scope

Identify:

- Operation: `create` | `modify` | `validate` | `analyze`
- Asset type: `agents-md` | `skill` | `role` | `rule` | `operation` | `template` | `checklist`
- Target path or asset name

If the request is ambiguous, resolve it from repository context before asking the user.

## 2. Gather Context

Read only what is required for the target:

1. The target asset, if it exists
2. Root `AGENTS.md`
3. Relevant files under `.codex/`
4. Relevant files under `.agents/skills/`
5. The matching Claude source under `.claude/` when parity is in scope
6. `framework-summary.md` for the Codex package layout and primitive mapping
7. `context-engineering` when the asset affects prompt layering, routing, memory, RAG, or orchestration

## 3. Build a Dependency Map

Map outgoing and incoming references.

Check for:

- References to `AGENTS.md`
- References to `.agents/skills/<name>/`
- References to `.codex/roles/`, `.codex/rules/`, `.codex/operations/`, `.codex/templates/`, or `.codex/checklists/`
- Missing files
- Orphaned assets
- Duplicate or stale aliases
- Claude-only concepts that were not translated into Codex-native form

For `analyze`, stop after presenting the dependency map.

## 4. Choose the Right Codex Primitive

Use the smallest Codex-native asset that matches the job:

- Repository or directory policy -> `AGENTS.md`
- Reusable workflow or knowledge -> `.agents/skills/<name>/SKILL.md`
- Reference role -> `.codex/roles/<name>.md`
- Executable role behavior layer -> `.codex/rules/role-overlays/<name>.md`
- Guardrail or package standard -> `.codex/rules/<name>.md`
- Hook/settings translation -> `.codex/operations/*.md`
- Reusable scaffold -> `.codex/templates/*.md`
- Manual validation aid -> `.codex/checklists/*.md` or companion markdown inside a skill

Do not recreate Claude-specific primitives such as agent files, hook configs, or `settings.json` inside the Codex package.

## 5. Authoring Rules

### `AGENTS.md`

- Put hard constraints first
- Keep project facts concrete and current
- Keep root guidance global and scoped guidance local
- Make role overlay activation visible when a skill declares `codex-roles`

### `SKILL.md`

- Required frontmatter: `name`, `description`
- Optional fields: `context`, `user-invocable`, `argument-hint`, `codex-roles`
- `description` should trigger the right workflow, not every vaguely related task
- `codex-roles` must resolve to both `.codex/roles/` and `.codex/rules/role-overlays/`
- Move bulky examples and checklists into companion files

### Roles and Overlays

- `.codex/roles/` is the detailed reference layer
- `.codex/rules/role-overlays/` is the concise execution layer
- Do not describe overlays as hidden agents
- Keep overlays imperative, short, and testable

### Rules, Operations, Templates, Checklists

- Keep policy separate from examples
- Keep hook intent visible in documentation instead of implying hidden automation
- Prefer reusable structures over repo-specific examples
- Remove machine-specific paths and project-specific commands

## 6. Prompt Engineering Review

Review the asset as live Codex context:

1. What behavior does it shape?
2. What failure mode does it prevent or enable?
3. Is the instruction hierarchy clear?
4. Is critical information front-loaded?
5. Is the token cost justified?
6. Does it stay Codex-native while preserving Claude-source intent?

Use `review-checklist.md` for the final pass.

## 7. Validate

Run these checks on every create or modify operation:

- Asset uses Codex-native concepts only
- References resolve
- `codex-roles` values resolve to both role and overlay files
- No machine-specific paths unless intentionally local documentation
- No secrets or credentials
- English only
- `SKILL.md` stays concise enough for progressive disclosure
- No stale Claude aliases or duplicate guardrails remain
- Parity-impacting changes update `review/parity-matrix.md`

## 8. Finalize

Report:

- What changed
- Dependency status
- Validation result
- Remaining follow-up items
