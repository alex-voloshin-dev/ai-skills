# Windsurf Framework Summary

This summary captures the Windsurf primitives used by this repository.

## Rules

- Location: `.windsurf/rules/*.md`
- Format: markdown with frontmatter containing `trigger` and `description`
- Valid triggers: `always_on`, `model_decision`, `glob`, `manual`
- Use for short behavioral constraints, package guardrails, and role routing

## Skills

- Location: `.windsurf/skills/<skill-name>/SKILL.md`
- Format: folder with `SKILL.md` plus supporting files
- Frontmatter: `name`, `description`
- Windsurf uses progressive disclosure: only `name` and `description` are always loaded
- Use for reusable procedures that need checklists, references, templates, or scripts

## Workflows

- Location: `.windsurf/workflows/**/*.md`
- Format: markdown with a `description` frontmatter field
- Invocation: manual only via `/workflow-name`
- Workflows can call other workflows and reference skills

## AGENTS.md

- Root `AGENTS.md` files are treated as always-on rules
- Nested `AGENTS.md` files auto-scope to their directory tree
- Use AGENTS for directory-specific conventions and project facts

## Hooks

- Workspace hook config lives at `.windsurf/hooks.json`
- Hook scripts can live under `.windsurf/hooks/scripts/`
- Workspace hooks are version-controlled and merged with user/system hooks
- Important events used here: `pre_read_code`, `post_read_code`, `pre_write_code`, `post_write_code`, `pre_run_command`, `post_run_command`, `post_mcp_tool_use`

## This Package Mapping

- `.claude/agents` -> `.windsurf/rules/roles/**`
- `.claude/rules` + `.codex/rules` -> `.windsurf/rules/**`
- `.agents/skills` -> `.windsurf/skills/**`
- user-facing `.claude/skills` -> `.windsurf/workflows/**`
- `.claude/hooks` -> `.windsurf/hooks.json` + `.windsurf/hooks/scripts/`
- `.codex/templates`, `.codex/checklists`, `.codex/operations` -> skill support resources under `.windsurf/skills/ai-assets/`