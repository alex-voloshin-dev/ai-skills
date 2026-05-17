# /feedback — Brief Output (severity floor = error)

> Invocation: `/feedback --severity error --days 14`
> Worker: `python3 plugin/skills/feedback/scripts/collect_session_data.py --severity error --days 14`

# Plugin Feedback — Brief

- Verdict: **YELLOW** · Window: 14d · Sessions: 11/11 · Findings: 1 (1 signature)
- Plugin: `ai-skills` · Project: `/home/u/dev/code/ai-skills`

## Top 5 failure signatures

| # | Sev | Kind | Source | Signature | Count |
|---|---|---|---|---|---:|
| 1 | error | hook | ralph-stop.py | Failed with non-blocking status code: `<path>`: `<n>`: `<path>`: Permission denied | 1 |

## Top 3 recommendations

1. **[f-3a91c5b2] hook: ralph-stop.py permission-denied** — confirm `python3 ${CLAUDE_PLUGIN_ROOT}/hooks/scripts/ralph-stop.py` wrapper form in `plugin/hooks/hooks.json`. Owner: `plugin/hooks/hooks.json`. Effort: S.
2. **Re-run with broader severity** to surface non-blocking warns: `/feedback --severity warn --days 14`.
3. **Run `/plugin-doctor`** to cross-check whether the failing hook is still wired correctly.

## What to do next

- Open the extended report for the full evidence block and surrounding events.
- Patch `plugin/hooks/hooks.json` if exec-bit is the root cause; otherwise file a bug under "hooks-runtime".

---

_Saved to:_ `/home/u/dev/code/ai-skills/.ai-skills-memory/feedback/feedback-2026-05-13-1014.md`
