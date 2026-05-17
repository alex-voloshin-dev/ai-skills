# /feedback — Brief Output (7-day window, ai-skills, 8 findings in 2 groups)

> Invocation: `/feedback`
> Worker: `python3 plugin/skills/feedback/scripts/collect_session_data.py`
> Extended saved to: `.ai-skills-memory/feedback/feedback-2026-05-13-0905.md`

# Plugin Feedback — Brief

- Verdict: **YELLOW** · Window: 7d · Sessions: 11/11 · Findings: 8 (2 signatures)
- Plugin: `ai-skills` · Project: `/home/u/dev/code/ai-skills`

## Top 5 failure signatures

| # | Sev | Kind | Source | Signature | Count |
|---|---|---|---|---|---:|
| 1 | error | hook | ralph-stop.py | Failed with non-blocking status code: `<path>`: `<n>`: `<path>`: Permission denied | 1 |
| 2 | warn  | assistant | claude-opus-4-7 | stop_reason=max_tokens | 7 |

## Top 3 recommendations

1. **[f-3a91c5b2] hook: ralph-stop.py permission-denied** — restore exec-bit OR confirm the v0.3.3+ wrapper form `python3 ${CLAUDE_PLUGIN_ROOT}/hooks/scripts/ralph-stop.py` is used in `plugin/hooks/hooks.json`. Owner: `plugin/hooks/hooks.json`. Effort: S.
2. **[f-7d12af04] assistant: max_tokens stops (7 occurrences)** — review which skills consistently hit max_tokens; consider raising the `max_tokens_output` in their eval cases or splitting the skill body. Owner: `plugin/skills/<top-offender>/SKILL.md`. Effort: M.
3. **Open question** — confirm whether the ralph-stop permission-denied was a one-off (v0.3.2 install bug) or a re-introduction. Run `/plugin-doctor` to triangulate. Effort: S.

## What to do next

- For full evidence + sequence chains + per-finding context, open the extended report.
- To narrow scope: `/feedback --plugin ai-skills --severity error --days 14`.
- To dive into a specific session: `~/.claude/projects/-home-u-dev-code-ai-skills/<session-id>.jsonl`.

---

_Saved to:_ `/home/u/dev/code/ai-skills/.ai-skills-memory/feedback/feedback-2026-05-13-0905.md`
