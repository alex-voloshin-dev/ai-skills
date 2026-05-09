# Eval Rubric

## Overview

Evaluates `/eval` skill output — the wrapper around `plugin/eval/runner.py`. Six dimensions × five levels. Tier 1 (linters) and Tier 2 (judge-calibration drift smoke) are shipped today; Tier 3, `--baseline`, and `--all --resume` are documented for design continuity but **not implemented** — invoking them must be surfaced as planned-not-shipped, never silently reported as success.

## Dimensions

### Dimension 1: Tier Identification
Correct selection of Tier 1 vs Tier 2 (vs marking Tier 3 as planned). Tier matches the user's invocation flag.

- **Level 1:** Wrong tier ran (Tier 1 reported when user asked `--tier 2`, or vice versa)
- **Level 2:** Right tier ran but mislabeled in the report
- **Level 3:** Right tier ran + labeled correctly
- **Level 4:** All of L3 + Tier 3 (or `--baseline` / `--resume`) explicitly flagged as "planned, not shipped" if the user invoked it
- **Level 5:** All of L4 + cite the `runner.py --tier 3` exit code 3 as the structural signal

### Dimension 2: Findings Clarity
Each finding has file:line + severity + actionable fix.

- **Level 1:** Findings cryptic; just rule names without context
- **Level 2:** File path given; line number missing
- **Level 3:** file:line + severity present; fix vague
- **Level 4:** file:line + severity + concrete fix per finding
- **Level 5:** All of L4 + auto-fix command shown where applicable

### Dimension 3: Calibration Interpretation (Tier 2)
Tier 2 score-band failures explained correctly: the runner verifies each sample's judge score lands within ±0.5 of the encoded filename score (e.g., `auth-flow.score-4.2.md` must score 3.7–4.7).

- **Level 1:** Tier 2 described as "activation precision" or some other pre-v0.3.5 spec
- **Level 2:** Score-band concept mentioned; tolerance value wrong
- **Level 3:** ±0.5 tolerance + filename-encoded expectation explained
- **Level 4:** All of L3 + drift class identified (rubric / judge-model / sample) when a band check fails
- **Level 5:** All of L4 + suggested next step (rubric edit, model pin, sample re-grade)

### Dimension 4: Boundary Discipline
Does not invoke planned features (Tier 3, `--baseline`, `--resume`) without flagging "not shipped". Refuses to fabricate output for surfaces that do not exist (e.g., `plugin/eval/cases/<skill>/`, `plugin/eval/results/<run-id>/`).

- **Level 1:** Reports planned feature output as if it ran
- **Level 2:** Acknowledges planned feature partially; still claims partial result
- **Level 3:** Refuses planned feature; mentions exit code or error
- **Level 4:** Refuses + explains "not shipped" + points to skill body or roadmap
- **Level 5:** All of L4 + cites the specific `runner.py` branch that returns the planned-error code

### Dimension 5: Token-Budget Awareness
Respects Tier 2 soft/hard caps from `eval/config.json` (50K soft / 150K hard). Reports estimated cost for Tier 2 runs; flags overruns.

- **Level 1:** No cost or budget mention for Tier 2
- **Level 2:** Cost mentioned in vague terms ("a few cents")
- **Level 3:** Token estimate present; soft/hard cap not referenced
- **Level 4:** Token estimate + soft/hard cap referenced from config.json
- **Level 5:** All of L4 + delta vs cap shown (e.g., "12K of 50K soft / 150K hard")

### Dimension 6: Report Shape
Clear pass/fail verdict + counts (CRITICAL / WARNING) + actionable next steps.

- **Level 1:** No clear verdict; just raw runner output dumped
- **Level 2:** Verdict present; counts missing
- **Level 3:** Verdict + counts; next steps absent
- **Level 4:** Verdict + counts + concrete next-steps list
- **Level 5:** All of L4 + per-skill or per-rubric breakdown when scope > 1

## Scoring Logic

- **Aggregate:** average of D1–D6
- **Pass threshold:** 3.5 (meta-skill — looser than user-facing skills, since output shape is mostly a runner pass-through)
- **Judge model:** Haiku (deterministic wrapper)

## Anti-Patterns (Auto-Fail)

- Tier 3 / `--baseline` / `--resume` invoked and reported as if it produced results
- Tier 2 described with the wrong specification (pre-v0.3.5 "activation precision")
- Silent fall-through on planned flags — failure must be surfaced to user
- Token-budget breach for Tier 2 with no warning
- Claims "0 findings" when runner exited non-zero

## Calibration Reference

- **Known-good:** `plugin/eval/calibration/eval/good/*`
- **Known-bad:** `plugin/eval/calibration/eval/bad/*`
