# Code Review — PR #4421: Add `RetryPolicy` to outbound HTTP client

## Verdict: REQUEST_CHANGES (1 blocking, 2 non-blocking nits, 1 praise)

Reviewer-coverage: logic + retry semantics. Not covered: load behaviour under sustained 5xx — recommend a follow-up perf check after merge.

## Findings

### `http/RetryPolicy.java:42` — issue (blocking)

`shouldRetry()` retries on `IOException` AND `4xx` responses. `4xx` is a client error and should not be retried — retrying a `400 Bad Request` will never succeed and burns the caller's quota.

Suggested change: split classification into `RETRYABLE` (5xx, IOException, timeout) and `TERMINAL` (4xx, 401, 403). The current code conflates these.

This is blocking because production callers will see avoidable amplification of bad-request load.

### `http/RetryPolicy.java:71` — nit (non-blocking)

`Math.min(backoffMs * 2, MAX_BACKOFF)` — consider exponential backoff WITH jitter. Without jitter, a fleet retrying in lockstep can self-DDoS the origin on recovery. Not blocking — current behaviour is no worse than before — but a 5-minute change.

### `http/RetryPolicyTest.java:128` — nit (non-blocking)

The `assertEquals(3, attempts)` magic number reads better as a named constant `EXPECTED_MAX_ATTEMPTS`. Strictly cosmetic; defer if you'd rather.

### `http/RetryPolicy.java:18` — praise

praise: extracting `RetryDecision` as a value object with `delay()` and `reason()` makes the policy testable in isolation — a real improvement over the previous in-line int-return. This is a pattern worth using elsewhere in the package.

## Summary

1 blocking issue (retry classification), 2 nits, 1 praise. Code-health-over-perfection: blocking item is a correctness concern; nits should NOT delay merge once the blocker is addressed.

Defer to siblings: dependency-CVE check on the new `okhttp` upgrade — please run `/security-scan` if not already in the pipeline.
