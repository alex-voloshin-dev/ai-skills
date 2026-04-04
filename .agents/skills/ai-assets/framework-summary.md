# Codex Framework Summary

This summary captures the Codex primitives used by this repository.

## Shared Skills

- Location: `.agents/skills/<skill-name>/`
- Format: `SKILL.md` plus companion markdown resources
- Required frontmatter: `name`, `description`
- Optional frontmatter used here: `context`, `user-invocable`, `argument-hint`, `codex-roles`
- Use for reusable workflows, knowledge packs, templates, and checklists shared by Codex runtime consumers

## Roles

- Location: `.codex/roles/*.md`
- Format: markdown reference documents
- Use for detailed role scope, hard rules, competencies, and handoff boundaries
- These are the reference layer, not the hidden execution layer

## Role Overlays

- Location: `.codex/rules/role-overlays/*.md`
- Format: concise imperative markdown
- Use for the active execution layer when a skill declares `codex-roles`
- Every `codex-roles` value must resolve to both a role file and an overlay file

## Rules

- Location: `.codex/rules/*.md`
- Format: markdown guidance files
- Use for package-wide standards, guardrails, and visible runtime constraints
- Keep hot-path markdown concise and front-load hard rules

## Operations

- Location: `.codex/operations/*.md`
- Format: markdown mappings and intent docs
- Use for visible translations of Claude hook, settings, and launch behavior
- Codex has no hidden hook runtime in this package

## Templates and Checklists

- Location: `.codex/templates/*.md`, `.codex/checklists/*.md`
- Use templates for scaffolds and checklists for manual validation passes
- Prefer reusable structures over repo-specific examples

## `AGENTS.md`

- Root `AGENTS.md` provides package-wide guidance
- Scoped `AGENTS.md` files refine rules for a directory tree
- `AGENTS.md` should make role overlay activation explicit when a skill declares `codex-roles`

## Source-of-Truth Mapping

- `.claude/agents/` is the semantic source for role behavior
- `.claude/skills/` is the semantic source for workflow coverage and supporting knowledge
- `.claude/rules/`, `.claude/hooks/`, and `.claude/settings.json` define the source guardrail intent
- `.agents/skills/` plus `.codex/` preserve that intent in Codex-native form
