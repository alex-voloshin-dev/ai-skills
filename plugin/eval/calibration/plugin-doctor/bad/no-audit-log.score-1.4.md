# /plugin-doctor — Default Mode

> Invocation: `/plugin-doctor`
> Wraps: `python3 plugin/eval/runner.py --tier 1`

## Verdict

**PASS** — all four sub-checks green.

## Sub-checks

| Check | Status | Detail |
|---|---|---|
| Skill frontmatter | PASS | 53 SKILL.md files OK |
| Hook references | PASS | 18 hooks resolved |
| JSON validity | PASS | All JSON files parse |
| Run-log parseability | PASS | runs.jsonl parses |

## Counts

```
PASS:  4
WARN:  0
FAIL:  0
```

Exit code: 0

## Calibration

Calibration not yet run; use `/plugin-doctor --calibrate-judge` to run Tier 2.

## Done

Plugin is healthy. Ready to use.
