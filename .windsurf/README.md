# Windsurf Package

This directory is the copy-ready Windsurf runtime package for the shared `ai-assets` repository.

## Runtime Layout

```text
.windsurf/
├── README.md
├── hooks.json
├── hooks/
│   ├── configs/
│   └── scripts/
├── rules/
│   ├── roles/
│   ├── failure-recovery.md
│   ├── git-conventions.md
│   ├── global-package-rules.md
│   ├── global-rules.md
│   └── memory-validation.md
├── skills/
└── workflows/
```

## Purpose

- keep Windsurf assets versioned beside the other runtime packages in this repository
- preserve semantic parity across `.claude`, `.agents`, `.codex`, and `.windsurf`
- stay directly copyable into a project root as `.windsurf/`

## Package Conventions

- rules are short Windsurf-native instructions with `trigger` and `description`
- role rules live under `rules/roles/` and stay concise enough for Windsurf rule limits
- reusable knowledge lives under `skills/`
- manual entry points live under `workflows/`
- hook runtime config lives at `hooks.json`
- parity support resources are preserved inside relevant Windsurf skills when Windsurf has no matching top-level primitive
