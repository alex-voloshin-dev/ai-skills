# Run Tests — `design-system` package (Jest snapshots)

## Stack Detection
- Detected: Node 22 / pnpm / Jest 29
- `jest.config.ts` confirms snapshot testing enabled
- Workspace shape: single package

## Command Used
```
jest --changedSince=main --ci
```

(TIA via `--changedSince` against the merge base)

## Suite Summary — First Pass

| Tests | Pass | Fail | Snap-stale | Duration |
|---|---|---|---|---|
| 312 | 309 | 3 | 3 | 24s |

## Per-Failure Analysis — First Pass

### `Button.snapshot` / `Button.disabled.snapshot` / `Button.loading.snapshot` — class: **test-bug (stale snapshot)**

Evidence:
- All 3 failures are pure snapshot diffs
- Diff in this PR is `Button.tsx`: added an explicit `aria-busy` attribute on the loading state
- The diff between expected and received snapshot is exactly the new `aria-busy="true"` line — no other deltas

Class confidence: HIGH — change is intentional (PR description explicitly mentions adding `aria-busy` for a11y); snapshots are out of date.

## Auto-Fix Decision

This is the canonical safe rebaseline scenario:
- Single attribute added
- Exact-match in snapshot diff
- Within 3-attempt cap (this is attempt 1)
- Owner intent confirmed by PR description

Auto-fix: ran `jest -u --testNamePattern='Button.*'` (scoped — NOT a blanket `-u` rebaseline of the whole suite, which would be unsafe).

## Suite Summary — Second Pass (post auto-fix)

| Tests | Pass | Fail | Snap-stale | Duration |
|---|---|---|---|---|
| 312 | 312 | 0 | 0 | 23s |

Coverage gate (jest config: line ≥ 90%, branch ≥ 85% on `Button.*`): **PASS** (94.1% / 89.0%).

## Class-Frequency Summary

| Class | Count |
|---|---|
| Test-bug (stale snapshot, auto-fixed) | 3 |
| Code-bug | 0 |
| Flaky | 0 |

## Audit Trail

- Attempt cap respected: 1 of 3 attempts used
- Scope: only `Button.*` snapshots regenerated (not blanket `-u`)
- Diff of `__snapshots__/Button.snap`: +3 lines (each adding `aria-busy="true"`); committed alongside the source change
