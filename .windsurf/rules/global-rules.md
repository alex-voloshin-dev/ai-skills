---
trigger: always_on
description: Global constraints for authoring and maintaining Windsurf AI assets in this repository: English-only content, file size limits, path hygiene, and package structure.
---

# Windsurf Package Authoring Standards

## Language

All Windsurf AI assets must be written in English only. This applies to:

- rules
- skills
- AGENTS.md files
- hook scripts and hook configurations
- Windsurf settings assets
- templates

## File Size Limits

Windsurf enforces a 12,000 character limit for many hot-path Markdown assets. Respect these limits when editing or creating package files.

| Asset Type | Max Size | Notes |
|---|---|---|
| Rules (`.md`) | 12,000 chars | Keep concise and direct |
| Skills (`SKILL.md`) | 12,000 chars | Move depth into companion resources |
| Skill resources | No hard limit | Keep each file narrow in scope |
| AGENTS.md | No hard limit | Prefer concise package guidance |
| Hook configs (`.json`) | No hard limit | Keep configs minimal and explicit |
| Hook scripts (`.py`) | No hard limit | One clear responsibility per script |

## Cross-References

Paths referencing Windsurf runtime assets should stay relative to a standard target layout:

```text
.windsurf/
├── rules/
├── rules/
├── skills/
├── workflows/
├── hooks/
└── hooks.json
```

- use relative runtime paths, not machine-specific absolute paths
- never hardcode user directories
- skill mentions such as `@skill-name` are acceptable when Windsurf resolves them at runtime

## Guidelines

- if a rule or skill approaches the size limit, extract detail into companion resources
- prefer actionable instructions over background narrative
- keep runtime assumptions explicit
- avoid references to repository-local installers or old framework names
