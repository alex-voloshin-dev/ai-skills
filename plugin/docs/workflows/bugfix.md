# /bugfix — Investigate, diagnose, and fix a bug end-to-end

From bug report to deployed fix with regression test, with optional environment diagnostic and RALF on the reproduction test.

## When to use

- A user-reported bug needs investigation and a fix
- A failing test in production or staging needs root-cause analysis
- An intermittent failure where you need RALF to converge on a stable repro

## Not for

- Adding features → use [`/develop`](develop.md)
- Refactoring without behaviour change → use [`/refactor`](refactor.md)
- Just diagnosing an environment (no code change needed) → use [`/env-analyze`](env-analyze.md)

## How to invoke

```bash
/bugfix "<bug description>"
/bugfix "Login form returns 500 when email contains apostrophe"
/bugfix "Webhook timeouts spiking on prod since deploy yesterday"
```

## What you get

- A structured bug report (you confirm before any code change)
- A fix plan (you approve before implementation)
- The fix itself
- A regression test that fails without the fix and passes with it
- Verification that all tests pass + linter clean
- A summary report

## How it works

1. **Receive bug report** — gather expected vs actual, environment, severity
2. **Analyze environment** — delegates to [`/env-analyze`](env-analyze.md) (local Docker) or `/analyze-prod` (production K8s)
3. **Detect stack and apply role** — `python-engineer` for Python, `frontend-engineer` for React, etc.
4. **Collect evidence** — stack trace, logs, recent commits, minimal repro
5. **Prepare bug report** — you confirm
6. **Plan the fix** — root-cause + changes + regression test + risk assessment; you approve
7. **(Optional) RALF on reproduction test** — for intermittent or hard-to-converge bugs
8. **Implement the fix** — minimal, complete, no scope creep
9. **Self-review** — diff check, lint clean, no TODO/FIXME introduced
10. **Verify** — regression test passes, full suite passes
11. **Summary** — what was fixed, root cause, prevention recommendations

## RALF on reproduction (optional)

For bugs where the failure mode is intermittent or environment-dependent, the workflow enables RALF on the regression test. Defaults: 6 iter / 300K tokens / 60 min. Kill-on: `oracle-pass` (regression test transitions FAIL → PASS).

Use cases:
- Test passes locally but fails in CI (environment drift)
- Race condition reproduction
- Memory leak repro that needs a load profile

## Severity model

| Severity | Description | Triage approach |
|---|---|---|
| **P1** | Outage, data loss, security breach | Skip detailed intake, immediate analyze-prod + fix |
| **P2** | Degraded service, partial outage | Standard intake but expedited |
| **P3** | Minor issue affecting some users | Standard pipeline |
| **P4** | Cosmetic, no functional impact | Standard pipeline (or batch with similar) |

## Common questions

**What if I don't know the root cause yet?**
That's fine — Step 4 collects evidence, Step 5 produces a hypothesis. The fix plan in Step 6 is your gate to confirm before any code change.

**Can the workflow fix tests instead of code?**
Yes, if Step 5 classifies the failure as "test bug — test is wrong or outdated" rather than "code bug." But it asks you to confirm the classification.

**What if the fix turns out larger than expected?**
The workflow stops and surfaces the deviation. You can approve a wider scope, narrow it, or pivot to `/refactor` or `/develop`.

**Is RALF always on?**
No — only when the bug profile suggests intermittency. You'll see "Step 7 RALF Loop" mentioned in the plan if it's enabled. You can override with `--no-ralph` flag if you want one-shot.

**What gets memory-written?**
- Run log to L4 `runs.jsonl`
- Bug summary + root cause to L4 (per `memory-discipline.md`)
- For P1/P2: optionally write a learning entry via `/learnings-write` to capture the class-of-bug for the team

## Examples

### Local Docker bug
```bash
/bugfix "Order endpoint returns 500 on empty cart from deep link"
```
Step 2 invokes `/env-analyze` — finds the Docker compose state is fine. Step 3 applies `python-engineer`. Steps 4–11 walk through to a regression test + fix.

### Production bug needing prod diagnostics
```bash
/bugfix "Webhook timeouts on prod since 14:00 UTC"
```
Step 2 invokes `/analyze-prod` — finds K8s pod is OOMKilled at peak load. Bug report shows it's an infra issue + an application memory leak. Fix plan addresses both: HPA tuning by `devops-engineer` + memory leak fix by `python-engineer`.

### Intermittent test failure (RALF enabled)
```bash
/bugfix "Test test_concurrent_order_creation flakes 30% of the time in CI"
```
Step 7 RALF runs the regression test up to 6 times to converge on a stable repro. The fix likely involves a race condition (locking, idempotency, or test isolation). RALF state captured in `.ai-skills-memory/ralph/<run-id>/` for forensics.

## Related

- [`/env-analyze`](env-analyze.md) — local Docker diagnostic (Step 2 sub-workflow)
- [`/develop`](develop.md) — sibling pipeline for new features
- [`/run-tests`](feature-design.md) — sub-workflow called for test execution
- [`/create-pr`](feature-design.md) — submits the fix as a PR
- [Memory](../concepts/memory.md) — bug summaries persist to L4
- [RALF](../concepts/ralf.md) — Step 7 reproduction loop
