# /ralph — fix flaky integration tests

> Run-id: `ralph-bad-1`
> Oracle: `pytest -q tests/integration/`
> Kill-on: (not set)

## Iter 001

5 failures. Patched fixture timing.
Oracle: 5 failures.

## Iter 002

Tried `time.sleep(0.5)` in setup.
Oracle: 5 failures.

## Iter 003

Removed sleep, added retry decorator.
Oracle: 5 failures.

## Iter 004

Re-added sleep with longer duration.
Oracle: 5 failures.

## Iter 005

Reverted to retry decorator with more attempts.
Oracle: 5 failures.

## Done?

Stopped after 5 iterations. Tests still fail.

## Issues

- No kill-on rules set; loop ran to max-iter without runaway detection
- 5 iterations with literally zero progress (5 failures every time) — `no-progress=2` would have caught this at iter 003
- No telemetry written; no `tokens.json` per iter
- Oracle was a command but had no scope filter — kept running the full integration suite when the failing tests were a known subset
- No final report — termination reason absent, just "stopped"
