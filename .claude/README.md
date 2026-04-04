# Claude Package

This directory is a copy-ready Claude Code runtime package.

## Contents

- `CLAUDE.md` for package-level guidance
- `agents/` for Claude agent prompts
- `rules/` for Claude rules and authoring standards
- `skills/` for Claude skills and companion resources
- `hooks/` for Claude hook configs and scripts
- `settings.json` for Claude runtime settings
- `templates/` for Claude-oriented templates

## Notes

- installers sync this package into `~/.claude/`
- hook commands are rewritten at install time to absolute `~/.claude/hooks/scripts/...` paths
- semantic parity with Codex is a source-repository maintenance rule, not an installed-runtime requirement
