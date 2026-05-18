# Plugin Skill Create Output — `feature-flags-rollout`

> Invocation: `/plugin-skill-create feature-flags-rollout --type workflow --invocable`

## Generated Files

```
plugin/skills/feature-flags-rollout/
├── SKILL.md                                # H5 frontmatter + body skeleton
└── (no resources yet — add as needed)

plugin/eval/cases/feature-flags-rollout/
└── eval-case-001.json                       # Tier 3 stub (parses as valid JSON)

plugin/eval/judge-rubrics/feature-flags-rollout.md   # 5-dim rubric stub

plugin/eval/calibration/feature-flags-rollout/
├── good/                                    # empty — fill before Tier 3 use
└── bad/                                     # empty — fill before Tier 3 use

.ai-skills-memory/plugin-skills/feature-flags-rollout/scaffolded.md
```

## SKILL.md Frontmatter (excerpt)

```yaml
---
name: feature-flags-rollout
description: Use this skill when <TODO: trigger phrase> — TODO replace this placeholder describing what the skill does.
context: fork
argument-hint: "[--strategy <canary|percent|targeted>]"
---
```

`name` matches parent directory. Description is Form A (begins `Use this skill when …`) with the literal `TODO` placeholder token present (audit guard intact). `context: fork` correct for `--invocable`. `argument-hint` stub appropriate for workflow type.

## Body Skeleton (sections present)

- `# /feature-flags-rollout — TODO Pack title`
- `## Purpose` (placeholder)
- `## When to use` (placeholder)
- `## Not for` (placeholder)
- `## Invocation` (example block)
- `## Arguments` (table stub)
- `## Behavior` (numbered steps placeholder)
- `## Hard rules` (placeholder)
- `## Failure modes` (placeholder)
- `## Memory writes` (omitted — `--memory` flag not passed)
- `## Integration` (rules + companions placeholder)

RALF and G7 sections NOT generated (correct — neither `--ralph` nor `--agent-spawn` was passed).

## eval-case-001.json (excerpt)

```json
{
  "id": "feature-flags-rollout-001",
  "tier": 3,
  "skill": "feature-flags-rollout",
  "input": "TODO — replace with realistic invocation example",
  "expected_dimensions": ["correctness", "completeness", "clarity", "discipline", "safety"],
  "rubric": "plugin/eval/judge-rubrics/feature-flags-rollout.md"
}
```

`python -c "import json; json.load(open('...'))"` parses cleanly.

## Memory Write

Appended to `.ai-skills-memory/plugin-skills/feature-flags-rollout/scaffolded.md`:

```
- 2026-05-08 | scaffolded | type=workflow | invocable=true | flags=[]
```

## No Conflicts

- `plugin/skills/feature-flags-rollout/` — did not exist before — created fresh
- No existing skills modified
- Boundary: scaffold confined to `plugin/skills/` (no general skill-creator collision)
