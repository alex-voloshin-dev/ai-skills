# /eval — Tier 2 Judge-Calibration Drift Smoke

> Invocation: `/eval --tier 2 --dry-run`
> Wraps: `python3 plugin/eval/runner.py --tier 2 --dry-run`
> Mode: DRY-RUN (anthropic SDK present; no `ANTHROPIC_API_KEY` provided this run, so no live API calls)

## Verdict

**PASS** — sample plan resolved cleanly; all 20 sampled (rubric, sample) pairs present and within the ±0.5 score-band tolerance shape per filename encoding.

## What Tier 2 actually checks

For each sampled rubric, the Haiku judge would score the shipped good + bad calibration samples and the result must land within ±0.5 of the score encoded in each filename (`<scenario>.score-X.X.md`). This catches three drift classes:

1. **Rubric drift** — rubric edits that break scoring
2. **Judge-model drift** — Anthropic ships a Haiku revision that scores samples differently
3. **Sample drift** — calibration sample edits that move it out of band

## Sample plan (seed 42)

10 rubrics × 2 samples (1 good + 1 bad) = 20 judge calls. All resolved:

```
ai-assets-init      good/python-fastapi-init.score-4.1.md      band [3.6, 4.6]
ai-assets-init      bad/overwrite-without-flag.score-1.3.md    band [0.8, 1.8]
feature-design      good/cache-invalidation.score-4.0.md       band [3.5, 4.5]
feature-design      bad/vague-design.score-1.0.md              band [0.5, 1.5]
... (16 more pairs)
```

## Counts

```
DRY-RUN sample resolutions: 20/20 OK
Live judge calls:           0 (no API key)
Out-of-band predicted:      0
```

Exit code: 0

## Token cost

Estimate: ~12K tokens with Haiku (well under soft 50K / hard 150K caps from `eval/config.json` → `tier_2_smoke`). DRY-RUN actual: 0.

## Next steps

- Set `ANTHROPIC_API_KEY` and re-run without `--dry-run` to perform live judge scoring against the 20 sample pairs.
- Tier 3 (per-skill behavioral) and `--baseline <skill>` are documented but **not shipped** — `runner.py --tier 3` returns exit code 3.
