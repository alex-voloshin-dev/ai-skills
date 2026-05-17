# RALF: Read-Act-Learn-Feedback

How ai-skills workflows iterate on a task until a mechanically-verifiable success signal.

> Internal spec lives in `plugin-design/01-WORKFLOW-SPECS.md` (`/ralph` section) and `plugin-design/00-PHASE-1-PLAN.md` §3.5. This doc is the user-facing summary.

## What RALF is

RALF is a controlled iteration loop. The model attempts a task, an **oracle** checks whether the attempt succeeded, and if it didn't, the model iterates with a **continuation prompt** (state delta only — not the full original brief).

It's the answer to "why does my agent silently fail after 5 attempts and burn 200K tokens?" — RALF caps iterations, tokens, and wall-time, and requires a binary success signal up front.

## When workflows use RALF

RALF is **opt-in per workflow**. The plugin ships these defaults:

| Workflow | Oracle | Kill-on | Caps |
|---|---|---|---|
| `/feature-design` | judge:feature-design.md (min 4.0) | regex:RUBRIC_FAILED_3X | 5 iter / 250K / 60min |
| `/develop` | cli:./run-tests.sh | oracle-pass | 8 iter / 640K / 90min |
| `/bugfix` (reproduction) | cli:./run-tests.sh (regression FAIL→PASS) | oracle-pass | 6 iter / 300K / 60min |
| `/refactor` | cli:./run-tests.sh | same-error-repeats:2 | 4 iter / 200K / 45min |
| `/migrate` (validation) | python:./validate-migration.py | oracle-pass OR no-progress:2 | 5 iter / 300K / 90min |
| `/infra-change` (optional) | terraform plan -detailed-exitcode | oracle-pass | 4 iter / 200K / 45min |

Standalone usage:

```bash
/ralph "<task>" --oracle <type:value> --kill-on <type:value>
```

## The four oracle types

| Type | Format | Pass condition |
|---|---|---|
| `cli` | `cli:./script.sh` | Script exits 0 |
| `judge` | `judge:rubric-name.md` | `eval-judge` agent score ≥ rubric threshold |
| `regex` | `regex:./out.log:^DONE$` | Pattern matches in named file |
| `python` | `python:./check.py` | Script exits 0 |

The oracle is mandatory — `/ralph` rejects invocation if missing per `ralph-budget.md`. The whole point of RALF is "we know objectively when to stop."

## The five kill-on signals

| Type | Format | Trigger |
|---|---|---|
| `oracle-pass` | (no value) | Happy stop on first oracle success |
| `same-error-repeats` | `same-error-repeats:N` | Same error string N iterations in a row → likely the approach is wrong |
| `regex` | `regex:PATTERN` | Pattern matches in latest model output |
| `python` | `python:./kill.py` | Custom predicate exits 2 |
| `no-progress` | `no-progress:N` | N iterations with no file diff |

Without a kill-on signal the loop will only stop at iteration cap, token cap, or wall-time cap. That's wasteful — pick the kill-on that names the failure mode you actually want to catch.

## Init vs continuation prompts (G10)

This is the key cost optimization.

- **Iter 1 (init prompt)**: full task brief — goal, constraints, evidence, output contract, oracle definition, kill-on signal. Typically 5–15K tokens depending on workflow.
- **Iter ≥ 2 (continuation prompt)**: state delta only — last-iteration diff, oracle failure summary, top-3 active constraints, kill-on countdown. Typically 1–3K tokens.

Continuation prompts reduce per-iteration cost by ~70%. The template lives at `plugin/skills/ralph/templates/continuation-prompt.md` and is applied automatically by the `ralph-stop.py` hook.

## Two-level budget caps

Per Round 6 HIGH-3, the plugin enforces two levels of caps:

### Per-workflow caps (D12 defaults)

Apply to a single RALF run within one workflow. Defaults shown above; overridable in `userConfig`:
- `ralph_default_max_iter` (10)
- `ralph_default_token_budget` (200_000)
- `ralph_default_time_cap_minutes` (120)

### Session-aggregate caps

Apply across ALL workflows in one session. Prevents runaway when chaining `/feature-design` → `/develop` etc. Defaults:
- `ralph_session_max_iter` (20)
- `ralph_session_token_budget` (400_000)
- `ralph_session_time_cap_minutes` (180)

The `ralph-stop.py` hook reads cumulative RALF token spend from the session token meter (`L3 token-meter.json`) before allowing iteration ≥ 2 of any workflow. Hard kill on aggregate exceedance, regardless of per-workflow budget remaining.

### Per-iteration measurement (v0.1.6)

A companion PostToolUse hook (`ralph-iter-meter.py`) estimates tokens per tool call (`chars(tool_input + tool_response) // 4`) and accumulates into the session meter while a RALF run is active. `ralph-stop.py` consumes the per-iteration accumulator on each Stop intercept and:

1. Persists per-iter spend to `iter-NNN/tokens.json` with the fair-share calculation.
2. Resets the accumulator so the next iteration starts at zero.
3. Fires a **runaway warning** when a single iteration exceeds 3× the fair share (`workflow_token_budget / max_iterations`), durably logging to `.ai-skills-memory/ralph-warnings.log`.

The chars/4 estimate is a guardrail, not a billing meter — Tier 3 eval runs populate exact API counts directly via `ralf_workflow_tokens_last`. Before v0.1.6, interactive RALF (`/ralph` directly) had no per-iteration token signal: only iteration-count and wall-time caps could fire. Now the session-aggregate token cap is also effective interactively.

## State and logs

Every RALF run writes to `<repo>/.ai-skills-memory/ralph/<run-id>/`:

- `config.json` — caps + oracle + kill-on as locked at start
- `active.lock` — presence = run is in progress
- `initial-prompt.md` — full init prompt
- `iter-NNN/` — one dir per iteration: `prompt.md`, `output.md`, `diff.patch`, `oracle-result.json`, `tokens.json` (v0.1.6)
- `budget.json` — final totals on exit

You can resume by reading `iter-NNN/` history. You can debug by inspecting `oracle-result.json` per iteration.

## Failure modes

- **Missing `--oracle` or `--kill-on`** → rejected at arg validation
- **Oracle script crashes** (exit ≠ 0 AND ≠ 2) → treated as `ORACLE_ERROR`, loop killed, diagnostic surfaced
- **Hard cap hit** → soft warn at threshold, hard pause at cap, user prompted to confirm continuation, raise budget, or abort
- **`ralph-stop.py` hook crashes** → fails open per `failure-recovery.md`; never blocks Stop

## Standalone vs embedded

- **Standalone:** `/ralph` for power users running their own iteration loop
- **Embedded:** workflows like `/feature-design` and `/develop` invoke RALF segments internally per their spec

Both share the same hook (`ralph-stop.py`), the same caps, and the same continuation template.

## When NOT to use RALF

- Open-ended exploration without a binary success signal → use `/spike` instead
- Code where you'd rather review the plan first → use `/plan` then `/develop`
- Anything where "good enough" is a judgment call → use a workflow with a judge rubric, but think hard before wiring up RALF on a subjective oracle (you'll burn tokens chasing a moving target)

## Related workflows

- [`/ralph`](../workflows/feature-design.md) — standalone RALF entry
- [`/feature-design`](../workflows/feature-design.md) — RALF on the design rubric
- [`/develop`](../workflows/develop.md) — RALF on test failures
- [`/bugfix`](../workflows/bugfix.md) — RALF on the regression test
- [`/migrate`](../workflows/migrate.md) — RALF on data integrity validation
