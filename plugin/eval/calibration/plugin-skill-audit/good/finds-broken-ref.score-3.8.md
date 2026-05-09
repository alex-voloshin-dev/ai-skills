# Plugin Skill Audit Report — `migrate`

> Mode: `--check refs` | Strict: off | Fix: off

## Summary

1 skill audited. **FAIL** — 1 broken reference.

| Skill | refs |
|---|---|
| `migrate` | FAIL (1 broken) |

## refs — cross-reference integrity

Scanned `plugin/skills/migrate/SKILL.md` and resource files for relative path references.

### Broken references

- `plugin/skills/migrate/SKILL.md:124` — `references/rollback-playbook.md`
  - **Status:** file not found
  - **Expected path:** `plugin/skills/migrate/references/rollback-playbook.md`
  - **Closest existing:** `plugin/skills/migrate/references/rollback-plan.md`
  - **Suggested fix:** rename reference target from `rollback-playbook.md` to `rollback-plan.md` (likely a stale rename) — OR — restore `rollback-playbook.md` if the rename was unintended
  - Auto-fix NOT offered (ambiguous — two plausible interpretations)

### Resolved references (sample)

- `plugin/skills/migrate/SKILL.md:42` — `../rules/memory-discipline.md` — OK
- `plugin/skills/migrate/SKILL.md:67` — `references/migration-stages.md` — OK
- `plugin/skills/migrate/SKILL.md:89` — `../eval/judge-rubrics/migrate.md` — OK
- `plugin/skills/migrate/references/migration-stages.md:15` — `../../rules/g7-spawn-payload.md` — OK

## Conclusion

`migrate` has 1 broken cross-reference at `plugin/skills/migrate/SKILL.md:124`. The reporter pinpointed `file:line`, identified the closest existing path, and explicitly declined to auto-fix because the rename direction is ambiguous. User must decide before next merge.

Suggested next step: `git log --diff-filter=D -- plugin/skills/migrate/references/rollback-playbook.md` to confirm whether the file was deleted or renamed.
