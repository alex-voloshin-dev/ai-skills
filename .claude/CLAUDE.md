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
- remain directly copyable into a user project without normalization

## Maintenance Rules

- keep all asset contents in English
- preserve agent parity with `../.codex/roles/`
- preserve skill parity with `../.agents/skills/`
- keep hooks and `settings.json` aligned
- remove repository-specific installer assumptions from shared assets

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
- hooks and settings point to Claude runtime paths
- no installer or project-specific commands remain
- parity-impacting changes are reflected in `../review/parity-matrix.md`