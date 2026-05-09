# /ralph — improve API documentation tone

> Run-id: `ralph-bad-2`
> Oracle: `"docs read clearly and use friendly tone"`
> Kill-on: `max-iter=5`

## Iter 001

Rewrote intro section. "Sounds friendlier now."
Oracle: subjective check — model decided "yes, friendly enough."

## Iter 002

Adjusted code-example comments. "Clearer."
Oracle: "yes."

## Iter 003

"All good." Stopped.

## Issues

- Oracle is subjective — "reads clearly" and "friendly tone" cannot be mechanically verified. The whole point of `/ralph` is a binary oracle (test passes / schema validates / regex match)
- Self-judging the oracle defeats the feedback loop — there is no external signal pulling the model toward a target
- Kill-on covers max-iter only; no `no-progress`, `token-spike`, or `repeat-error`
- For prose / tone work, `/ralph` is the wrong tool — should use `/humanizer` or a quality rubric with judge eval, not RALF
- No telemetry, no convergence transparency
