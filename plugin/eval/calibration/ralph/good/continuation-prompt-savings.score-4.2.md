# /ralph — refactor convergence with G10 continuation prompts

> Run-id: `ralph-2026-05-05-extract-validator`
> Oracle: `pytest -q tests/contract/ && ruff check src/ && mypy src/` exits 0
> Kill-on: `no-progress=2,token-spike=2x,repeat-error=3`
> Caps: `ralph_session_max_iter=12`, `ralph_session_max_tokens=250000`

## Strategy

- Iter 001: full init prompt (repo context, target file list, oracle definition)
- Iter ≥ 2: G10 continuation prompt template — sends only `{failed_check, last_patch, oracle_stderr_tail, delta_files}`. Full repo context cached + reused.

## Iter 001 (init, 24811 input tokens)

Target: extract `validate_payload` into `src/validators/payload.py`. 6 callers updated.
Oracle: pytest 2 fail, ruff 0, mypy 1.

## Iter 002 (G10 continuation, 4102 input)

Fixed type-narrowing in caller `routes/orders.py`.
Oracle: pytest 1 fail, mypy 0.

## Iter 003 (G10 continuation, 3918 input)

Fixed test fixture import path.
Oracle: 0 — converged.

## Token analysis

| Metric | Iter 1 | Iter 2 | Iter 3 |
|---|---:|---:|---:|
| Input tokens | 24811 | 4102 | 3918 |
| Cache-read tokens | 0 | 19444 | 19612 |
| Output tokens | 2614 | 1108 | 891 |
| Total billable | 27425 | 5210 | 4809 |

Continuation savings (vs replaying init context every iter): **(54822 - 10019) / 54822 ≈ 81.7%** for iters 2–3.

## Termination

- Reason: oracle satisfied (pytest + ruff + mypy all 0)
- Iterations: 3 / 12
- Total: input=32831, output=4613, cache-read=39056
- Cap utilization: 25% iter, 13% tokens

## Per-iter telemetry

`.ai-skills-memory/ralph/ralph-2026-05-05-extract-validator/iter-{001..003}/tokens.json` + `summary.json`. Schema versioned (`v1`).

## Final report

Oracle: PASS. Iter: 3. Tokens: 32831 in / 4613 out. Termination: converged. Cost projection per iter shown to user before iter 002 (user confirmed: "continue").
