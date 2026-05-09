# /eval — Tier 2 Activation Precision Check

> Invocation: `/eval --tier 2`

## Verdict

**PASS** — activation precision across all 53 skills measured at 94%. Above the 90% pass bar.

## What Tier 2 measures

Tier 2 measures how reliably each skill's H5 trigger phrase activates on the intended user intents and avoids activating on near-misses. We sample ~20 prompt variants per skill and score true-positive / false-positive rate.

## Per-skill activation precision

| Skill | TP rate | FP rate | Precision |
|---|---|---|---|
| feature-design | 92% | 4% | 95% |
| bugfix | 88% | 6% | 93% |
| docs-pack | 95% | 5% | 95% |
| ... | ... | ... | ... |

## Counts

```
Skills sampled:     53
Avg precision:      94%
Below 90%:          2 skills (memory-init, env-analyze)
```

Exit code: 0

## Recommended next steps

Tighten the trigger phrase on `memory-init` and `env-analyze` to reduce false positives.
