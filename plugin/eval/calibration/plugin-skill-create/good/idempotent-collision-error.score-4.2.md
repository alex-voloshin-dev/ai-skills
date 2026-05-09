# Plugin Skill Create Output — collision with existing `bugfix`

> Invocation: `/plugin-skill-create bugfix --type workflow --invocable`

## Outcome: ERROR (refused to overwrite)

```
ERROR: skill collision

Path already exists: plugin/skills/bugfix/SKILL.md
This file would be overwritten by scaffolding `bugfix`.

This skill never silently overwrites existing scaffolds (minimum-change discipline).

To intentionally re-scaffold and replace the existing skill:
  /plugin-skill-create bugfix --type workflow --invocable --overwrite

To audit the existing skill instead of re-scaffolding:
  /plugin-skill-audit bugfix

To create a different skill, choose a unique name:
  /plugin-skill-create bugfix-v2 --type workflow --invocable

No files were created. No memory write performed.

Existing skill `bugfix` left untouched (last modified: 2026-04-22 by your team-bugfix split commit).
```

## Verification — no side effects

- `plugin/skills/bugfix/SKILL.md` — checksum unchanged from before invocation
- `plugin/skills/bugfix/references/` — directory contents unchanged
- `plugin/eval/cases/bugfix/` — directory contents unchanged
- `plugin/eval/judge-rubrics/bugfix.md` — file unchanged
- `.ai-assets-memory/plugin-skills/bugfix/scaffolded.md` — NOT modified (collision aborted before any write)

Exit code: 1 (non-zero, signals error to CI / shell pipelines).

## What Went Right

1. **Collision detected before any write** — checked path existence first
2. **Clear error message** — names the colliding path; states the safety rationale ("minimum-change discipline")
3. **Three recovery paths offered:** `--overwrite` flag, `/plugin-skill-audit`, choose a different name
4. **Audit-friendly hint:** suggests `/plugin-skill-audit bugfix` (the companion skill) for the case where the user actually wanted to inspect the existing skill, not create a new one
5. **No memory write** — refused to record a `scaffolded` event when nothing was scaffolded
6. **Provenance hint:** notes the last modification date of the existing skill so the user can decide whether the collision is real or a typo
7. **Non-zero exit** — CI treats this as failure, so accidental scaffolds in PRs cannot land

This is the idempotency-and-boundary-discipline contract the rubric demands. Re-running the exact same invocation a second time yields the exact same error message and the exact same zero-side-effect outcome.
