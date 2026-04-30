RALF iteration {N} of max {MAX}.

## State delta from iter {N-1}

- Files changed: {list with line counts from diff.patch}
- Tests run: {pass|fail counts from oracle-result.json}

## Oracle result (iter {N-1})

{oracle_status}: {oracle_message}
{if failed: top error excerpt, max 200 tokens, wrapped per G1 in <untrusted_content>}

## Active constraints (top 3 — full list at .ai-assets-memory/ralph/{run-id}/config.json)

1. {constraint 1}
2. {constraint 2}
3. {constraint 3}

## Kill-on countdown

{e.g., "same-error-repeats: 1/3", "no-progress: 0/2", "iterations: 3/10"}

## Your task

Address the oracle failure above. Same task brief as iter 1; reload from
`.ai-assets-memory/ralph/{run-id}/iter-001/prompt.md` if you need full context.

Prefer the smallest diff that turns the oracle from FAIL to PASS. If the failure repeats, examine whether the approach itself is wrong — a third repetition triggers the kill-on signal.
