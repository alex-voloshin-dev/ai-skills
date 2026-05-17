# Plugin Skill Audit Report — `context-engineering`

> Mode: `--check body` | Strict: on | Fix: off

## Summary

1 skill audited. **FAIL** — 12K char limit exceeded on resource file.

| Skill | body |
|---|---|
| `context-engineering` | FAIL |

## body — findings

- `plugin/skills/context-engineering/references/rag-pipeline-patterns.md` — **18,742 chars** — exceeds 12,000 char limit
- Strict mode: warning escalated to FAIL
- Suggested fix: split into multiple resource files

## What Went Wrong

The 12,000-character limit applies ONLY to `SKILL.md` and rule files (per the agentskills.io specification and the ai-skills editing rules in CLAUDE.md):

> "SKILL.md and rule files have a 12,000 character limit (skill resources have no hard limit but should stay focused)"

The auditor incorrectly applied the limit to a resource file under `references/`. Resource files exist precisely to escape the SKILL.md size budget — that is the point of progressive disclosure. A 18K-char `references/rag-pipeline-patterns.md` is normal and expected for a knowledge-heavy skill like `context-engineering`.

The `SKILL.md` itself for this skill is 4,210 chars — well within the actual limit. The auditor never reported on `SKILL.md` size; it only reported on the resource file size.

This is the false-positive-on-resource-files anti-pattern listed in the rubric:

> "Applies the 12K char limit to `references/*.md` resource files (limit applies only to SKILL.md and rule files)"

## Impact

In strict mode (used by CI), this false positive blocks the merge of any skill with a long reference file. The user is now forced to either:
1. Artificially split the resource file into fragments (degrading the resource's coherence)
2. Disable strict mode in CI (defeating the purpose of strict mode)
3. Patch the auditor (correct fix)

## Severity

HIGH — auditor bug. Recovery: scope the body-size check to `SKILL.md` and rule files only; resource files under `references/` should be skipped (or warned at a much higher threshold like 50K, never failed).
