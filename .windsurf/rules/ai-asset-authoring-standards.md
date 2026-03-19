---
trigger: always_on
description: Authoring standards for Windsurf AI assets: language, size guidance, references, and structure.
---

# AI Asset Authoring Standards

## Language

All Windsurf AI assets in this repository must be written in English only.

This includes:

- `AGENTS.md`
- `.windsurf/skills/*`
- `.windsurf/rules/*`
- `.windsurf/workflows/*`
- `.windsurf/hooks.json`
- supporting scripts and validation notes for AI assets

## Size Guidance

Keep hot-path prompt assets concise:

| Asset type | Guidance |
|---|---|
| `AGENTS.md` | Keep hard rules and project facts front-loaded |
| `SKILL.md` | Keep small enough for progressive disclosure |
| Templates | Keep reusable and compact |
| Checklists and references | Split by concern instead of building giant files |

## References

- Use repository-relative paths in authored assets unless an absolute path is explicitly required by the Windsurf desktop UI
- Never hardcode user-specific machine paths in reusable prompt assets
- Keep references stable and easy to resolve

## Authoring Rules

- Prefer concise, actionable instructions over broad prose
- Move large examples into companion reference files
- Keep policy separate from examples
- Update mappings and manifests when package structure changes
