# AI Assets

Reusable AI assets for Claude Code, Codex, and Windsurf.

Two delivery formats live in this repo:

1. **`plugin/`** — full Claude Code plugin (v0.2.0+). The canonical source of truth for Claude Code: 26 agents, 52 skills, 18 hooks, 17 eval rubrics + 102 calibration samples, 12 rules, 31 user-invocable workflows. Install via `claude --plugin-dir ./plugin` (local) or `/plugin marketplace add alex-voloshin/ai-assets` (after publishing). See [plugin/README.md](plugin/README.md) for full install + usage.
2. **`.codex/` + `.windsurf/` + `.agents/`** — copy-ready runtime folders for OpenAI Codex and Codeium Windsurf. Install via `install.sh` / `install.ps1`, which sync them into `~/.codex/`, `~/.windsurf/`, and `~/.agents/`.

The legacy `.claude/` package was removed in v0.2.0 — `plugin/` fully replaces it. Existing `~/.claude/` installs from earlier versions can be cleaned up with `rm -rf ~/.claude/agents ~/.claude/skills ~/.claude/rules ~/.claude/hooks ~/.claude/settings.json` (preserve any of your own personal `~/.claude/` content first).

## Documentation

| Document | Purpose |
|---|---|
| [plugin/README.md](plugin/README.md) | Claude Code plugin install, workflows, and what's inside |
| [plugin/CHANGELOG.md](plugin/CHANGELOG.md) | Plugin version history (v0.1.0 → current) |
| [CLAUDE.md](CLAUDE.md) | Claude Code instructions for working in this repo |
| [AGENTS.md](AGENTS.md) | Codex instructions, package layout, editing rules |
| [ARCHITECTURE.md](ARCHITECTURE.md) | System design, primitive mapping, hook architecture, installation flow |
| [PARITY.md](PARITY.md) | Cross-vendor parity model — Codex ↔ Windsurf parity (Claude Code lives in plugin/) |
| [TESTING.md](TESTING.md) | Validation approach, hook testing, parity checks |
| [review/parity-matrix.md](review/parity-matrix.md) | Change log and detailed parity tracking |

## Structure

```text
ai-assets/
├── plugin/                 # Claude Code plugin (v0.2.0+) — canonical source of truth for Claude Code
├── .agents/skills/         # 38 shared skills (Codex + Windsurf)
├── .codex/                 # Codex runtime package
├── .windsurf/              # Windsurf runtime package
├── review/                 # parity-matrix.md
├── plugin-design/          # historical plugin design docs (Phase 1-2 plan + checklists)
├── install.ps1             # PowerShell installer (Codex + Windsurf only — Windows)
└── install.sh              # bash installer (Codex + Windsurf only — Linux/macOS)
```

## Install

### Claude Code (plugin)

```bash
claude --plugin-dir /path/to/ai-assets/plugin
```

After editing plugin files in the same Claude Code session, reload without restarting:

```text
/reload-plugins
```

All 31 user-invocable skills appear in `/help` under the `ai-assets:` namespace, e.g. `/ai-assets:feature-design`, `/ai-assets:develop`, `/ai-assets:plugin-doctor`.

### Codex + Windsurf (legacy three-package)

Windows PowerShell:

```powershell
.\install.ps1
```

Linux/macOS:

```bash
./install.sh
```

The scripts sync `.agents/`, `.codex/`, `.windsurf/` into `~/.agents/`, `~/.codex/`, `~/.windsurf/` and remove stale files so the global packages stay aligned with the repo contents.

## Parity

The Codex and Windsurf packages must stay in sync with each other (38 shared skills via `.agents/skills/`, 22 roles, 8 rules + role overlays). Claude Code parity moved to `plugin/` in v0.2.0 — those assets follow the plugin's own internal organization rather than the three-package mirror. See [PARITY.md](PARITY.md) for the full model.

## Maintenance Rules

- keep all asset contents in English
- changes to Codex assets MUST be mirrored to Windsurf assets (and vice versa)
- changes to Claude Code assets land in `plugin/` only
- prefer runtime-native representations over forced file mirroring
- remove project-specific assumptions when importing assets from other repositories
- update `review/parity-matrix.md` for any Codex ↔ Windsurf parity-impacting change
