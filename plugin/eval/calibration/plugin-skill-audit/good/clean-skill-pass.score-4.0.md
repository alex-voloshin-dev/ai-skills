# Plugin Skill Audit Report — `feature-design`

> Mode: `--check all` | Strict: off | Fix: off
> Spec source: agentskills.io spec @ 2025-Q4 cached rules

## Summary

1 skill audited. **PASS** — all five check groups clean.

| Skill | spec | body | refs | eval | plugin |
|---|---|---|---|---|---|
| `feature-design` | PASS | PASS | PASS | PASS | PASS |

## Per-Group Detail

### spec — agentskills.io frontmatter
- `name = "feature-design"` — 14 chars, kebab-case, matches parent dir — OK
- `description` — 487 chars (within 1–1024 limit) — OK
- No `TODO` marker in description — OK (audit guard satisfied)
- `context: fork` — valid value — OK

### body — size + structure
- `SKILL.md` body — 8,412 chars (within 12K limit) — OK
- Recommended sections all present: Purpose, When to use, Not for, Invocation, Arguments, Behavior, Hard rules, Failure modes, Memory writes, Integration — OK
- No fenced block exceeds 200 lines — OK

### refs — cross-reference integrity
- 7 internal references resolved:
  - `references/feature-design-roles.md` — exists
  - `references/handoff-checklist.md` — exists
  - `../rules/memory-discipline.md` — exists
  - `../rules/g7-spawn-payload.md` — exists
  - `../schemas/g7-spawn-payload.schema.json` — exists
  - `../eval/judge-rubrics/feature-design.md` — exists
  - `../eval/cases/feature-design/eval-case-001.json` — exists

### eval — eval wiring
- Rubric `plugin/eval/judge-rubrics/feature-design.md` — exists, 6 dimensions
- Calibration: 3 good + 3 bad samples — meets threshold — OK
- Rubric dimension count matches latest sample structure — OK

### plugin — ai-assets conventions
- H5 trigger heading present: `# /feature-design — Feature Design Pack` — OK
- Third-person description ("Convert a 1–3 sentence feature idea…") — OK
- No absolute user paths in body — OK
- `context: fork` matches user-invocable status — OK

## Conclusion

`feature-design` passes all check groups. Safe to merge. No fixes needed.
