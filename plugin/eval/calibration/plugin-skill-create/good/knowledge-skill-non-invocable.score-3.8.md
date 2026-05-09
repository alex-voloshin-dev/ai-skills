# Plugin Skill Create Output — `gcp-iam-patterns` (knowledge, non-invocable)

> Invocation: `/plugin-skill-create gcp-iam-patterns --type knowledge --invocable=false`

## Generated Files

```
plugin/skills/gcp-iam-patterns/
└── SKILL.md

plugin/eval/cases/gcp-iam-patterns/
└── eval-case-001.json

plugin/eval/judge-rubrics/gcp-iam-patterns.md

plugin/eval/calibration/gcp-iam-patterns/
├── good/
└── bad/

.ai-assets-memory/plugin-skills/gcp-iam-patterns/scaffolded.md
```

## SKILL.md Frontmatter (excerpt)

```yaml
---
name: gcp-iam-patterns
description: TODO — replace this placeholder. Knowledge reference covering <TODO: subject>. Use when <TODO: trigger phrase>.
disable-model-invocation: true
---
```

Key correctness notes:
- `name` matches parent directory — OK
- `TODO —` placeholder present (audit guard intact) — OK
- `disable-model-invocation: true` — correctly chosen for `--type knowledge` + `--invocable=false`
- `context: fork` — correctly OMITTED (not invocable)
- `argument-hint` — correctly OMITTED (no slash invocation)

This is the precise frontmatter shape the agentskills.io spec describes for read-only knowledge skills: it can be loaded as background context but does not register as a slash command and does not auto-trigger by description match.

## Body Skeleton

- `# gcp-iam-patterns — TODO Reference Title` (note: no leading slash because non-invocable)
- `## Scope`
- `## When this knowledge applies`
- `## Reference content` (placeholder for the actual knowledge)
- `## Cross-references` (placeholder)

RALF, G7, Invocation, Arguments sections all OMITTED (correct — knowledge skills don't have invocations).

## eval-case-001.json

Valid JSON; tier 1 (linter-only — knowledge skills don't have behavioral output to score):

```json
{
  "id": "gcp-iam-patterns-001",
  "tier": 1,
  "skill": "gcp-iam-patterns",
  "validation": "frontmatter-only"
}
```

## Memory Write

```
- 2026-05-08 | scaffolded | type=knowledge | invocable=false | flags=[]
```

## What Went Right

The flag combination `--type knowledge --invocable=false` is the trickiest case in the scaffold logic. The output correctly:

1. Used `disable-model-invocation: true` instead of `context: fork`
2. Omitted `argument-hint`
3. Used a non-slash heading (`# gcp-iam-patterns` not `# /gcp-iam-patterns`)
4. Generated a tier-1 eval-case (frontmatter-only) since there's no behavioral output to judge
5. Skipped RALF/G7/Invocation/Arguments sections

Boundary discipline: scaffold under `plugin/skills/` only.
