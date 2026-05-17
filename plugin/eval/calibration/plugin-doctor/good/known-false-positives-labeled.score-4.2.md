# /plugin-doctor — Default Mode (with known false positives)

> Invocation: `/plugin-doctor`
> Wraps: `python3 plugin/eval/runner.py --tier 1`
> Install mode: `claude --plugin-dir /path/to/ai-skills/plugin` (local dev)

## Verdict

**PASS** — all four sub-checks green. Two known-false-positive surfaces correctly labeled INFO (not WARN) per skill body.

## Sub-checks

| Check | Status | Detail |
|---|---|---|
| Skill frontmatter | PASS | 53 SKILL.md files OK |
| Hook references | PASS | 18 hooks resolved; wrapper form accepted |
| JSON validity | PASS | All required JSON files parse |
| Run-log parseability | PASS | `.ai-skills-memory/runs.jsonl` parses |

## INFO (expected; not warnings)

```
INFO  hooks/scripts/*.py — exec bit absent on 19 scripts
      Expected since v0.3.3 (commit 4ea3347). Hooks invoke via the wrapper form
      `python3 ${CLAUDE_PLUGIN_ROOT}/hooks/scripts/<name>.py`, which does not
      need the exec bit. Reverting would re-introduce the v0.3.2 "Permission
      denied" install bug. Action: none.

INFO  ~/.claude/plugins/cache/<owner>/ai-skills/.claude-plugin/marketplace.json absent
      Expected in `claude --plugin-dir` install mode. The repo-level
      `/<repo>/.claude-plugin/marketplace.json` is the source of truth and is
      consumed only by `/plugin marketplace add`. `--plugin-dir` is the
      supported install mode for local development of this repo. Action: none.

INFO  hooks.json command form starts with `python3 ${CLAUDE_PLUGIN_ROOT}/...`
      Expected since v0.3.3 (same reason as above). The Tier 1 linter accepts
      both `python3 ${CLAUDE_PLUGIN_ROOT}/...` (wrapper, current) and bare
      `${CLAUDE_PLUGIN_ROOT}/...` (legacy) forms by searching for the
      placeholder substring. Third-party validators that flag this are
      linter-bugs, not plugin-bugs. Action: none.
```

## Counts

```
PASS:  4
WARN:  0
FAIL:  0
INFO:  3 (all known-expected; no action required)
```

Exit code: 0

## Audit log

Appended to `.ai-skills-memory/plugin-doctor.log`:

```
2026-05-08T14:30:18Z mode=default verdict=PASS exit=0 pass=4 warn=0 fail=0 info=3
```
