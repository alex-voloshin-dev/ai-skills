# AI Assets Repository — Codex Instructions

This repository stores reusable AI coding assistant configurations for three runtimes: Claude Code, OpenAI Codex, and Codeium Windsurf. It is not an application — it contains only Markdown, JSON, Python hook scripts, and shell installers.

## Quick Reference

```text
ai-assets/
├── .agents/skills/          # 38 skills (shared between Codex and Windsurf)
├── .claude/                  # Claude Code runtime package
│   ├── agents/              # 22 sub-agent definitions
│   ├── skills/              # 40 skills (38 shared + 2 Claude-only)
│   ├── rules/               # guardrails
│   ├── hooks/               # Python enforcement scripts + configs
│   ├── templates/           # CLAUDE.md scaffolds per tech stack
│   └── settings.json        # global hook wiring
├── .codex/                   # Codex runtime package
│   ├── roles/               # 22 role definitions (mirrors .claude/agents/)
│   ├── rules/               # 8 rule files + role overlays
│   ├── operations/          # hook-intents, launch-reference, settings-mapping, source-sync
│   ├── templates/           # 14 AGENTS.md scaffolds
│   └── checklists/          # review checklists
├── .windsurf/                # Windsurf runtime package
│   ├── rules/roles/         # 22 role files (mirrors .claude/agents/)
│   ├── skills/              # 38 skills (mirrors .agents/skills/)
│   ├── workflows/           # 26 user-facing workflow files
│   └── hooks/               # Python scripts + configs
├── review/parity-matrix.md  # cross-package alignment tracker
├── install.sh               # bash installer (Linux/macOS)
└── install.ps1              # PowerShell installer (Windows)
```

## Core Concepts

### Three-Package Parity

Every role, skill, and guardrail must exist in all three runtime packages. Changes must land in the same changeset across Claude, Codex, and Windsurf. The parity matrix (`review/parity-matrix.md`) tracks alignment.

Capability mapping:
- Claude agents = Codex roles = Windsurf roles
- Claude skills = `.agents/skills/` = Windsurf skills
- Claude hooks = Codex operations (documented intent) = Windsurf hooks
- Claude templates = Codex templates = Windsurf skill resources

See [PARITY.md](PARITY.md) for the full parity model, current status, intentional gaps, and the process for adding new capabilities.

### Codex Package Layout

```text
.codex/
├── roles/              # role definitions (one per file)
├── rules/              # guardrails and standards
├── operations/         # hook intent docs, launch reference, settings mapping
├── templates/          # AGENTS.md scaffolds per tech stack
├── checklists/         # review checklists
├── config.toml         # package configuration
└── instructions.md     # maintenance rules
```

Codex has no native hook execution. `.codex/operations/hook-intents.md` documents what Claude hooks enforce so reviewers can verify intent compliance manually.

### Skill Format

Skills live in `.agents/skills/<name>/SKILL.md` with YAML frontmatter. Resource files sit alongside the skill file. Codex and Windsurf both read from `.agents/skills/`.

### Installers

`install.sh` and `install.ps1` sync all four directories to `~/` and rewrite hook paths to absolute for global operation.

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
| Add a new guardrail | Create rule in `.claude/rules/`, `.codex/rules/`, `.windsurf/rules/`. If hook-backed, update `.codex/operations/hook-intents.md` |
| Add a template | Create in `.claude/templates/` and `.codex/templates/`. Windsurf embeds templates inside skill resources |
