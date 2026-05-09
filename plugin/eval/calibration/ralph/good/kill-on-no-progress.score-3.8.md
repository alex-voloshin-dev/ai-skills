# /ralph — schema-validation loop, killed on no-progress (correctly)

> Run-id: `ralph-2026-05-04-jsonschema`
> Oracle: `ajv validate -s schema.json -d output.json` exits 0
> Kill-on: `no-progress=2,token-spike=2x,repeat-error=3`
> Caps: `ralph_session_max_iter=8`, `ralph_session_max_tokens=150000`

## Iter 001 (init)

Schema fails on missing `correlation_id`. Patched generator to emit it.
Oracle: 1 (still failing — pattern mismatch). Tokens: in=22014, out=1801.

## Iter 002 (G10 continuation)

Fixed pattern. Now fails on date-time format.
Oracle: 1 (still failing — different rule). Tokens: in=3920, out=1402, cache=18012.

## Iter 003 (G10 continuation)

Switched to ISO-8601 helper. Fails again — same date-time rule.
Oracle: 1. Tokens: in=3811, out=1198, cache=18190.

## Iter 004 (G10 continuation)

Tried timezone-aware variant. Fails again — same date-time rule.
Oracle: 1. Tokens: in=3754, out=1132, cache=18310.

## Kill-on triggered

`repeat-error=3`: same `format/date-time` rule failing 3 iterations in a row → loop terminated.

## Termination

- Reason: kill-on `repeat-error` (3 consecutive identical failures on `format/date-time`)
- Iterations: 4 of 8
- Total tokens: in=33499, out=5533, cache-read=54512
- Caps: respected
- Recommended human action: inspect ajv format definitions; the input may need `"format": "date-time"` mode set explicitly. Surfaced in summary.json.

## Telemetry written

`.ai-assets-memory/ralph/ralph-2026-05-04-jsonschema/iter-{001..004}/tokens.json` + `summary.json` with `terminated:"kill-on:repeat-error"`.

## Note

This run is a "good" example because the kill-on rule fired correctly — the model would have spun forever on a problem it couldn't see (ajv format-mode mismatch). Surfacing the loop to the human is the right outcome.
