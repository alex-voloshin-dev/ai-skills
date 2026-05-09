---
name: eval
description: Run plugin evaluation tiers — Tier 1 linters and Tier 2 judge-calibration drift smoke. Wraps the eval/runner.py harness. Use for pre-release validation, regression detection, or skill tuning. Tier 1 is free (no LLM); Tier 2 budgets tokens per `eval/config.json`. Tier 3 (full behavioral suites) is planned but not yet shipped — runner returns error code 3 if invoked.
context: fork
argument-hint: "[skill-name | --tier 1|2 | --rubric NAME]"
---

# /eval — Plugin Evaluation Harness

Validate the plugin against rubric-scored test cases. Two tiers shipped today:

- **Tier 1 — linters** (shipped, free): frontmatter, schema, hook-reference, char-limit, JSON-syntax, AST checks. No LLM calls.
- **Tier 2 — judge-calibration drift smoke** (shipped, opt-in): for each sampled rubric, the Haiku judge scores the shipped good + bad calibration samples, and the result is checked against a ±0.5 score-band tolerance around the score encoded in each filename (`<scenario>.score-X.X.md`). This catches three drift classes:
  1. **Rubric drift** — someone edits the rubric in a way that breaks scoring
  2. **Judge model drift** — Anthropic ships a new Haiku version that scores samples differently
  3. **Sample drift** — someone edits a calibration sample so it no longer hits its band
- **Tier 3 — behavioral** (planned, not shipped): full executor + judge + blind-comparator per skill case. `runner.py --tier 3` currently exits with error code 3.

## Invocation

Shipped commands:

```text
/eval                                  # Tier 1 linters across all skills
/eval feature-design                   # Tier 1 lint scoped to one skill
/eval --tier 2                         # Tier 2 judge-calibration smoke (default 10 rubrics × 2 samples)
/eval --tier 2 --rubric feature-design # Tier 2 limited to one rubric
/eval --tier 2 --dry-run               # plan-only; no API calls (also auto-applies if anthropic SDK unavailable)
/eval --all                            # Tier 1 + Tier 2 in one run
```

Planned (not yet shipped — runner returns error code 3):

```text
/eval --tier 3                         # full behavioral suite (planned)
/eval --skill <name> --tier 3          # Tier 3 per-skill (planned)
/eval --baseline <skill>               # capture per-skill baseline scorecard (planned)
/eval --all --resume                   # resume after interruption (planned, Tier 3 only)
```

## Tier 2 details

Sample plan (default seed 42): 10 rubrics × 2 samples = 20 judge calls. Override via runner flags `--seed N`, `--sample-rubrics N`, `--samples-per-rubric N`, `--rubric NAME`.

Requires `ANTHROPIC_API_KEY` and the `anthropic` Python SDK. Without either, the runner reports `DRY-RUN ONLY` and skips actual API calls.

Default judge model: **Haiku** (`claude-haiku-4-5`). Per-rubric override allowed when calibration Spearman drops below threshold (see `plugin/eval/config.json` → `judge_models`).

## Token budgets

Per `plugin/eval/config.json`:

| Tier | Soft cap | Hard cap | Notes |
|---|---|---|---|
| Tier 1 | 0 | 0 | No LLM. Always free. |
| Tier 2 smoke | 50K | 150K | Default plan ~10–20K with Haiku. |
| Tier 3 (planned) | 30K | 100K | Per-skill (60K/150K with Sonnet judge override). Not shipped. |
| Tier 3 full suite (planned) | 500K | 1.5M | Release-gate run. Not shipped. |

## Output

- Tier 1: stderr findings + summary count of CRITICAL / WARNING. Exit code 0/1/2.
- Tier 2: per-sample PASS/FAIL with score delta + dry-run skip count. Exit code 0/1/2.

## Integration

- **Wraps**: `plugin/eval/runner.py` (entry) + `plugin/eval/tier2.py` (Tier 2 implementation)
- **Reads**: `plugin/eval/config.json` (token caps + judge models + calibration thresholds)
- **Reads**: `plugin/eval/judge-rubrics/<rubric>.md` (per-rubric scoring criteria)
- **Reads**: `plugin/eval/calibration/<rubric>/{good,bad}/<scenario>.score-X.X.md` (Tier 2 calibration samples — 17 rubrics × 6 samples = 102 total)
- **Honors**: `userConfig.ralph_session_*` caps if eval cases ever trigger embedded RALF (Tier 3, planned)
- **Used by**: `/plugin-doctor --calibrate-judge` (Tier 2 opt-in)

## Future surfaces (not currently wired)

These are referenced by the planned Tier 3 design but **not implemented**:

- `plugin/eval/cases/<skill>/*.json` — per-skill behavioral test cases. Directory does not exist; expect to ship in Phase 4.
- `plugin/eval/results/<run-id>/` — per-run output artefacts.
- `eval-judge` subagent role — currently inline; if the planned design needs a dedicated agent, it would land in `plugin/agents/`.
- `--baseline <skill>` capture to `.committed/eval-baselines/<release-tag>.json`.
- Blind-comparator (third agent in isolated context with skills suppressed) — design-only.

Do not write code that depends on these surfaces today; they are documented for design continuity, not behavior.
