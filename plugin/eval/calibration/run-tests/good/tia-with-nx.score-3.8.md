# Run Tests — `web-monorepo` (Nx workspace, PR branch)

## Stack Detection
- Detected: Nx 19 / pnpm / Vitest + Playwright
- `nx.json` confirms 14 projects (10 libs, 3 apps, 1 e2e)
- Workspace shape: monorepo with TIA-capable runner

## TIA Strategy
Branch diverged from `main` at commit `a3f9c10`. Used `nx affected` to scope:

```
nx affected:test --base=main --head=HEAD --parallel=4
nx affected:e2e  --base=main --head=HEAD
```

Affected: 3 libs (`pricing`, `cart`, `ui-kit`) + 1 app (`web-shop`) + 1 e2e (`web-shop-e2e`). Saved ~71% of suite (10 of 14 projects untouched by diff — skipped). Falls back to full `nx run-many --target=test --all` on `main` and release branches.

## Suite Summary

| Project | Tests | Pass | Fail | Duration |
|---|---|---|---|---|
| pricing (lib, vitest) | 84 | 84 | 0 | 12s |
| cart (lib, vitest) | 56 | 55 | 1 | 9s |
| ui-kit (lib, vitest) | 178 | 178 | 0 | 21s |
| web-shop (app, vitest) | 92 | 92 | 0 | 33s |
| web-shop-e2e (Playwright) | 18 | 18 | 0 | 4m 02s |

Coverage gate (vitest config: line ≥ 80%, branch ≥ 75%): **PASS** on all changed projects.

## Per-Failure Analysis

### `cart > applyPromoCode handles expired code` — class: **code-bug**

Evidence:
- Assertion: expected `{ applied: false, reason: 'EXPIRED' }`, got `{ applied: false, reason: 'INVALID' }`
- Diff in this PR touches `src/promo.ts` (the change introduced a unified `INVALID` reason for all rejection paths — collapses what the test expects to be distinct)

Class confidence: HIGH — code change broke the contract the test encodes.

### Suggested Next Action

Restore the `EXPIRED` discriminator in the rejection-reason union, OR update the test if the unified reason is intentional. Did NOT auto-fix — this is a contract decision (semantic), not a safe rebaseline.

## Class-Frequency Summary

| Class | Count |
|---|---|
| Code-bug | 1 |
| Test-bug | 0 |
| Flaky | 0 |
| Contract-drift | 0 |
| Environment | 0 |

## TIA Saving Reported

10 of 14 projects untouched → ~71% of suite skipped. Wall-clock saving on this run: 5m 17s (vs estimated 13m on full run-many).
