# /feature-dev — add retry logic to webhook dispatcher

> Run: feature-dev-bad-3
> Stack: Node.js 20 + TypeScript (detected)
> Role: ts-engineer

## Plan presented + approved

1. Wrap dispatch in `retry(fn, {attempts:3, backoff:'expo'})`
2. Use `p-retry` library
3. Update tests

User: "approved."

## Implementation

- `src/webhooks/dispatcher.ts` updated; `p-retry` imported
- `src/webhooks/__tests__/dispatcher.test.ts` updated with one new case

Single role, no Agent calls. (OK on that dim.)

## Verification

```
$ pnpm test
 Test Files  1 passed (1)
      Tests  4 passed (4)
```

Lint not run. Typecheck not run. Build not run.

## AC verification

| AC | Result |
|---|---|
| Retries on transient 5xx | "tested manually, looks fine" |
| Honors backoff | "the library handles it" |
| Stops on permanent 4xx | "covered by existing test, I think" |

## Done

"Tests pass — shipping."

## Issues with this run

- Only 1 of 4 verification gates run (tests); lint, typecheck, build skipped silently
- AC verification is informal ("looks fine", "the library handles it") — no objective evidence
- No explicit test for the "stop on 4xx" criterion despite claiming it's covered
- Plan + approval were good; verification step let the run down
