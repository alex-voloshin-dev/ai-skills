# /eval — Tier 1 Linters

> Invocation: `/eval` (no flags, default tier)
> Wraps: `python3 plugin/eval/runner.py --tier 1`

## Verdict

**PASS** — 0 CRITICAL, 0 WARNING. Plugin is clean.

## What Ran

Tier 1 linters (free, no LLM calls):
- Skill frontmatter (53 SKILL.md files) — name + description present, kebab-case names, H5 trigger phrase recognizable
- Hook references (18 hook scripts under `hooks/scripts/`) — every entry in `hooks.json` resolves; `python3 ${CLAUDE_PLUGIN_ROOT}/...` wrapper form accepted (v0.3.3+)
- Hook script syntax (`py_compile` per script) — all parse
- Run logs (`.ai-skills-memory/runs.jsonl`) — JSON-syntax check; richer summaries are planned via `--runs --last N` (not shipped)
- JSON validity (`plugin/schemas/*.json`, `eval/config.json`, `monitors/monitors.json`, `.claude-plugin/plugin.json`) — all parse

## Counts

```
CRITICAL: 0
WARNING:  0
TOTAL:    0
```

Exit code: 0

## Token cost

Tier 1: 0 tokens (pure Python lints, no LLM calls per `eval/config.json` → `tier_1_linters.tokens_soft: 0`).

## Next steps

- For judge-calibration drift smoke (Tier 2), run `/eval --tier 2` (~10–20K tokens with Haiku, soft cap 50K / hard cap 150K from `eval/config.json`).
- Tier 3 (full behavioral suite) is **planned but not yet shipped** — `runner.py --tier 3` exits with error code 3.
- `--baseline <skill>` and `--all --resume` are also planned-not-shipped per skill body.
