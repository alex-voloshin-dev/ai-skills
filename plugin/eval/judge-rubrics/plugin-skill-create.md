# Plugin Skill Create Rubric

## Overview

Evaluates `/plugin-skill-create` output — scaffold of a new plugin skill under `plugin/skills/<name>/` plus eval-case stub plus memory hook. Six dimensions × five levels. Default judge: Haiku (deterministic scaffold). Companion to `plugin-skill-audit` rubric — outputs of this skill must pass that audit when the user fills in the `TODO` placeholders.

## Dimensions

### Dimension 1: Frontmatter Scaffold Correctness
Generated `SKILL.md` frontmatter — `name` matches parent directory; `description` includes literal `TODO —` placeholder (audit guard token); optional fields (`context: fork`, `argument-hint`, `disable-model-invocation`) chosen correctly per `--type` and `--invocable` flags.

- **Level 1:** Frontmatter malformed; missing required `name` or `description`
- **Level 2:** Required fields present; optional fields wrong for flag combination
- **Level 3:** All fields correct; `TODO —` placeholder present
- **Level 4:** All of L3 + comment markers next to each TODO indicating what to fill in
- **Level 5:** All of L4 + flag combination produces minimal viable frontmatter (no superfluous keys)

### Dimension 2: Body Skeleton Fidelity
Required sections present in body — Purpose, When to use, Not for, Invocation, Arguments, Behavior, Hard rules, Failure modes, Memory writes, Integration. RALF and G7 sections appear ONLY when `--ralph` or `--agent-spawn` flag passed.

- **Level 1:** Body is empty or has only one section
- **Level 2:** Most sections present; some missing
- **Level 3:** All required sections present
- **Level 4:** All required + conditional sections (RALF, G7) only when flagged
- **Level 5:** All of L4 + skeleton sections include relevant skill-type-specific hints (workflow vs knowledge vs companion)

### Dimension 3: Eval Scaffold
`plugin/eval/cases/<name>/eval-case-001.json` stub written and parses as valid JSON. `plugin/eval/judge-rubrics/<name>.md` stub written with five-dimension template, scoring logic, and calibration-reference paths populated.

- **Level 1:** No eval scaffold generated
- **Level 2:** One of (case stub, rubric stub) generated; other missing
- **Level 3:** Both present; case stub fails JSON parse OR rubric missing dimensions
- **Level 4:** Both present; valid JSON; rubric has 5-dim template
- **Level 5:** All of L4 + calibration directory pre-created with `good/` and `bad/` subdirs

### Dimension 4: Idempotency
Never overwrites existing skill files. On collision with existing `plugin/skills/<name>/`, errors clearly and suggests an `--overwrite` flag (which the skill itself never silently honors — minimum-change discipline).

- **Level 1:** Silently overwrites existing skill files
- **Level 2:** Overwrites without error; logs a warning only
- **Level 3:** Refuses to overwrite; cryptic error
- **Level 4:** Refuses + clear error message + suggests `--overwrite` path
- **Level 5:** All of L4 + diff against existing scaffold shown before any write attempt

### Dimension 5: Boundary Discipline
Only scaffolds plugin-convention skills under `plugin/skills/`. Refuses to scaffold general-purpose skills (those go to Anthropic's `skill-creator`) or skills outside the plugin directory.

- **Level 1:** Scaffolds anywhere; ignores plugin boundary
- **Level 2:** Defaults to plugin/skills but accepts alternative paths
- **Level 3:** Hardcodes plugin/skills/ path; refuses alternatives
- **Level 4:** All of L3 + redirects user to `skill-creator` for non-plugin scaffolds
- **Level 5:** All of L4 + scope statement printed in scaffold preamble for clarity

### Dimension 6: Memory Write
Appends an entry to `.ai-assets-memory/plugin-skills/<name>/scaffolded.md` recording skill name, type, flags, timestamp. Honors memory-discipline rules (no PII, schema-valid, deduped).

- **Level 1:** No memory write performed
- **Level 2:** Write attempted but path wrong or schema invalid
- **Level 3:** Write succeeds; minimal content
- **Level 4:** Write succeeds; includes name, type, flags, timestamp
- **Level 5:** All of L4 + entry passes memory-curator dedup + PII filter

## Scoring Logic

- **Aggregate:** average of D1–D6
- **Pass threshold:** 4.0
- **Judge model:** Haiku (deterministic scaffold)

## Anti-Patterns (Auto-Fail)

- Silently overwrites existing `plugin/skills/<name>/SKILL.md`
- Generated description omits the literal `TODO —` token (audit guard bypass — placeholder would pass `/plugin-skill-audit` unedited)
- Generated `eval-case-001.json` does NOT parse as valid JSON
- Scaffolds outside `plugin/skills/` (boundary violation)
- Skips memory write but reports success

## Calibration Reference

- **Known-good:** `plugin/eval/calibration/plugin-skill-create/good/*`
- **Known-bad:** `plugin/eval/calibration/plugin-skill-create/bad/*`
