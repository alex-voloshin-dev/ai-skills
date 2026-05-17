# Windsurf Package

This directory is the copy-ready Windsurf runtime package for the `ai-skills` repository.

## Runtime Layout

```text
.windsurf/
├── README.md
├── hooks.json
├── hooks/
│   ├── configs/
│   └── scripts/              # 4 carry-over security/audit hooks
├── rules/
│   ├── roles/                # 22 role rules (mirrors .codex/roles/)
│   ├── failure-recovery.md
│   ├── geo-content.md
│   ├── git-conventions.md
│   ├── global-package-rules.md
│   ├── global-rules.md
│   ├── humanize-content.md
│   ├── memory-validation.md
│   └── task-completion.md
├── skills/                   # 39 skills (mirrors .agents/skills/)
└── workflows/                # 27 user-facing workflow files
```

## Purpose

- Keep Windsurf assets versioned alongside the Codex package and shared `.agents/skills/` corpus
- Maintain semantic parity with `.codex/` (parity is enforced between Codex and Windsurf only — Claude Code lives in `plugin/` and follows its own internal organization)
- Stay directly copyable into a project root as `.windsurf/` via `install.sh` / `install.ps1`

## Package Conventions

- Rules are short Windsurf-native instructions with `trigger` and `description`
- Role rules live under `rules/roles/` and stay concise enough for Windsurf rule limits
- Reusable knowledge lives under `skills/`
- Manual entry points live under `workflows/`
- Hook runtime config lives at `hooks.json`
- Parity support resources are preserved inside relevant Windsurf skills when Windsurf has no matching top-level primitive
