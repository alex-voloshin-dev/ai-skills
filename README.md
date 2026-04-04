# AI Assets

Reusable AI assets for Claude Code, Codex, and Windsurf.

This repository is organized as copy-ready runtime folders. You can either copy `.claude`, `.agents`, `.codex`, and `.windsurf` manually into a target project, or use the installer scripts to sync the global packages into your user home directory.

## Documentation

| Document | Purpose |
|---|---|
| [CLAUDE.md](CLAUDE.md) | Claude Code instructions, quick reference, editing rules |
| [AGENTS.md](AGENTS.md) | Codex instructions, package layout, editing rules |
| [ARCHITECTURE.md](ARCHITECTURE.md) | System design, primitive mapping, hook architecture, installation flow |
| [PARITY.md](PARITY.md) | Cross-vendor parity model, current status, intentional gaps, how to add capabilities |
| [TESTING.md](TESTING.md) | Validation approach, hook testing, parity checks |
| [review/parity-matrix.md](review/parity-matrix.md) | Change log and detailed parity tracking |

## Structure

```text
ai-assets/
├── .agents/skills/      # 38 shared skills (Codex + Windsurf)
├── .claude/              # Claude Code runtime package
├── .codex/               # Codex runtime package
├── .windsurf/            # Windsurf runtime package
├── review/               # parity-matrix.md
├── install.ps1           # PowerShell installer (Windows)
└── install.sh            # bash installer (Linux/macOS)
```

## Global Install

Windows PowerShell:

```powershell
.\install.ps1
```

Linux/macOS:

```bash
./install.sh
```

By default the scripts sync:

- `.claude` -> `~/.claude`
- `.agents` -> `~/.agents`
- `.codex` -> `~/.codex`
- `.windsurf` -> `~/.windsurf`

Both scripts also remove stale files inside those target directories so the global package stays aligned with the repository contents. For Claude, the installer also rewrites global hook commands in `~/.claude/settings.json` to point at Python scripts inside `~/.claude/hooks/scripts`, so hooks do not depend on a project-local `.claude/` folder.

## Project Install

- copy `.claude/` into the target project root for Claude Code assets
- copy `.agents/` and `.codex/` into the target project root for Codex assets
- copy `.windsurf/` into the target project root for Windsurf assets

## Parity

Every role, skill, and guardrail exists in all three packages. See [PARITY.md](PARITY.md) for the full model and current status.

## Maintenance Rules

- keep all asset contents in English
- new roles/skills/guardrails must be added to all three packages simultaneously
- prefer runtime-native representations over forced file mirroring
- remove project-specific assumptions when importing assets from other repositories
- update `review/parity-matrix.md` for any parity-impacting change
