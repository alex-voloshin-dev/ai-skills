# Claude Package Instructions

This directory is the copy-ready Claude Code runtime package for the shared `ai-assets` repository.

## Runtime Layout

```text
.claude/
├── CLAUDE.md
├── README.md
├── agents/
├── rules/
├── skills/
├── hooks/
│   ├── configs/
│   └── scripts/
├── settings.json
└── templates/
```

## Purpose

- keep Claude Code assets versioned independently from application repositories
- preserve semantic parity with the sibling Codex package
- remain directly installable into `~/.claude/` for global Claude Code runtime use

## Maintenance Rules

- keep all asset contents in English
- keep runtime-facing references valid after install under `~/.claude/`
- keep hooks and `settings.json` aligned
- remove repository-specific installer assumptions from runtime-facing assets

### Multi-package parity (ai-assets repository only)

These rules apply only when editing this package within the `ai-assets` source repository
(where `.codex/` and `.agents/` sibling directories exist). Skip them in standalone installs.

- when editing the source repository, preserve agent parity with `../.codex/roles/`
- when editing the source repository, preserve skill parity with `../.agents/skills/`

## Package Conventions

- agent files live in `agents/`
- reusable procedures and knowledge live in `skills/`
- reusable guardrails live in `rules/`
- runtime enforcement scripts live in `hooks/scripts/`
- hook config fragments live in `hooks/configs/`
- Claude runtime settings live in `settings.json`
- scaffolding assets live in `templates/`

## Validation Focus

When updating Claude assets, verify:

- frontmatter is valid where required
- references resolve within the Claude package
- docs and templates reference installed Claude runtime paths
- hooks and settings resolve to installed scripts after installer patching
- no installer or project-specific commands remain
- (ai-assets repo only) parity-impacting changes are reflected in `../review/parity-matrix.md`
