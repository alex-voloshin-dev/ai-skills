# /env-analyze — Diagnose your local Docker / K8s / CI environment

Read-only environment diagnostic with optional safe auto-fix for container-level issues.

## When to use

- "My Docker compose isn't starting cleanly"
- "Build is flaky on CI — what's the runner state?"
- "Pre-deploy: validate K8s cluster"
- "Debugging a deployment that's failing intermittently"

## Not for

- Code bugs → use [`/bugfix`](bugfix.md) (which calls `/env-analyze` as a sub-workflow when needed)
- Application-level diagnostics (DB query plan, API behavior) → use [`/spike`](spike.md)
- Production incidents requiring SRE response → use `/analyze-prod` + on-call

## How to invoke

```bash
/env-analyze
/env-analyze --scope local
/env-analyze --scope docker --auto-fix
/env-analyze --scope ci
```

| Flag | Default | Effect |
|---|---|---|
| `--scope` | auto-detect | `local` (Docker/K8s detected), `docker`, `kubernetes`, `ci` |
| `--auto-fix` | off | Apply container-level safe fixes only |

## What you get

`<repo>/.ai-assets-memory/env-reports/<run-id>/ENV-REPORT.md` with:

- Container/pod status (name, state, restarts, uptime)
- Log excerpts (last 20 lines per service, error filter)
- Network sanity (connectivity, DNS, port availability)
- Resource saturation (CPU, memory, disk %)
- Identified anomalies (with severity)
- Recommended actions (prioritized; `--auto-fix` outcomes if enabled)

## `--auto-fix` scope (explicit boundary)

**In scope (safe):**
- Restart stuck container
- Clear container-scoped cache
- Regenerate config from existing template

**Out of scope (manual escalation only):**
- Restart Docker daemon
- Regenerate TLS certs
- Modify host-level state
- Delete data
- Change secrets
- K8s namespace operations
- Production value mutation

If the workflow detects a needed action outside this scope, it flags as `manual: <reason>` rather than performing it. This is by design — diagnostic skill should not destroy.

## How it works

`sre-engineer` and `devops-engineer` agents work in parallel:

- **sre-engineer** — `docker inspect`, `docker logs`, `docker stats` (or `kubectl get pods/nodes/logs` for K8s)
- **devops-engineer** — CI runner health, job queue, runner status, cache age

The Lead consolidates both reports into a unified `ENV-REPORT.md`.

No RALF — diagnostic is pass-once. If `--auto-fix` is enabled, each action has its own per-action oracle (post-action health check).

## Common questions

**Is `--auto-fix` safe to run on production?**
The actions inside scope are designed to be safe (restart container, clear cache, regen config from existing template). But: this skill is intended for **local** environments by default. Use `/analyze-prod` for production diagnostics; do not point `/env-analyze --auto-fix` at production K8s without understanding the side effects.

**What if Docker isn't installed?**
Graceful skip; report N/A for that scope.

**What if K8s connection is refused?**
Report as connection error; offer manual debugging guidance.

**Why didn't the workflow restart the Docker daemon?**
Out-of-scope per design. Daemon restart is a host-level change with broad blast radius — manual escalation only.

**How does this differ from `/analyze-local`?**
`/analyze-local` is a carried (legacy) skill that still works. `/env-analyze` is the B12 redesign with G2 normalization on bash output, G7 spawn payloads, and the explicit `--auto-fix` scope boundary. Either skill works; `/env-analyze` is preferred for new flows.

## Examples

### Quick check before starting work
```bash
/env-analyze
```
Auto-detects scope. Produces a report. Useful as a 30-second sanity check.

### Diagnose + safely fix a stuck container
```bash
/env-analyze --scope docker --auto-fix
```
If a container is in restart-loop because of a port conflict, the workflow will identify the conflicting process AND attempt a safe restart (without killing the conflicting host process — that's manual).

### CI pipeline investigation
```bash
/env-analyze --scope ci
```
`devops-engineer` checks runner state, job queue, recent failures, cache age. Produces actionable report.

## Related

- [`/bugfix`](bugfix.md) — calls `/env-analyze` as a sub-workflow when needed
- [`/team-bugfix`](feature-design.md) — pre-pipeline context-gathering
- `/analyze-local` (carried) — legacy alternative
- `/analyze-prod` (carried) — production K8s diagnostic
- [Memory](../concepts/memory.md) — environment baselines persist to L4 for drift detection
