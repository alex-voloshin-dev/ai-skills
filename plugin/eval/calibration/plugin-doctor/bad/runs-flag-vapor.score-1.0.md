# /plugin-doctor — Recent Runs Summary

> Invocation: `/plugin-doctor --runs --last 5`

## Verdict

**OK** — last 5 workflow runs summarized below.

## Recent runs

| Run ID | Skill | Started | Duration | Status |
|---|---|---|---|---|
| run-0142 | feature-design | 2026-05-07 09:14 | 18m 22s | PASS |
| run-0141 | bugfix | 2026-05-06 16:02 | 7m 11s | PASS |
| run-0140 | develop | 2026-05-06 11:45 | 33m 04s | PASS |
| run-0139 | security-audit | 2026-05-05 14:30 | 12m 50s | PASS |
| run-0138 | refactor | 2026-05-05 09:18 | 21m 33s | FAIL (test gate) |

## Trend

4 of last 5 runs passed. Average duration 18m. No regressions detected versus the prior 5-run window.

## Counts

```
Runs analyzed: 5
PASS:          4
FAIL:          1
```

## Next steps

Investigate `run-0138` (refactor) — the test-equivalence gate failed.
