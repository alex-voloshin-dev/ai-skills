# Codex Instructions

This package defines the copy-ready Codex half of the shared AI asset repository.

## Runtime Model

In a consuming project, Codex assets land in:

- `.agents/skills/` for reusable task workflows
- `.codex/roles/` for role references
- `.codex/rules/` for explicit guardrails and role overlays
- `.codex/operations/` for hook and settings intent
- `.codex/templates/` for reusable authoring scaffolds
- `.codex/checklists/` for manual review aids

This repository stores the runtime directories directly so they can be copied into a project without translation.

## Skill-to-Role Overlay Contract

Codex has no hidden agent runtime in this package. Role activation must stay visible in prompt-facing assets.

- `SKILL.md` files may declare `codex-roles` in YAML frontmatter
- `codex-roles` lists role ids from `.codex/roles/`
- each listed role must have a matching executable overlay under `.codex/rules/role-overlays/`
- consuming projects should activate the listed overlays from root or scoped `AGENTS.md`
- overlays are the runtime behavior layer; `.codex/roles/` remains the reference layer
- do not describe overlay activation as spawning a hidden sub-agent
- when adding a new role requirement to a skill, update the overlay, the mapping docs, and parity tracking in the same changeset

## Maintenance Rules

- prefer Codex-native representation over literal Claude emulation
- keep project-specific commands out of shared package docs
- maintain role parity with `../.claude/agents/`
- maintain skill parity with `../.claude/skills/`
- keep `.agents/skills/` and `.codex/` aligned as one runtime package
