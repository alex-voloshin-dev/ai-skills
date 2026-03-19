# Codex Instructions

This package defines the copy-ready Codex half of the shared AI asset repository.

## Runtime Model

In a consuming project, Codex assets land in:

- `.agents/skills/` for reusable task workflows
- `.codex/roles/` for role references
- `.codex/rules/` for explicit guardrails
- `.codex/operations/` for hook and settings intent
- `.codex/templates/` for reusable authoring scaffolds
- `.codex/checklists/` for manual review aids

This repository stores the runtime directories directly so they can be copied into a project without translation.

## Maintenance Rules

- prefer Codex-native representation over literal Claude emulation
- keep project-specific commands out of shared package docs
- maintain role parity with `../.claude/agents/`
- maintain skill parity with `../.claude/skills/`
- keep `.agents/skills/` and `.codex/` aligned as one runtime package