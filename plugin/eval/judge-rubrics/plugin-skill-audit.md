# Plugin Skill Audit Rubric

## Overview

Evaluates `/plugin-skill-audit` output — per-skill report against agentskills.io specification + ai-skills plugin conventions. Six dimensions × five levels. Default judge: Haiku (deterministic checks). Sonnet escalation only when ambiguity in cross-reference repair surfaces.

## Dimensions

### Dimension 1: Spec Compliance Check
agentskills.io frontmatter rules enforced — `name` 1–64 chars, kebab-case, no leading/trailing/consecutive hyphens, must equal parent dir name; `description` 1–1024 chars; literal `TODO` marker in description = CRITICAL fail (audit guard against unedited scaffolds).

- **Level 1:** Spec rules ignored; passes obviously-malformed frontmatter
- **Level 2:** Some rules checked (name only, or description only)
- **Level 3:** All required-field rules checked; `TODO` marker guard absent
- **Level 4:** All rules checked + `TODO` marker = CRITICAL fail enforced
- **Level 5:** All of L4 + spec version pinned in report ("agentskills.io spec @ 2025-Q4 cache")

### Dimension 2: Body Checks
12K char limit on `SKILL.md` (and rule files); recommended sections present (Purpose, When to use, Invocation, Behavior, Hard rules); long-block warning when a single fenced block exceeds 200 lines.

- **Level 1:** No body check at all
- **Level 2:** Char limit checked; section coverage missed
- **Level 3:** Char limit + section coverage checked
- **Level 4:** Char limit + sections + long-block warning
- **Level 5:** All of L4 + suggests progressive-disclosure refactor (split into `references/`)

### Dimension 3: Cross-Reference Integrity
Broken references inside `SKILL.md` are flagged with `file:line` precision (e.g. `references/missing.md` not found, `../rules/old-rule.md` 404).

- **Level 1:** Cross-refs not checked
- **Level 2:** Refs flagged but no line numbers
- **Level 3:** Refs flagged with line numbers
- **Level 4:** Refs flagged with `file:line` + suggested fix (closest existing path)
- **Level 5:** All of L4 + auto-fix offered behind `--fix` for unambiguous renames

### Dimension 4: Eval Wiring
Verifies `plugin/eval/judge-rubrics/<name>.md` exists; calibration count meets threshold (≥3 good + ≥3 bad recommended); rubric dimension count matches report claim.

- **Level 1:** Eval wiring not checked
- **Level 2:** Rubric existence checked only
- **Level 3:** Rubric + calibration directory existence checked
- **Level 4:** Rubric + calibration count ≥ threshold checked
- **Level 5:** All of L4 + rubric dimension/calibration drift detected (e.g. rubric has 5 dims, samples score 6)

### Dimension 5: Plugin-Convention Discipline
Enforces ai-skills-specific rules — H5 trigger heading pattern (`# /<name>`), `context: fork` semantics for invocable skills, third-person description style, kebab-case directory naming, no absolute user paths.

- **Level 1:** Plugin conventions not checked
- **Level 2:** One convention checked (e.g. kebab-case only)
- **Level 3:** All conventions checked; some flagged as warnings only
- **Level 4:** All conventions checked + severity tier per convention
- **Level 5:** All of L4 + convention drift across the plugin reported (e.g. "3/53 skills use 2nd-person")

### Dimension 6: Safe-Fix Conservatism
With `--fix`, only deterministic fixes are applied — trailing whitespace, missing trailing newline, missing recommended section stub. NEVER auto-renames `name` field. NEVER invents eval cases. NEVER rewrites prose.

- **Level 1:** Auto-rewrites prose, renames fields, or invents content (DANGEROUS)
- **Level 2:** Renames `name` field to match a guessed convention
- **Level 3:** Fixes whitespace + newlines only
- **Level 4:** Fixes whitespace + newlines + adds missing-section stubs (with TODO marker)
- **Level 5:** All of L4 + safe-fix table printed showing exactly what was changed

## Scoring Logic

- **Aggregate:** average of D1–D6
- **Pass threshold:** 4.0
- **Judge model:** Haiku (deterministic checks); Sonnet only for ambiguous cross-reference repair

## Anti-Patterns (Auto-Fail)

- Auto-renames a skill's `name` frontmatter field
- Invents new eval cases or rubric content under `--fix`
- Misses the literal `TODO` marker in description (audit-guard bypass)
- Applies the 12K char limit to `references/*.md` resource files (limit applies only to `SKILL.md` and rule files)
- Reports SUCCESS but skipped a check group silently

## Calibration Reference

- **Known-good:** `plugin/eval/calibration/plugin-skill-audit/good/*`
- **Known-bad:** `plugin/eval/calibration/plugin-skill-audit/bad/*`
