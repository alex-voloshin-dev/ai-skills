# /feature-dev — debounce search input on settings page

> Run: feature-dev-2026-05-01-debounce
> Stack: TypeScript + React 18 + Vite (detected from `package.json`)
> Role applied: ts-engineer

## Acceptance criteria (from request)

1. Search input fires API call only after 300ms idle
2. Aborts in-flight request when user keeps typing
3. Loading spinner appears within 50ms of API call start
4. Empty input returns to default list without API call
5. Existing keyboard navigation tests still pass

## Plan presented + approved

1. Replace `useEffect(fetch, [query])` with `useDebouncedSearch(query, 300)` hook
2. Hook uses `AbortController`; cancels previous on re-trigger
3. Loading state lifted to `useState`; spinner rendered via existing `<Spinner>`
4. Skip-empty guard inside hook: `if (!q.trim()) return early`
5. Tests: hook unit test (vitest fake timers) + component test (RTL) + keep existing nav test
6. Verification: `pnpm test && pnpm lint && pnpm typecheck && pnpm build`

User reply: "approved."

## Implementation

- `src/hooks/useDebouncedSearch.ts` (new, 42 LOC)
- `src/pages/SettingsSearch.tsx` (refactor, -18 / +9)
- `src/hooks/__tests__/useDebouncedSearch.test.ts` (new, 6 cases)
- `src/pages/__tests__/SettingsSearch.test.tsx` (updated)

Inline. No `Agent(...)`. ts-engineer role throughout.

## Verification

```
$ pnpm test
 Test Files  3 passed (3)
      Tests  18 passed (18)
   Duration  3.42s

$ pnpm lint   # eslint
0 errors, 0 warnings

$ pnpm typecheck   # tsc --noEmit
(success, 0 errors)

$ pnpm build
✓ built in 4.81s
```

## AC verification (traceability table)

| AC | Verification | Test name / evidence | Result |
|---|---|---|---|
| 1. 300ms debounce | vitest fake timer asserts no fetch < 300ms | `debounces with 300ms idle` | pass |
| 2. Abort in-flight | mock fetch records 2 abort calls on rapid typing | `aborts previous request` | pass |
| 3. Spinner < 50ms | RTL `findByRole('status', {timeout: 50})` | `shows spinner during fetch` | pass |
| 4. Empty returns to default | mock fetch call count = 0 on empty input | `skips fetch on empty input` | pass |
| 5. Keyboard nav unchanged | existing `keyboard navigation` test re-run | green | pass |

## Boundary

Single-component scope; one role; user opted in to inline path. Justified.

## Done

Coverage: SettingsSearch 91% (was 76%). PR opened.
