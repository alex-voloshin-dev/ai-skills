# /plugin-doctor — Calibration (DRY-RUN)

> Invocation: `/plugin-doctor --calibrate-judge`
> Wraps: `python3 plugin/eval/runner.py --tier 2`
> Mode: DRY-RUN (`ANTHROPIC_API_KEY` not set; anthropic SDK present)

## Verdict

**PASS (DRY-RUN)** — sample plan resolved cleanly across 10 sampled rubrics × 2 samples = 20 pairs. No live judge calls performed because `ANTHROPIC_API_KEY` is unset; the runner gracefully reported `DRY-RUN ONLY` instead of crashing.

## What `--calibrate-judge` checks

Delegates to Tier 2 of the eval runner — score-band tolerance check against `plugin/eval/calibration/<rubric>/` samples. The Haiku judge scores known good + known bad samples; the result must land within ±0.5 of the score encoded in the filename (`<scenario>.score-X.X.md`).

Catches three drift classes:
1. Rubric drift (rubric edits that break scoring)
2. Judge-model drift (Haiku version change scores differently)
3. Sample drift (calibration sample edits move it out of band)

## Sample plan (seed 42)

```
Sampled rubrics:    10 of 17
Samples per rubric: 2 (1 good + 1 bad)
Total pairs:        20
```

All 20 pairs resolved to existing files; bands computed; no live API calls performed.

## Counts

```
PASS:           20 (DRY-RUN resolutions)
LIVE JUDGE:      0 (no API key)
OUT-OF-BAND:     0
```

Exit code: 0

## Audit log

Appended to `.ai-assets-memory/plugin-doctor.log`:

```
2026-05-08T14:24:03Z mode=calibrate-judge verdict=PASS-DRY-RUN exit=0 pairs=20 live=0
```

## Next steps

- Set `ANTHROPIC_API_KEY` and re-run for live judge scoring (~12K tokens at Haiku price).
- Default-mode `/plugin-doctor` already passed; no further action required.
