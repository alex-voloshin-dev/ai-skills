# AI Assets Repository

This repository ships AI coding assistant configurations in two delivery formats:

1. **`plugin/`** — full Claude Code plugin (canonical source of truth for Claude Code; current version in `plugin/.claude-plugin/plugin.json`).
2. **`.codex/` + `.windsurf/` + `.agents/`** — copy-ready three-package layout for OpenAI Codex and Codeium Windsurf (.agents/ holds skills shared between Codex and Windsurf).

The legacy `.claude/` package was removed in v0.2.0 — `plugin/` fully replaces it for Claude Code.

## Quick Reference

```text
ai-assets/
├── plugin/                  # Claude Code plugin
│   ├── .claude-plugin/
│   │   └── plugin.json      # manifest + 13 userConfig knobs
│   ├── agents/              # 26 specialized agents
│   ├── skills/              # 75 skills (31 user-invocable + 5 main-thread orchestrators)
│   ├── rules/               # 12 guardrail rules
│   ├── hooks/               # 19 hooks across 14 lifecycle events
│   ├── schemas/             # 2 JSON Schemas (G7 spawn + return)
│   ├── eval/                # 47 rubrics + 282 calibration samples + Tier 1/2 runners + g1g2 attack-surface
│   ├── docs/                # 16 user docs (1 getting-started + 11 workflows + 4 concepts)
│   └── dev/validate.py      # local validator (25 checks)
├── .agents/skills/          # 39 skills (shared by Codex + Windsurf)
├── .codex/                  # Codex runtime package
│   ├── roles/               # 22 role definitions
│   ├── rules/               # 8 rule files + role overlays
│   ├── operations/          # hook-intents, launch-reference, settings-mapping, source-sync, skill-role-mapping
│   ├── templates/           # 14 AGENTS.md scaffolds
│   └── checklists/          # review checklists
├── .windsurf/               # Windsurf runtime package
│   ├── rules/roles/         # 22 role files (mirrors .codex/roles/)
│   ├── skills/              # 39 skills (mirrors .agents/skills/)
│   ├── workflows/           # 27 user-facing workflow files
│   ├── hooks/               # Python scripts + configs
│   └── hooks.json           # Windsurf-native hook wiring
├── .claude-plugin/marketplace.json  # marketplace manifest pointing at ./plugin
├── review/parity-matrix.md  # cross-package alignment tracker (Codex ↔ Windsurf)
├── plugin-design/           # historical plugin design docs
├── install.sh               # bash installer (Codex + Windsurf only — Linux/macOS)
└── install.ps1              # PowerShell installer (Codex + Windsurf only — Windows)
```

## Core Concepts

### Two-Vendor Parity (Codex + Windsurf)

After v0.2.0, parity is enforced between Codex and Windsurf only — Claude Code lives in `plugin/` and follows its own internal organization (no longer mirrored into a sibling top-level package). Every role, skill, and guardrail in `.codex/` must have a matching entry in `.windsurf/`. The parity matrix (`review/parity-matrix.md`) tracks alignment.

Runtime primitives differ but capability coverage must match:
- Codex roles = Windsurf roles
- `.agents/skills/` = `.windsurf/skills/`
- Codex operations (documented intent) = Windsurf hooks (scripts + hooks.json)

See [PARITY.md](PARITY.md) for the full parity model.

### Claude Code lives in plugin/

For Claude Code, the plugin layout supersedes the old `.claude/` package. To use this repo's Claude Code assets:

```bash
claude --plugin-dir /path/to/ai-assets/plugin
```

After editing plugin files in the same Claude Code session, reload without restarting:

```text
/reload-plugins
```

All 31 forked + 5 main-thread orchestrator skills (= 36 user-invocable surface) appear in `/help` under the `ai-assets:` namespace.

### Skill Format

Skills live in `<package>/skills/<name>/SKILL.md` with YAML frontmatter:
- `user-invocable: false` — background knowledge, loaded as context
- `context: fork` — user-invocable workflow (called via `/<skill-name>`)
- Resource files sit alongside `SKILL.md` in the same directory

### Hook Architecture

In the plugin (`plugin/hooks/scripts/`): 18 Python scripts across 13 lifecycle events, all importing the shared `_lib.py`. See `plugin/hooks/README.md`.

In the Codex/Windsurf packages: 4 carried-over Python scripts in `.windsurf/hooks/scripts/` mirror the security/audit hooks. Codex declares the same intent declaratively in `.codex/operations/hook-intents.md`.

Exit code 2 = block, exit code 0 = allow.

### Installers

`install.sh` and `install.ps1` sync the Codex + Windsurf + shared-skills packages to `~/`. Claude Code is no longer installed via these scripts (v0.2.0+) — use `claude --plugin-dir` instead.

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
| Add a Claude Code skill | Create `SKILL.md` in `plugin/skills/<name>/`. Update `plugin/dev/validate.py` `EXPECTED_COUNTS` if needed |
| Add a Claude Code agent | Create `plugin/agents/<name>.md`. Update `EXPECTED_COUNTS["agents"]` if shipping permanent role |
| Add a Claude Code hook | Create `plugin/hooks/scripts/<name>.py`, wire into `plugin/hooks/hooks.json`, bump `EXPECTED_COUNTS["hooks"]` |
| Add a Codex/Windsurf skill | Create `SKILL.md` in `.agents/skills/` and `.windsurf/skills/`. Add workflow in `.windsurf/workflows/` if user-invocable. Update parity matrix |
| Add a Codex/Windsurf role | Create role in `.codex/roles/`, role in `.windsurf/rules/roles/`. Update parity matrix |
| Add a Codex/Windsurf guardrail | Create rule in `.codex/rules/`, `.windsurf/rules/`. If hook-backed, add Python script + config in `.windsurf/hooks/` and document intent in `.codex/operations/hook-intents.md` |
| Add a Codex template | Create in `.codex/templates/`. Windsurf embeds templates inside skill resources |
