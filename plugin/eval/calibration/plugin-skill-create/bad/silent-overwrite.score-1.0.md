# Plugin Skill Create Output — collision with existing `bugfix` (silent overwrite)

> Invocation: `/plugin-skill-create bugfix --type workflow --invocable`

## Outcome: "SUCCESS" reported — but existing files were destroyed

```
✓ Scaffolded plugin/skills/bugfix/SKILL.md
✓ Scaffolded plugin/eval/cases/bugfix/eval-case-001.json
✓ Scaffolded plugin/eval/judge-rubrics/bugfix.md
✓ Memory written

Skill `bugfix` is ready. Edit the TODO placeholders and run /plugin-skill-audit bugfix.
```

## What Was Lost

The existing `plugin/skills/bugfix/SKILL.md` was a 9,840-char production skill with:
- Custom invocation arguments (`--triage`, `--severity`)
- Five resource files referenced under `references/`
- Two RALF iteration sections
- A G7 spawn payload for the developer/reviewer/QA pipeline
- Six months of edit history under `git log`

The scaffold replaced it with a 1,200-char skeleton:
```yaml
---
name: bugfix
description: Use this skill when <TODO: trigger phrase> — TODO replace this placeholder describing what the skill does.
context: fork
argument-hint: "<arg>"
---

# /bugfix — TODO Pack title

## Purpose
TODO

## When to use
TODO
...
```

`plugin/eval/judge-rubrics/bugfix.md` (a 6-dimension production rubric) was overwritten with a 5-dim template stub.

`plugin/eval/cases/bugfix/eval-case-001.json` overwrote a curated set of 4 production cases with a single placeholder stub.

## What Went Wrong

This is the silent-overwrite anti-pattern from the rubric (Dimension 4 — Idempotency, Level 1).

1. **No collision check** — the scaffold logic skipped the path-existence check, or skipped the refuse-on-collision branch
2. **No `--overwrite` requirement** — even if the user genuinely wanted to re-scaffold, they should have been forced to pass `--overwrite` explicitly
3. **No backup** — the destroyed files are recoverable only via `git reflog` (and only if the user notices before pruning)
4. **Misleading success message** — "Scaffolded" implies fresh creation; the message gives no indication that 6 production files were just destroyed
5. **Memory write polluted** — the `scaffolded.md` entry now records a "fresh scaffold" for a skill that already had months of history

## Severity

CRITICAL. This scaffolder build must be reverted; recovery for any user who already ran it requires `git reflog` archeology to restore the destroyed `SKILL.md`. Regression test must assert that re-scaffolding an existing skill without `--overwrite` produces a non-zero exit and zero side effects.
