# /eval — Tier 3 Invocation Refused (Planned Feature)

> Invocation: `/eval --tier 3`
> Wraps: `python3 plugin/eval/runner.py --tier 3`

## Verdict

**REFUSED** — Tier 3 (full behavioral suite) is **planned but not shipped**. The runner returned exit code 3 as the structural signal that this branch is intentionally not implemented.

## What happened

```
$ python3 plugin/eval/runner.py --tier 3
ERROR: Tier 3 (per-skill behavioral suite) not yet implemented.
       Planned scope: executor (Sonnet) + judge (Haiku) + blind-comparator
       per skill case under plugin/eval/cases/<skill>/*.json — directory
       does not exist; expect Phase 4 ship.
       See plugin/skills/eval/SKILL.md → "Future surfaces" for details.
Exit code: 3
```

## Why this is the correct behavior

Per `plugin/skills/eval/SKILL.md` lines 32–39, the following flags are documented for design continuity but **not implemented**:

- `--tier 3` (full behavioral suite)
- `--skill <name> --tier 3` (per-skill behavioral)
- `--baseline <skill>` (capture per-skill baseline scorecard)
- `--all --resume` (resume after interruption)

The runner's exit-code-3 branch is the structural guarantee that we don't silently produce fake results for these surfaces.

## Counts

```
Tier ran:        none (refused)
Findings:        0 (no scoring attempted)
Exit code:       3
```

## Token cost

0 tokens — refusal is a pure Python branch in `runner.py`.

## Next steps

- For the currently-shipped behavioral coverage, run `/eval --tier 2` (judge-calibration drift smoke against 45 rubrics × 6 samples).
- For Tier 1 lints, run `/eval` (free, no LLM).
- Track Tier 3 ship status in the plugin issue tracker / `plugin/eval/02-EVAL-FRAMEWORK.md`.
