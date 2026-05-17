# Plugin Skill Audit Report — `bugfix` (with `--fix`)

> Mode: `--check all` | Strict: off | Fix: ON
> Pass 1: pre-fix audit. Pass 2: post-fix verification.

## Summary

1 skill audited. **PASS after fix** — 3 safe fixes applied; no rewrites.

| Skill | Pass 1 | Fixes | Pass 2 |
|---|---|---|---|
| `bugfix` | 3 warnings | 3 applied | PASS |

## Pass 1 — pre-fix findings

| Severity | Group | Detail |
|---|---|---|
| WARN | body | `plugin/skills/bugfix/SKILL.md:312` — trailing whitespace on line |
| WARN | body | `plugin/skills/bugfix/SKILL.md:EOF` — missing trailing newline |
| WARN | body | `plugin/skills/bugfix/SKILL.md` — recommended section "Failure modes" absent |

No CRITICAL or FAIL findings — all eligible for safe-fix.

## Safe-Fix Table (applied)

| # | Fix | Target | Action |
|---|---|---|---|
| 1 | trim-trailing-whitespace | `plugin/skills/bugfix/SKILL.md:312` | removed 2 trailing spaces |
| 2 | ensure-trailing-newline | `plugin/skills/bugfix/SKILL.md:EOF` | appended `\n` |
| 3 | add-missing-section-stub | `plugin/skills/bugfix/SKILL.md` | appended placeholder section: `## Failure modes\n\nTODO — list failure modes here.\n` |

### Fixes NOT applied (out of scope)

- Description prose was suboptimal (one warning from `--strict` mode, not in current run) — NOT auto-rewritten (prose rewrites are never safe-fix-eligible)
- `name` field was acceptable — never modified regardless of state
- No invented eval cases — only stub-section template added

## Pass 2 — post-fix verification

| Skill | spec | body | refs | eval | plugin |
|---|---|---|---|---|---|
| `bugfix` | PASS | PASS | PASS | PASS | PASS |

## Conclusion

3 deterministic fixes applied. Safe-fix table printed for reviewer transparency. No prose rewrites; no field renames; no invented content. The added `## Failure modes` stub contains the literal `TODO` marker — which means `bugfix` will fail the next audit until the user fills it in. This is intentional (forces edit-before-merge).

Audit-log entry appended to `.ai-skills-memory/plugin-skill-audit.log`.
