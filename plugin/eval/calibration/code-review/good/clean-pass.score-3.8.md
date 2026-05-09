# Code Review — PR #4502: Replace bespoke email regex with `validator-js`

## Verdict: APPROVE (substantive review; 0 blocking, 1 suggestion, 2 praise)

Reviewer-coverage: input validation surface + behaviour parity with previous regex. Not covered: i18n IDN domains under load (out-of-scope for this PR).

## Findings

### `validators/email.ts:14` — praise

praise: dropping the 80-line custom regex in favour of a maintained library is the right move. The regex had three known false-rejects logged in `EMAIL-FALSE-REJECT.md`; this PR closes all three.

### `validators/email.ts:22` — praise

praise (testing): the parity test (`email.parity.test.ts`) re-runs the entire historical pass/fail corpus against the new validator. Excellent way to lock in equivalence.

### `validators/email.ts:30` — suggestion (non-blocking)

suggestion: consider re-exporting `EmailValidationError` from the package barrel (`src/index.ts`). Callers who catch this error today import it from a deep path — and a follow-up PR can change the import location. Non-blocking; cosmetic to the API surface.

## Summary

Behaviour-preserving migration. Diff is small, tests are strong, the change is reversible. APPROVE on technical facts: parity test passes, library is maintained, three pre-existing bugs go away.

Code-health-over-perfection: the suggestion is a nice-to-have and may be deferred to a follow-up.

Defer to siblings: none — diff is contained.
