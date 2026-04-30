---
name: eval
description: Run plugin evaluation tiers — Tier 1 linters, Tier 2 sampled smoke, Tier 3 full behavioral suites. Wraps the eval/runner.py harness. Use for pre-release validation, regression detection, or skill tuning. Tier 1 is free (no LLM); Tiers 2 and 3 budget tokens per `eval/config.json`.
context: fork
argument-hint: "[skill-name | --tier N | --all]"
---

# /eval — Plugin Evaluation Harness

Validate skills and agents against rubric-scored test cases. Three tiers:

- **Tier 1 — linters:** frontmatter, schema, reference checks. No LLM calls. Always free
- **Tier 2 — smoke:** 10 sampled skills × 20 prompts each, activation precision check. ~60K tokens with Haiku judge
- **Tier 3 — behavioral:** full test cases per skill, executor + judge + blind-comparator. 30–100K tokens per skill

## Invocation

```
/eval feature-design                     # all tiers for one skill
/eval --skill feature-design --tier 3    # Tier 3 only for one skill
/eval --tier 2                           # Tier 2 smoke across sampled skills
/eval --all                              # Tier 3 full suite — release-gate run
/eval --all --resume                     # resume after interruption
/eval --baseline <skill>                 # capture per-skill baseline scorecard
```

## Token budgets

Per `plugin/eval/config.json` (D11 token-based budgets fit Max-subscription model):

| Tier | Soft cap | Hard cap |
|---|---|---|
| Tier 1 | 0 | 0 (no LLM) |
| Tier 2 smoke | 50K | 150K |
| Tier 3 per-skill | 30K | 100K (60K/150K with Sonnet judge override) |
| Tier 3 full suite | 500K | 1.5M |

## Judge model selection

Default judge: **Haiku** (fast, cheap). Sonnet override per `eval/config.json`:
- Rubric calibration Spearman < 0.7
- Rubric explicitly marked `judge_model: sonnet` in case JSON
- Subjective rubrics (faithfulness, security-soundness)

## Output

- `plugin/eval/results/<run-id>/summary.json` — overall pass/fail per skill
- `plugin/eval/results/<run-id>/<skill>/<case-id>.json` — per-case scores per dimension
- Console: pass/fail summary + token totals + duration

## Resume support

`--resume` picks up from the last completed case in `summary.json` — useful for long Tier 3 full-suite runs interrupted by network or rate-limit.

## Blind-comparator (Round 3 Q3)

Tier 3 cases that ship a `comparator-prompt` field run a third agent in an isolated subagent context with skills suppressed via instruction. Validates that the executor's output is genuinely better than a vanilla baseline. Suppression compliance is probed per `eval/config.json` `blind_comparator.suppression_compliance_probe`.

## Integration

- **Wraps**: `plugin/eval/runner.py` (B10 deliverable)
- **Reads**: `plugin/eval/config.json` (token caps + judge model + calibration thresholds)
- **Reads**: `plugin/eval/judge-rubrics/<skill>.md` (per-skill rubrics, B10)
- **Reads**: `plugin/eval/cases/<skill>/*.json` (test cases, B10)
- **Reads**: `plugin/eval/calibration/<rubric>/` (calibration samples, B10a)
- **Spawns**: `eval-judge` agent (G7 spawn payload required)
- **Honors**: `userConfig.ralph_session_*` caps if eval cases trigger embedded RALF
- **Memory writes**: `.committed/eval-baselines/<release-tag>.json` when `--baseline` flag used
- **Used by**: `/plugin-doctor` (Tier 1 + opt-in calibration), CI (release gate `--all`)
