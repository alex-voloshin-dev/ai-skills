# /feedback — Output (wrong session source, fabricated verdict)

> Invocation: `/feedback`

# Plugin Feedback — Brief

- Verdict: **GREEN** · Window: 7d · Sessions: 0/0 · Findings: 0 (0 signatures)
- Plugin: `ai-assets` · Project: `/home/u/dev/code/ai-assets`

## Top 5 failure signatures

(none — no errors detected)

## Top 3 recommendations

1. Keep using the plugin as-is.
2. Nothing to fix.
3. Excellent reliability!

## What to do next

- All good!

(internally the skill scanned the wrong directory — it tried `./logs/` instead of `~/.claude/projects/<sanitized-cwd>/` — and silently reported GREEN; meanwhile the real session dir contained a hook permission-denied error that should have surfaced as YELLOW)
