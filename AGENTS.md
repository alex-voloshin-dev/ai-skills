# AI Assets Repository — Codex Instructions

This repository ships AI coding assistant configurations in two delivery formats:

1. **`plugin/`** — full Claude Code plugin (v0.2.0+, canonical source of truth for Claude Code).
2. **`.codex/` + `.windsurf/` + `.agents/`** — copy-ready three-package layout for OpenAI Codex and Codeium Windsurf (your runtime).

The legacy `.claude/` package was removed in v0.2.0 — `plugin/` fully replaces it for Claude Code. This file is your (Codex's) instructions for working in the `.codex/` and shared `.agents/` directories.

## Quick Reference

```text
ai-assets/
├── plugin/                  # Claude Code plugin — DO NOT MIRROR INTO .codex/
├── .agents/skills/          # 38 skills (shared between Codex and Windsurf)
├── .codex/                   # Codex runtime package (your home)
│   ├── roles/               # 22 role definitions (mirrors .windsurf/rules/roles/)
│   ├── rules/               # 8 rule files + role overlays
│   ├── operations/          # hook-intents, launch-reference, settings-mapping, source-sync
│   ├── templates/           # 14 AGENTS.md scaffolds
│   └── checklists/          # review checklists
├── .windsurf/                # Windsurf runtime package (parity target)
│   ├── rules/roles/         # 22 role files (mirrors .codex/roles/)
│   ├── skills/              # 38 skills (mirrors .agents/skills/)
│   ├── workflows/           # 26 user-facing workflow files
│   └── hooks/               # Python scripts + configs
├── review/parity-matrix.md  # Codex ↔ Windsurf alignment tracker
├── install.sh               # bash installer (Codex + Windsurf only — Linux/macOS)
└── install.ps1              # PowerShell installer (Codex + Windsurf only — Windows)
```

## Core Concepts

### Two-Vendor Parity (Codex ↔ Windsurf)

After v0.2.0, parity is enforced between Codex and Windsurf only — Claude Code lives in `plugin/` and follows its own internal organization. Every role, skill, and guardrail in `.codex/` must have a matching entry in `.windsurf/`. The parity matrix (`review/parity-matrix.md`) tracks alignment.

Capability mapping:
- Codex roles = Windsurf roles
- `.agents/skills/` = `.windsurf/skills/`
- Codex operations (documented intent) = Windsurf hooks (scripts + hooks.json)
- Codex templates = Windsurf skill-embedded resources

See [PARITY.md](PARITY.md) for the full parity model.

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

Codex has no native hook execution. `.codex/operations/hook-intents.md` documents what the equivalent Windsurf/Claude Code hooks enforce so Codex reviewers can verify intent compliance manually.

### Skill Format

Skills live in `.agents/skills/<name>/SKILL.md` with YAML frontmatter. Resource files sit alongside the skill file. Codex and Windsurf both read from `.agents/skills/`.

### Installers

`install.sh` and `install.ps1` sync `.agents/`, `.codex/`, `.windsurf/` to `~/`. Claude Code is installed separately via `claude --plugin-dir ./plugin` (not these scripts).

## Editing Rules

- all asset contents must be in English
- SKILL.md and rule files have a 12,000 character limit (skill resources have no hard limit but should stay focused)
- use relative runtime paths, never absolute user paths
- new Codex roles/skills/guardrails must be added to Windsurf simultaneously (and vice versa)
- new plugin assets land in `plugin/` only — there is no longer a `.claude/` mirror to keep in sync
- update `review/parity-matrix.md` for any Codex ↔ Windsurf parity-impacting change
- remove project-specific assumptions from shared assets
- prefer runtime-native representations over forced file mirroring
- the `@humanizer` skill must be applied to all public-facing content

## Common Tasks

| Task | What to do |
|---|---|
| Add a Codex/Windsurf skill | Create `SKILL.md` in `.agents/skills/` and `.windsurf/skills/`. Add workflow in `.windsurf/workflows/` if user-invocable. Update parity matrix |
| Add a Codex/Windsurf role | Create role in `.codex/roles/`, role in `.windsurf/rules/roles/`. Update parity matrix |
| Add a Codex/Windsurf guardrail | Create rule in `.codex/rules/`, `.windsurf/rules/`. If hook-backed, document intent in `.codex/operations/hook-intents.md` and add Python script + config in `.windsurf/hooks/` |
| Add a Codex template | Create in `.codex/templates/`. Windsurf embeds templates inside skill resources |
| Touch Claude Code assets | Edit in `plugin/` directly — do NOT mirror into `.codex/` or `.windsurf/` |
