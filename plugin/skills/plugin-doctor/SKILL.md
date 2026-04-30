---
name: plugin-doctor
description: Self-diagnostic for the ai-assets plugin — validates skill frontmatter, hook executability, run-log parseability, and judge calibration. Default mode is fast and cost-free; --calibrate-judge is opt-in (Round 4 O4). Use after install, after upgrades, or when something feels off.
context: fork
argument-hint: "[--calibrate-judge | --runs --last N | --health-trends]"
---

# /plugin-doctor — Plugin Self-Diagnostic

Check that the plugin is installed correctly and operating within healthy bounds. Default mode is fast (linter-only, no LLM cost) and always passes on a clean install.

## Invocation

```
/plugin-doctor                          # default smoke test
/plugin-doctor --calibrate-judge        # opt-in: judge calibration vs samples
/plugin-doctor --runs --last 5          # summarize last 5 workflow runs
/plugin-doctor --health-trends          # context health metrics summary (G8)
```

## Two-step boot model (Round 4 O4)

### Default mode (`/plugin-doctor`)

Runs and reports only on:
- **Skill frontmatter** — `name` + `description` present, lowercase-hyphens, third-person, `Use when` trigger pattern (H5). Validates against `plugin/eval/judge-rubrics/`-format schema.
- **Hook scripts** — executable bit set (where applicable), Python syntax valid (`python3 -m py_compile`)
- **Hook references** — every entry in `plugin/hooks/hooks.json` resolves to an existing script under `${CLAUDE_PLUGIN_ROOT}/hooks/scripts/`
- **Run logs** — `.ai-assets-memory/runs.jsonl` parses; summarize total runs, avg duration, token totals, success rate
- **Schema integrity** — `plugin/schemas/*.schema.json` parse as valid JSON Schema 2020-12

Reports calibration as `not yet run; use /plugin-doctor --calibrate-judge to run`.

### `--calibrate-judge` (explicit opt-in)

Runs Spearman correlation per rubric against `plugin/eval/calibration/<rubric>/` samples (shipped in B10a). Errors clearly when samples missing or count too low (< 4 per rubric):

```
ERROR: Insufficient calibration samples at plugin/eval/calibration/<rubric>/.
       Expected ≥ 4 (good + bad pairs). Found N.
       See plugin/docs/concepts/eval.md for guidance.
```

Spearman < 0.7 triggers a Sonnet judge override flag in subsequent eval runs.

## Other modes

### `--runs --last N`

Summarize the last N runs from `.ai-assets-memory/runs.jsonl`:
- Workflow type
- Duration
- Token totals (input + output)
- Status (SUCCESS / FAILED / RALF_FAILED_BUDGET / etc.)
- Top error if failed

### `--health-trends`

Context health summary per Round 4 G8 — over the last 30 days:
- Average tokens per workflow
- p95 tokens per workflow
- RALF iteration distribution
- Top failure modes

## Output

- stdout: human-readable report
- `.ai-assets-memory/plugin-doctor.log` — append-only audit log

## Failure modes

- **No `.ai-assets-memory/`:** report as "first run — no history yet"; suggest `/ai-assets-init`
- **Hook script missing executable bit on Unix:** report as warning (Windows ignores); suggest `chmod +x`
- **Run log too large to parse fully:** stream-parse last 1000 lines; report partial stats with "(last 1000 events)" note

## Integration

- **Reads**: every file under `plugin/` for lints; `.ai-assets-memory/runs.jsonl`, `plugin-doctor.log` for summaries
- **Calls**: `eval/runner.py --tier 1` (Tier 1 linters); `eval/runner.py --calibrate` if `--calibrate-judge`
- **Memory writes**: `.ai-assets-memory/plugin-doctor.log` (audit trail)
- **Used by**: developers post-install, CI smoke before merge
