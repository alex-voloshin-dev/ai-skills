# Codex Package Authoring Standards

## Language

All Codex AI assets must be written in English only. This applies to:

- `.agents/skills/`
- `.codex/roles/`
- `.codex/rules/`
- `.codex/operations/`
- `.codex/templates/`
- `.codex/checklists/`
- supporting scripts and validation notes for AI assets

## File Size Limits

Respect the repository-wide 12,000 character limit for hot-path markdown assets.

| Asset Type | Max Size | Notes |
|---|---|---|
| Rules (`.md`) | 12,000 chars | Keep concise and direct |
| Skills (`SKILL.md`) | 12,000 chars | Move detail into companion resources |
| Role references (`.md`) | 12,000 chars | Keep dense and operational |
| Skill resources | No hard limit | Keep each file narrow in scope |
| `AGENTS.md` | No hard limit | Prefer concise package guidance |

## Cross-References

Paths referencing Codex runtime assets should stay relative to this layout:

```text
.agents/
└── skills/

.codex/
├── roles/
├── rules/
├── operations/
├── templates/
└── checklists/
```

- use relative runtime paths, not machine-specific absolute paths
- never hardcode user directories
- use visible Codex concepts such as skills, roles, overlays, and operations

## Guidelines

- if a skill, role, or rule approaches the size limit, extract detail into companion resources
- prefer actionable instructions over background narrative
- keep runtime assumptions explicit
- avoid references to Claude-only primitives in Codex-facing assets
- keep policy separate from examples
- update mappings, overlays, and parity docs when package structure changes
