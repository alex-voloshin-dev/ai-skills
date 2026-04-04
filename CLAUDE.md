# AI Assets Repository

This repository stores reusable AI coding assistant configurations for three runtimes: Claude Code, OpenAI Codex, and Codeium Windsurf. It is not an application — it contains only Markdown, JSON, Python hook scripts, and shell installers.

## Quick Reference

```text
ai-assets/
├── .agents/skills/          # 38 skills (shared between Codex and Windsurf)
├── .claude/                  # Claude Code runtime package
│   ├── agents/              # 22 sub-agent definitions
│   ├── skills/              # 40 skills (38 shared + 2 Claude-only)
│   ├── rules/               # 7 guardrail rules
│   ├── hooks/scripts/       # 4 Python enforcement scripts
│   ├── hooks/configs/       # hook wiring fragments
│   ├── templates/           # 7 CLAUDE.md scaffolds per tech stack
│   └── settings.json        # global hook wiring
├── .codex/                   # Codex runtime package
│   ├── roles/               # 22 role definitions (mirrors .claude/agents/)
│   ├── rules/               # 8 rule files + 2 aliases + 5 role overlays
│   ├── operations/          # hook-intents, launch-reference, settings-mapping, source-sync, skill-role-mapping
│   ├── templates/           # 14 AGENTS.md scaffolds (includes parity aliases)
│   └── checklists/          # review checklists
├── .windsurf/                # Windsurf runtime package
│   ├── rules/roles/         # 22 role files (mirrors .claude/agents/)
│   ├── skills/              # 38 skills (mirrors .agents/skills/)
│   ├── workflows/           # 26 user-facing workflow files
│   ├── hooks/               # same 4 Python scripts + configs
│   └── hooks.json           # Windsurf-native hook wiring
├── review/parity-matrix.md  # cross-package alignment tracker
├── install.sh               # bash installer (Linux/macOS)
└── install.ps1              # PowerShell installer (Windows)
```

## Core Concepts

### Three-Package Parity

Every role, skill, and guardrail must exist in all three runtime packages. Changes must land in the same changeset across Claude, Codex, and Windsurf. The parity matrix (`review/parity-matrix.md`) tracks alignment.

Runtime primitives differ but capability coverage must match:
- Claude agents = Codex roles = Windsurf roles
- Claude skills = `.agents/skills/` = Windsurf skills
- Claude user-invocable skills = Windsurf workflows
- Claude hooks = Codex operations (documented intent) = Windsurf hooks

See [PARITY.md](PARITY.md) for the full parity model, current status, intentional gaps, and the process for adding new capabilities.

### Skill Format

Skills live in `<package>/skills/<name>/SKILL.md` with YAML frontmatter:
- `user-invocable: false` — background knowledge, loaded as context
- `context: fork` — user-invocable workflow (called via `/<skill-name>`)
- Resource files sit alongside `SKILL.md` in the same directory

### Hook Architecture

Four Python scripts in `.claude/hooks/scripts/` (mirrored to `.windsurf/hooks/scripts/`):
- `block-dangerous-commands.py` — PreToolUse(Bash): blocks destructive shell commands
- `block-secrets-in-code.py` — PreToolUse(Write|Edit): blocks secrets in code
- `block-sensitive-files.py` — PreToolUse(Read): blocks reading credential files
- `log-actions.py` — PostToolUse: structured audit logging

Exit code 2 = block, exit code 0 = allow.

### Installers

`install.sh` and `install.ps1` sync packages to `~/` and rewrite hook command paths to absolute `~/.claude/hooks/scripts/...` paths for global operation.

## Editing Rules

- all asset contents must be in English
- SKILL.md and rule files have a 12,000 character limit (skill resources have no hard limit but should stay focused)
- use relative runtime paths, never absolute user paths
- new roles/skills/guardrails must be added to all three packages simultaneously
- update `review/parity-matrix.md` for any parity-impacting change
- remove project-specific assumptions from shared assets
- prefer runtime-native representations over forced file mirroring
- the `@humanizer` skill must be applied to all public-facing content

## Common Tasks

| Task | What to do |
|---|---|
| Add a new skill | Create `SKILL.md` in `.claude/skills/`, `.agents/skills/`, `.windsurf/skills/`. Add workflow in `.windsurf/workflows/` if user-invocable. Update parity matrix |
| Add a new role | Create agent in `.claude/agents/`, role in `.codex/roles/`, role in `.windsurf/rules/roles/`. Update parity matrix |
| Add a new guardrail | Create rule in `.claude/rules/`, `.codex/rules/`, `.windsurf/rules/`. If hook-backed, add Python script + config |
| Update a hook script | Edit in `.claude/hooks/scripts/`, mirror to `.windsurf/hooks/scripts/`. Update `.codex/operations/hook-intents.md` |
| Add a template | Create in `.claude/templates/` and `.codex/templates/`. Windsurf embeds templates inside skill resources |
