# /plugin-doctor — Default Mode

> Invocation: `/plugin-doctor`

## Verdict

**WARN** — 19 hook scripts are missing the executable bit. Plugin may not function correctly.

## Sub-checks

| Check | Status | Detail |
|---|---|---|
| Skill frontmatter | PASS | 53 skills OK |
| Hook references | WARN | 19 of 18 scripts non-executable; see below |
| JSON validity | PASS | All JSON parses |
| Run-log parseability | PASS | runs.jsonl parses |

## Warnings

```
WARN  hooks/scripts/audit-pretooluse.py — chmod +x missing
WARN  hooks/scripts/audit-posttooluse.py — chmod +x missing
WARN  hooks/scripts/auto-format.py — chmod +x missing
WARN  hooks/scripts/block-secrets.py — chmod +x missing
WARN  hooks/scripts/context-health-watcher.py — chmod +x missing
WARN  hooks/scripts/deny-network-egress.py — chmod +x missing
WARN  hooks/scripts/env-watch-trigger.py — chmod +x missing
WARN  hooks/scripts/format-on-save.py — chmod +x missing
WARN  hooks/scripts/g7-spawn-validator.py — chmod +x missing
WARN  hooks/scripts/g8-context-meter.py — chmod +x missing
WARN  hooks/scripts/learnings-curator.py — chmod +x missing
WARN  hooks/scripts/memory-write-guard.py — chmod +x missing
WARN  hooks/scripts/post-compact-summary.py — chmod +x missing
WARN  hooks/scripts/pre-compact-snapshot.py — chmod +x missing
WARN  hooks/scripts/ralph-iter-meter.py — chmod +x missing
WARN  hooks/scripts/session-end-rollup.py — chmod +x missing
WARN  hooks/scripts/session-start-loader.py — chmod +x missing
WARN  hooks/scripts/subagent-depth-guard.py — chmod +x missing
WARN  hooks/scripts/task-result-logger.py — chmod +x missing
```

## Counts

```
PASS:  3
WARN:  19
FAIL:  0
```

Exit code: 1

## Recommended fix

Run `chmod +x plugin/hooks/scripts/*.py` to make hook scripts executable.
