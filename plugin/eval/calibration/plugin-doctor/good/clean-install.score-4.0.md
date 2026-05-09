# /plugin-doctor — Default Mode (Clean Install)

> Invocation: `/plugin-doctor`
> Wraps: `python3 plugin/eval/runner.py --tier 1`
> Mode: default (no `--calibrate-judge`)

## Verdict

**PASS** — all four sub-checks green. Plugin is operating within healthy bounds.

## Sub-checks

| Check | Status | Detail |
|---|---|---|
| Skill frontmatter | PASS | 53 SKILL.md files; name + description present; kebab-case names match parent dir; H5 trigger phrase present |
| Hook references | PASS | 18 hook scripts; every `hooks.json` entry resolves; `python3 ${CLAUDE_PLUGIN_ROOT}/...` wrapper form accepted (v0.3.3+) |
| JSON validity | PASS | `plugin/schemas/*.json` (2), `eval/config.json`, `monitors/monitors.json`, `.claude-plugin/plugin.json` — all parse |
| Run-log parseability | PASS | `.ai-assets-memory/runs.jsonl` parses (12 entries) |

## Counts

```
PASS:  4
WARN:  0
FAIL:  0
```

Exit code: 0

## Calibration

Calibration not yet run; use `/plugin-doctor --calibrate-judge` to run the Tier 2 judge-calibration drift smoke (delegates to `runner.py --tier 2`, ~12K tokens with Haiku).

## Audit log

Appended to `.ai-assets-memory/plugin-doctor.log`:

```
2026-05-08T14:22:11Z mode=default verdict=PASS exit=0 pass=4 warn=0 fail=0
```

## Planned modes (not yet shipped)

- `--runs --last N` — summarize last N workflow runs
- `--health-trends` — context-health metrics summary (G8)

Both will land once `runs.jsonl` accumulates enough entries.
