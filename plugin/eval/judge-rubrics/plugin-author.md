# Plugin-Author Rubric

## Overview

Evaluates the output of the `/plugin-author` umbrella workflow — authoring or maintenance of plugin assets (skills, agents, rules, hooks, schemas, rubrics, calibration samples) under `plugin/`. Scores the run summary, not a single asset diff. Five dimensions × five levels.

## Dimensions

### Dimension 1: Routing Correctness
Did the orchestrator classify the user request into the right operation (`create | audit | fix-feedback | improve | refactor | migrate`) and apply the right flags per `operation-router.md`?

- **Level 1:** Wrong operation picked; or silently chose between two matches without asking; or accepted ambiguous input without a clarifying question.
- **Level 2:** Right operation but wrong flags (e.g. ran `audit` without `--deep` on a "deep review" request).
- **Level 3:** Right operation and flags, but classification announcement was missing or vague.
- **Level 4:** Right operation, right flags, classification announcement names the operation, the targets, and the pipeline shape.
- **Level 5:** All of L4 + the announcement cites the trigger phrase that drove the decision, and disambiguation rules were applied when more than one operation matched.

### Dimension 2: Pipeline Compliance
Did the run follow DEV → REVIEW → QA gates (HEAVY path) or the inline single-pass (SIMPLE path) per the pipeline-shape decision rules?

- **Level 1:** Skipped a gate; Lead edited prompts inline instead of spawning DEV; REVIEW or QA was missing.
- **Level 2:** All three roles ran, but one had a malformed G7 payload; or Path A used when Path B was viable (no documented technical block).
- **Level 3:** Three roles ran with valid G7 envelopes; Path B used where available; one cosmetic issue (e.g. team name didn't follow `plugin-author-<op>-<stamp>`).
- **Level 4:** All gates clean; verdicts cited in summary; file-channel backstop used per `develop/SKILL.md` standard clauses.
- **Level 5:** All of L4 + max-3-cycles loop honored on gate failures with explicit failure-attached constraints; wave sizing applied when WPs > 6.

### Dimension 3: Asset-Role Mapping
Did the orchestrator pick the right DEV (and REVIEW) subagent for the asset kind per `asset-to-role-map.md`?

- **Level 1:** Wrong role for the asset (e.g. `software-engineer` editing a SKILL.md, or `prompt-engineer` editing a hook script).
- **Level 2:** Right DEV but wrong REVIEW (e.g. `software-engineer` reviewing a SKILL.md when prompt-engineer was the correct reviewer).
- **Level 3:** Right roles for all assets; one cross-boundary WP not split (e.g. SKILL.md + hook bundled in one WP).
- **Level 4:** Right roles + cross-boundary WPs split per multi-asset table; REVIEW spawn carries `disallowedTools: ["Write", "Edit"]`.
- **Level 5:** All of L4 + sequential per-file gate honored; co-review explicitly NOT used (one reviewer per WP).

### Dimension 4: Eval-Loop Closure
Did the run close the eval loop where required (rubric present, calibration ≥ 6 samples, `/eval --tier 1` pass, Lead-side post-checks all green)?

- **Level 1:** No eval invoked at all on a `create`/`improve` touching a user-invocable workflow skill or rubric.
- **Level 2:** Rubric exists but no calibration samples; or `/eval --tier 1` not run; or validate.py exit-code not checked.
- **Level 3:** Rubric + calibration + validate.py all checked; one Lead-side post-check missing (e.g. `/plugin-doctor`).
- **Level 4:** All four post-checks pass — `validate.py`, internal audit per `plugin-skill-audit/SKILL.md`, `/plugin-doctor`, `/eval --tier 1` — and the summary lists their results.
- **Level 5:** All of L4 + counts in `plugin/dev/validate.py` `EXPECTED_COUNTS` bumped in the same change set when assets were added or hidden.

### Dimension 5: Memory & Trace Hygiene
Did the run produce the required memory entries (L4 `runs.log`; `fix-cycles/<stamp>.json` on `fix-feedback`) and a clean final summary?

- **Level 1:** No memory entry written; no summary; no record that the run happened.
- **Level 2:** Summary printed but `runs.log` not appended; or `fix-feedback` produced no `fix-cycles/<stamp>.json` mapping WPs to `finding_id`s.
- **Level 3:** `runs.log` present; on `fix-feedback`, the JSON written but missing `unfixed_findings` or `follow_ups` keys.
- **Level 4:** Both files complete; summary cites the closed WPs and any escalations; PII not present in any log.
- **Level 5:** All of L4 + Codex/Windsurf parity warning surfaced when a touched asset has a mirror outside `plugin/`; `--learnings` correctly routed through `/learnings-write` when flag passed.

## Scoring Logic

- **Aggregate:** average of D1–D5
- **Pass threshold:** 4.0
- **Judge model:** Haiku default; Sonnet when the run touched multiple asset kinds or used the `--md` fallback (those increase ambiguity in evidence anchoring)

## Anti-Patterns (Auto-Fail)

- Lead edited a SKILL.md / agent.md / rubric inline instead of spawning DEV (HEAVY pipeline violation).
- Spawn payload missing required G7 fields (`trace_id`, `subagent_role`, `goal`, `constraints`, `allowed_tools`, `budget`).
- `fix-feedback` consumed the Markdown report without warning when the JSON counterpart existed.
- Renamed or deleted an existing skill / agent automatically (must refuse).
- Touched files outside `plugin/`.
- Skipped `validate.py` re-run after counts-impacting change.

## Calibration Reference

- **Known-good:** `plugin/eval/calibration/plugin-author/good/*`
- **Known-bad:** `plugin/eval/calibration/plugin-author/bad/*`
