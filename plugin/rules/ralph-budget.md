---
description: RALF iteration loop budget enforcement — per-workflow caps (10 iter / 200K tokens / 2h defaults), session-aggregate caps (20 iter / 400K tokens / 3h), mandatory --kill-on signal, fail-open on hook errors. Activates whenever /ralph or any RALF-using workflow (/feature-design, /develop, /bugfix, /refactor, /migrate) is about to start an iteration loop.
---

# RALF Budget Enforcement

Caps and discipline for the Read-Act-Learn-Feedback iteration loop. Pairs with `01-WORKFLOW-SPECS.md` /ralph spec and `00-PHASE-1-PLAN.md` §3.5 RALF integration.

## Two-Level Budget Model

### Per-Workflow Defaults (D12)

Apply to a single RALF run within one workflow.

| Cap | Default | userConfig override | Notes |
|---|---|---|---|
| Max iterations | 10 | `ralph_default_max_iter` | First iteration is "init"; subsequent are "continuation" per G10 |
| Token budget | 200_000 | `ralph_default_token_budget` | Counts cumulative tokens across all iter (executor + judge + comparator) |
| Wall-time | 120 min | `ralph_default_time_cap_minutes` | First iter to terminal state |

Per-workflow override in workflow spec body (typically tighter):
- `/feature-design`: 5 iter / 250K tokens / 60 min (rubric converges fast)
- `/develop`: 8 iter / 640K tokens / 90 min (test loop)
- `/bugfix`: 6 iter / 300K tokens / 60 min (reproduction loop)
- `/refactor`: 4 iter / 200K tokens / 45 min
- `/migrate`: 5 iter / 300K tokens / 90 min

### Session-Aggregate Caps (Round 6 HIGH-3)

Apply across ALL workflows in one session. Prevents runaway when chaining `/feature-design` → `/develop` etc.

| Cap | Default | userConfig override |
|---|---|---|
| Aggregate iterations | 20 | `ralph_session_max_iter` |
| Aggregate tokens | 400_000 | `ralph_session_token_budget` |
| Aggregate wall-time | 180 min | `ralph_session_time_cap_minutes` |

`ralph-stop.py` reads cumulative RALF token spend from session token meter (`L3 token-meter.json`) before allowing iteration ≥ 2 of any workflow. Hard kill on aggregate exceedance, regardless of per-workflow budget remaining.

### Per-iteration measurement (Phase 4 #3, v0.1.6)

`ralph-iter-meter.py` PostToolUse hook estimates tokens per tool call (`chars(tool_input + tool_response) // 4`) and accumulates into `ralf_iter_tokens_partial` while a RALF run is active. `ralph-stop.py` consumes the accumulator on each Stop intercept, resets it to 0, and persists per-iteration spend to `.ai-assets-memory/ralph/<run-id>/iter-NNN/tokens.json`.

A **runaway warning** fires when a single iteration exceeds **3× the per-iteration fair share** (`workflow_token_budget / max_iterations`). The warning is recorded in `tokens.json` as `runaway: true` and durably appended to `.ai-assets-memory/ralph-warnings.log`. This catches "one bad iteration burning the whole workflow budget" before the hard cap fires.

Estimate accuracy: chars/4 is Anthropic's published English-text average; non-English / code-heavy iterations may under- or over-estimate by ~20-30%. The cap is a guardrail, not a billing meter — exact API token counts come from Tier 3 eval runs that populate `ralf_workflow_tokens_last` directly.

## Mandatory `--kill-on` Signal

Per D12: every RALF run MUST have an explicit `--kill-on` signal. `/ralph` skill validates args and rejects with clear error if `--kill-on` is missing. Per-workflow integrated RALF (`/feature-design` etc.) declares its own kill-on in skill body.

Valid `--kill-on TYPE:VALUE`:
- `oracle-pass` — happy stop on first oracle success
- `same-error-repeats:N` — same error string N iterations in a row
- `regex:PATTERN` — regex matches in latest model output
- `python:./kill.py` — custom kill predicate (exit 0 = continue, 2 = kill)
- `no-progress:N` — N iterations with no file diff

## Oracle Types

`--oracle TYPE:VALUE`:
- `cli:./test.sh` — shell command, exit 0 = pass
- `judge:rubric-name.md` — invokes `eval-judge` agent against named rubric, threshold from rubric file
- `regex:./out.log:^DONE$` — pattern match in named file
- `python:./check.py` — custom predicate

## State and Logs

Every RALF run writes to `<repo>/.ai-assets-memory/ralph/<run-id>/`:
- `config.json` — caps + oracle + kill-on as locked at start
- `active.lock` — presence = run is in progress (read by `ralph-stop.py` to detect active loop)
- `initial-prompt.md` — full init prompt (G10)
- `iter-NNN/` — one dir per iteration with prompt.md, output.md, diff.patch, oracle-result.json, tokens.json (per Phase 4 #3)
- `ralph-warnings.log` — durable record of runaway warnings (single-iter token spend > 3× fair share)
- `budget.json` — final totals on exit (iterations completed, tokens spent, wall-time, exit reason)

Per G10, iter ≥ 2 uses `continuation-prompt.md` (state delta only, ~70% token savings vs full init).

## Failure Modes (per `00-PHASE-1-PLAN.md` §3.8)

- `ralph-stop.py` script crash → fail open (log to `hook-errors.log`, allow Stop, write incomplete `budget.json`). Never block all tool use because of buggy hook.
- Oracle exit ambiguous (≠0 AND ≠2) → treat as unknown state, kill loop, write `ORACLE_ERROR` status, surface diagnostic to user
- Token budget hit during iteration → soft warn at threshold; hard pause at cap; user prompted to confirm continuation, raise budget, or abort
- Cowork host memory conflict (L0 vs L4) → trust most-recently-confirmed layer; flag conflict to user

## Anti-Patterns

- Invoking `/ralph` without `--kill-on` (rejected by skill arg validator)
- Running RALF without writing `budget.json` on exit (forensic loss)
- Per-workflow caps bypass session-aggregate caps (always check both)
- Continuation prompt that re-includes full init context (defeats G10 token savings)

## Pairing

- `subagent-isolation.md` — RALF iterations may spawn subagents; both per-workflow + session-aggregate budgets enforced
- `memory-discipline.md` — `ralph-stop.py` writes to L4 ralph/ dir per L4 schema
- `untrusted-content-wrapping.md` — last-iter diff/error injected into continuation prompt MUST be wrapped per G1 (it came from tool output)
