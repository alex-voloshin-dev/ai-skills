# AI Assets

Reusable AI assets for Claude Code, Codex, and Windsurf.

This repository is organized as copy-ready runtime folders. You can either copy `.claude`, `.agents`, `.codex`, and `.windsurf` manually into a target project, or use the installer scripts to sync the global packages into your user home directory.

## Structure

```text
ai-assets/
├── .claude/
├── .agents/
├── .codex/
├── .windsurf/
├── review/
├── install.ps1
└── install.sh
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

Both scripts also remove stale files inside those target directories so the global package stays aligned with the repository contents.
For Claude, the installer also rewrites global hook commands in `~/.claude/settings.json` to point at Python scripts inside `~/.claude/hooks/scripts`, so hooks do not depend on a project-local `.claude/` folder.

## Project Install

- copy `.claude/` into the target project root for Claude Code assets
- copy `.agents/` and `.codex/` into the target project root for Codex assets
- copy `.windsurf/` into the target project root for Windsurf assets

## Maintenance Rules

- keep `.claude/agents/` semantically aligned with `.codex/roles/`
- keep `.claude/skills/` semantically aligned with `.agents/skills/`
- keep `.windsurf/rules/roles/` semantically aligned with `.claude/agents/` and `.codex/roles/`
- keep `.windsurf/skills/` semantically aligned with `.agents/skills/`
- keep user-facing `.windsurf/workflows/` semantically aligned with actionable `.claude/skills/`
- prefer runtime-native representations over forced file mirroring
- remove project-specific assumptions when importing assets from other repositories
