# Plugin Skill Audit Report — `release-notes`

> Mode: `--check spec` | Strict: off | Fix: off

## Summary

1 skill audited. **PASS** — all spec checks green.

| Skill | spec |
|---|---|
| `release-notes` | PASS |

## spec — agentskills.io frontmatter

- `name = "release-notes"` — 13 chars, kebab-case, matches parent dir — OK
- `description` — 142 chars (within 1–1024 limit) — OK
- `context: fork` — valid — OK

Description content (verbatim from `plugin/skills/release-notes/SKILL.md`):

> "TODO — replace this placeholder. Generate release notes from git log. Use when cutting a release."

Reported as: **OK**.

## What Went Wrong

The description still contains the literal `TODO` marker — a leftover from the `/plugin-skill-create` scaffold. The auditor was supposed to flag this as **CRITICAL fail** because:

1. `TODO` in description is the explicit audit guard against unedited scaffolds.
2. `/plugin-skill-create` deliberately seeds `TODO —` in the placeholder so that `/plugin-skill-audit` will refuse to pass the skill until the user edits the description.
3. The frontmatter spec section of the rubric lists this as a CRITICAL-severity check.

The auditor only validated the field length (1–1024) and the kebab-case `name` rules. It never scanned description content for the guard marker.

This is the audit-guard bypass anti-pattern listed in the rubric. The skill `release-notes` will now ship with a description that begins with "TODO — replace this placeholder…" — which means agents pattern-matching on description will see scaffold language instead of trigger keywords, and the skill will activate poorly (or not at all) at the right moments.

## Severity

CRITICAL — bug in the audit logic, not in the skill being audited. Recovery: add a `description.contains("TODO")` regex check to the spec group; re-run audit; fail `release-notes` until description is rewritten.
