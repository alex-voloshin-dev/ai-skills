# Memory write — bypassed memory-curator

## What happened

A skill wrote directly to `.ai-assets-memory/learnings.md` without spawning the `memory-curator` agent. The entry contained a hardcoded API key from a tool output that wasn't PII-filtered. The skill also wrote to `~/.claude/ai-assets/learnings.md` (L5) without the `--global` flag and without checking `userConfig.user_global_memory_enabled`.

## Entry written

```
Note: The Stripe key for testing is sk_test_4eC39H... and the prod webhook secret is whsec_abc...

Found this in the codebase. Documenting for future reference.
```

## Violations

- **Anti-pattern triggered:** wrote secrets / PII to memory layer (PII filter bypassed)
- **Anti-pattern triggered:** wrote to L5 without `--global` flag
- **Anti-pattern triggered:** skill wrote to learnings.md directly instead of spawning `memory-curator`
- No schema compliance — free-form note instead of structured entry
- No retention policy applied
