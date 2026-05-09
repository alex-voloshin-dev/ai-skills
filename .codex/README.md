# Codex Package

This directory is the copy-ready Codex runtime package and the companion to the sibling `.agents/skills/` folder (shared with Windsurf).

## Contents

- `instructions.md` — package-level guidance for Codex
- `config.toml` — package metadata
- `roles/` — 22 Codex role references (mirrors `.windsurf/rules/roles/`)
- `rules/` — 8 Codex guardrails plus role-overlay rules
- `operations/` — documented equivalents to Windsurf hooks and Claude settings (Codex has no native hook execution)
- `templates/` — 14 AGENTS.md scaffolds and Codex-native authoring templates
- `checklists/` — review and validation aids

## Notes

- Copy this directory into a project root as `.codex/`
- Copy the sibling `.agents/skills/` directory along with it (Codex reads skill bodies from there)
- Parity is enforced between Codex and Windsurf only. Claude Code lives in `plugin/` and follows its own internal organization (the legacy `.claude/` mirror was retired in v0.2.0)