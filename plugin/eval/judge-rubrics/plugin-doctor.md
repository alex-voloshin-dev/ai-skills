# Plugin Doctor Rubric

## Overview

Evaluates `/plugin-doctor` output — the self-diagnostic for the ai-skills plugin. Six dimensions × five levels. Default mode is fast and cost-free (Tier 1 wrapper); `--calibrate-judge` is opt-in and delegates to Tier 2. `--runs --last N` and `--health-trends` are documented for design continuity but **not yet shipped**.

## Dimensions

### Dimension 1: Default-Mode Coverage
Default invocation reports on all four sub-checks: skill frontmatter, hooks.json reference resolution, JSON syntax (schemas + plugin.json + monitors.json + eval/config.json), and run-log parseability.

- **Level 1:** Two or more sub-checks missing from the report
- **Level 2:** Three of four sub-checks reported; one silently skipped
- **Level 3:** All four sub-checks reported
- **Level 4:** All four + per-check pass/warn/fail badge + counts
- **Level 5:** All of L4 + first-run handling (no `.ai-skills-memory/` → suggest `/ai-skills-init`)

### Dimension 2: Calibration Delegation
`--calibrate-judge` correctly delegates to `runner.py --tier 2` and surfaces the score-band tolerance check (±0.5 around filename-encoded score).

- **Level 1:** `--calibrate-judge` ignored or runs the wrong tier
- **Level 2:** Delegates to Tier 2 but mislabels what Tier 2 checks
- **Level 3:** Delegates correctly; mentions ±0.5 band
- **Level 4:** All of L3 + lists drift classes (rubric / judge / sample) on failure
- **Level 5:** All of L4 + DRY-RUN graceful path when `ANTHROPIC_API_KEY` is unset

### Dimension 3: Failure-Mode Framing
Known false positives (hook-script-missing-exec-bit since v0.3.3 wrapper, marketplace.json absent at cache root in `--plugin-dir` mode, `hooks.json` `python3 ${CLAUDE_PLUGIN_ROOT}/...` wrapper form) are labeled as expected/INFO, not as warnings or failures.

- **Level 1:** Treats known false positives as real warnings; spams the report
- **Level 2:** Mentions the false positives but still elevates them to WARN
- **Level 3:** Labels them INFO with a one-line rationale
- **Level 4:** All of L3 + cites the version/commit that made them expected (v0.3.3 / `4ea3347`)
- **Level 5:** All of L4 + offers the user a way to suppress permanently if they want

### Dimension 4: Vapor-Flag Handling
`--runs --last N` and `--health-trends` invocations are explicitly marked planned, not silently fallen-through to default mode or — worse — fabricated output.

- **Level 1:** Vapor flag invoked; output fabricated as if real
- **Level 2:** Vapor flag silently falls through to default mode without notice
- **Level 3:** Refuses + mentions "planned"
- **Level 4:** Refuses + cites the skill body's "Planned, not yet shipped" section + tracks where the feature will appear
- **Level 5:** All of L4 + suggests the closest currently-supported alternative

### Dimension 5: Report Clarity
Pass / warn / fail counts at top + per-check line-level details + suggested fix per failure.

- **Level 1:** No counts; just a stream of unstructured output
- **Level 2:** Counts present; details missing
- **Level 3:** Counts + details; no per-fail fix suggestion
- **Level 4:** Counts + details + per-fail fix suggestion
- **Level 5:** All of L4 + machine-readable summary section (JSON or counts table)

### Dimension 6: Audit-Log Discipline
Appends an entry to `.ai-skills-memory/plugin-doctor.log` per memory-discipline. Entry includes timestamp, mode (default vs `--calibrate-judge`), and verdict.

- **Level 1:** No log entry written
- **Level 2:** Log entry written; missing timestamp or verdict
- **Level 3:** Log entry has timestamp + mode + verdict
- **Level 4:** All of L3 + exit code recorded
- **Level 5:** All of L4 + diff vs previous run noted (e.g., "first WARN since 3 runs ago")

## Scoring Logic

- **Aggregate:** average of D1–D6
- **Pass threshold:** 3.5 (meta-skill — wraps the runner, so output shape carries less novel judgment than user-facing skills)
- **Judge model:** Haiku (deterministic wrapper)

## Anti-Patterns (Auto-Fail)

- Reports known false positives (exec-bit since v0.3.3, marketplace.json absent at cache root) as real warnings
- `--runs --last N` or `--health-trends` invoked and output fabricated
- `--calibrate-judge` runs without `ANTHROPIC_API_KEY` and crashes instead of DRY-RUN
- Skips the audit-log append silently
- Reports PASS while the underlying `runner.py --tier 1` exited non-zero

## Calibration Reference

- **Known-good:** `plugin/eval/calibration/plugin-doctor/good/*`
- **Known-bad:** `plugin/eval/calibration/plugin-doctor/bad/*`
