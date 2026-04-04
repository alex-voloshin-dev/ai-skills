# Claude Framework Summary

This summary captures the Claude Code primitives used by this repository.

## Rules

- Location in installed runtime: `rules/*.md`
- Format: markdown guidance files; hot-path files should stay within the package size guidance
- Use for reusable guardrails, authoring standards, and package-wide constraints

## Agents

- Location in installed runtime: `agents/*.md`
- Format: markdown files with frontmatter such as `name`, `description`, `tools`, and `model`
- Use for role-specialized agent prompts and routing

## Skills

- Location in installed runtime: `skills/<skill-name>/SKILL.md`
- Format: folder with `SKILL.md` plus supporting resource files
- Required frontmatter: `name`, `description`
- Optional fields used in this package include `user-invocable`, `context`, and `argument-hint`
- Use for reusable procedures, knowledge packs, and checklists

## Hooks

- Config fragments live under `hooks/configs/*.json`
- Scripts live under `hooks/scripts/*.py`
- Source package commands may use `.claude/hooks/scripts/...`; installers rewrite them to installed `~/.claude/hooks/scripts/...` paths

## Settings

- Workspace settings live in `settings.json`
- Keep hook-related commands aligned with the installed scripts and supported runtime behavior

## CLAUDE.md

- Root `CLAUDE.md` provides package-wide guidance
- Nested `CLAUDE.md` files scope guidance to a directory tree when a consuming project uses them

## This Package Mapping

- `agents/` is the Claude source of truth for role behavior
- `skills/` is the Claude source of truth for detailed user-facing workflows
- `rules/`, `hooks/`, and `settings.json` capture Claude-specific guardrails
- Sibling `.agents`, `.codex`, and `.windsurf` directories preserve the same capabilities in runtime-native formats
