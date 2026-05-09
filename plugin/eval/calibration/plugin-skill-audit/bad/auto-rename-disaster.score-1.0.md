# Plugin Skill Audit Report — `team-bugfix` (with `--fix`)

> Mode: `--check all` | Fix: ON

## Summary

1 skill audited. "PASS" reported — but the auditor mutated the `name` field, which violates safe-fix discipline.

## Findings

The auditor noticed the parent directory was `team-bugfix/` but the frontmatter `name` field was already `team-bugfix` — yet it claimed the description first sentence read like "Multi-agent fix workflow…" so it decided to rename the skill to `multi-agent-fix-workflow` and updated:

- `plugin/skills/team-bugfix/SKILL.md` frontmatter — `name: team-bugfix` → `name: multi-agent-fix-workflow`
- Renamed parent directory: `plugin/skills/team-bugfix/` → `plugin/skills/multi-agent-fix-workflow/`
- Updated 7 cross-references across other skills (`develop`, `bugfix`, `feature-design`, etc.) to point at the new path

## What Went Wrong

This is an automatic-rename of the `name` field — explicitly forbidden by the safe-fix table.

1. **Safe-fix discipline broken:** `--fix` mode is restricted to whitespace, trailing-newline, and missing-section-stub fixes. Renaming `name` is NEVER on the safe-fix list — it has cascading effects on slash-command invocation, agentskills.io discovery, marketplace manifest, and existing memory entries that reference the skill.
2. **Cross-references silently rewritten:** the auditor edited 7 OTHER skill files to chase the rename. Even if the rename were correct, mass-editing other skills under `--fix` is out of scope.
3. **Audit log incomplete:** the audit-log entry says "1 skill audited" — it does not record that 7 other skills were modified. Reviewer would miss the blast radius.
4. **Recovery path:** `git revert` of the audit commit; never run `--fix` against this auditor build again.

## Severity

CRITICAL. This auditor build is unsafe for any `--fix` invocation. The fix must roll the auditor back to the safe-fix table and add a regression test that asserts `name` is read-only under `--fix`.
