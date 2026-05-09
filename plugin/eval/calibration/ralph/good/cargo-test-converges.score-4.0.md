# /ralph — converge contract tests

> Run-id: `ralph-2026-05-03-contract-fix`
> Oracle: `cargo test --quiet -p contract -- --test-threads=1` exits 0
> Kill-on: `no-progress=2,token-spike=2x,repeat-error=3`
> Caps: `ralph_session_max_iter=10`, `ralph_session_max_tokens=200000`

## Iter 001 (init prompt)

Goal: 4 failing tests under `contract::serializer::*`.
Action: ran oracle → 4 failures captured. Patched `serializer::encode` for the first failure (mismatched discriminator).
Oracle exit: 1 (3 failing). Tokens: in=18421, out=2104, cache=0.

## Iter 002 (continuation prompt G10)

Continuation prompt template — sent only: failed assertions + last patch + oracle stderr tail. Full repo context not replayed.
Action: fixed null-handling in `decode`.
Oracle exit: 1 (1 failing). Tokens: in=4218, out=1612, cache=14882.

## Iter 003 (continuation prompt G10)

Action: corrected enum-tag wire format.
Oracle exit: 0 — converged. Tokens: in=3801, out=982, cache=15110.

## Termination

- Reason: oracle satisfied
- Iterations: 3
- Total tokens: in=26440, out=4698, cache-read=29992
- Token saving from continuation prompts (iter 2-3 vs replaying iter-1 context): ~58%
- All caps respected (3/10 iter, 31k/200k tokens)

## Telemetry written

```
.ai-assets-memory/ralph/ralph-2026-05-03-contract-fix/
  iter-001/tokens.json   {input:18421, output:2104, cache_read:0, duration_s:42, oracle_exit:1}
  iter-002/tokens.json   {input:4218,  output:1612, cache_read:14882, duration_s:18, oracle_exit:1}
  iter-003/tokens.json   {input:3801,  output:982,  cache_read:15110, duration_s:14, oracle_exit:0}
  summary.json           {iters:3, terminated:"converged", total_input:26440, total_output:4698}
```

## Per-iter trend

Failing-tests count: 4 → 3 → 1 → 0 (monotonically improving — kill-on `no-progress` never triggered).
