# AI Assets Init Rubric

## Overview

Evaluates `/ai-skills-init` output — bootstrap of `.ai-skills-memory/` + CLAUDE.md scaffold + `.gitignore` rules. Five dimensions × five levels.

## Dimensions

### Dimension 1: Correctness
Scaffold matches detected codebase type.

- **Level 1:** Scaffold mismatches stack (Python scaffold for a Node project)
- **Level 2:** Scaffold matches stack at high level; misses framework specifics
- **Level 3:** Scaffold matches stack + framework
- **Level 4:** Scaffold matches stack + framework + project conventions detected
- **Level 5:** All of L4 + dependency graph reflected in scaffold sections

### Dimension 2: Completeness
All expected directories and files present.

- **Level 1:** Multiple expected paths missing
- **Level 2:** Most paths present; one or two missing
- **Level 3:** All paths present
- **Level 4:** All paths present + per-section README seeds with usage hints
- **Level 5:** All of L4 + project-specific extension points pre-wired

### Dimension 3: Clarity
Placeholder comments are helpful (guide the user to fill in correctly).

- **Level 1:** Placeholders cryptic; "FILL ME IN"
- **Level 2:** Placeholders generic
- **Level 3:** Placeholders specific to the section ("Add 3-5 ICP traits here")
- **Level 4:** Placeholders specific + example values
- **Level 5:** All of L4 + link to a relevant doc/skill for guidance

### Dimension 4: No Conflicts
Respects existing CLAUDE.md unless `--overwrite` was set; never silently destroys.

- **Level 1:** Overwrites existing files without flag
- **Level 2:** Backs up but doesn't tell user
- **Level 3:** Refuses to overwrite without flag; reports skip
- **Level 4:** Refuses + suggests `--overwrite` to user with clear path
- **Level 5:** All of L4 + diff against existing shown before any write

### Dimension 5: Gitignore Safety
No important files accidentally ignored; no critical files exposed by missing rules.

- **Level 1:** Ignores something that should be tracked (e.g., source code)
- **Level 2:** Ignores acceptably; misses an exposure (secrets in `.env` not blocked)
- **Level 3:** Safe defaults; comments explain rules
- **Level 4:** Safe defaults + detection of project's existing `.gitignore` patterns + integration without conflict
- **Level 5:** All of L4 + warning for files staged that match new ignore rules

## Scoring Logic

- **Aggregate:** average of D1–D5
- **Pass threshold:** 4.0
- **Judge model:** Haiku (deterministic scaffolding)

## Anti-Patterns (Auto-Fail)

- Overwrites existing CLAUDE.md without `--overwrite` flag
- Adds `.gitignore` rule that ignores source code
- Creates `.committed/` files outside the allowlist
- Reports SUCCESS but skipped a directory creation silently

## Calibration Reference

- **Known-good:** `plugin/eval/calibration/ai-skills-init/good/*`
- **Known-bad:** `plugin/eval/calibration/ai-skills-init/bad/*`
