---
name: env-analyze
description: Multi-scope environment diagnostic — Kubernetes, CI runner, network, resource usage, and cross-scope drift snapshot for baselining across runs. Optional `--auto-fix` for container-level safe actions. Use when troubleshooting a deployment, debugging CI flakes, validating an environment before deployment, or when local diagnostics need to span more than just Docker. For Docker-only local triage use `/analyze-local`. Not for code bugs (use /bugfix) or application-level diagnostics (use /spike).
context: fork
argument-hint: "[--scope local|docker|kubernetes|ci] [--auto-fix]"
allowed-tools: Read, Grep, Glob, Bash
---

# /env-analyze — Environment Diagnostic

Read-only diagnostic that produces a structured `ENV-REPORT.md` for the current environment. Optional `--auto-fix` applies ONLY container-level safe actions; anything outside that scope requires manual escalation.

## When to use

- "Build is flaky on CI — check the runner"
- "Local Docker compose: services not starting"
- "Pre-deploy: validate K8s cluster state"
- "Debugging a deployment that's been failing intermittently"

## Not for

- Code bugs → `/bugfix`
- Application-level diagnostics (DB query plan, API behavior) → `/spike`
- Production incidents requiring SRE response → `/analyze-prod` (carried) + on-call

## Invocation

```
/env-analyze
/env-analyze --scope local
/env-analyze --scope docker --auto-fix
/env-analyze --scope ci
```

## Arguments

| Flag | Default | Effect |
|---|---|---|
| `--scope` | auto-detect | `local` (Docker/K8s detected), `docker`, `kubernetes`, `ci` |
| `--auto-fix` | off | Apply container-level safe fixes only — see scope below |

### `--auto-fix` scope (explicit boundary)

**In scope (safe):**
- Restart stuck containers
- Clear container-scoped caches
- Regenerate config from existing template

**Out of scope (manual escalation only):**
- Restarting Docker daemon
- Regenerating TLS certs
- Modifying host-level state
- Deleting data
- Changing secrets
- Kubernetes namespace operations
- Production value mutation

## Output

`<repo>/.ai-assets-memory/env-reports/<run-id>/ENV-REPORT.md` with tables:

- Container/pod status (name, state, restarts, uptime)
- Log excerpts (last 20 lines per service, error filter)
- Network sanity (connectivity, DNS, port availability)
- Resource saturation (CPU, memory, disk %)
- Identified anomalies (list with severity)
- Recommended actions (prioritized)

If `--auto-fix`: list of actions taken + per-action success/failure outcome.

## Agent roster

| Agent | Model | Effort | Tools | Role |
|---|---|---|---|---|
| `sre-engineer` | inherit | high | Bash, Read, Grep, Glob | Docker/K8s diagnostics, log analysis |
| `devops-engineer` | inherit | high | Bash, Read, Grep, Glob | CI/CD environment diagnostics |

## Pipeline

```
┌─ Scope detection: check for docker-compose.yml, k8s config, CI runner config
│
├─ SRE + DevOps in parallel (Wave 1):
│  ├─ sre-engineer:
│  │  - docker inspect, docker logs, docker stats (or kubectl get pods/nodes/logs)
│  │  → SRE-REPORT.md (containers, logs, resource usage)
│  │
│  └─ devops-engineer:
│     - CI runner health (GitHub Actions, GitLab CI, etc.)
│     → DEVOPS-REPORT.md (job queue, runner status, cache age)
│
├─ Lead consolidates → ENV-REPORT.md (merged view + anomaly list)
│
├─ If --auto-fix:
│  │  Per safe action: oracle = post-action health check
│  │  Out-of-scope items flagged as "manual: <reason>"
│  └─ Report action outcomes
│
└─ Memory write: L4 environment baseline snapshot for drift detection
```

No RALF — diagnostic is pass-once. Each `--auto-fix` action has its own per-action oracle (the post-action health check).

## Tool-output normalization

Bash output from `docker inspect`, `kubectl logs`, `docker stats` etc. is normalized by `tool-output-normalize.py` hook (G2) when > 2000 tokens — large log dumps become envelope metadata + extracted top-k errors rather than raw bytes.

## Eval rubric

Pointer: `plugin/eval/judge-rubrics/env-analyze.md` (B10).

Dimensions:
1. **Completeness** — all scopes checked (if applicable)
2. **Accuracy** — reports match actual state
3. **Clarity** — anomalies clearly flagged with severity
4. **Actionability** — recommendations are specific and executable
5. **Safety** — no destructive actions without explicit user approval

Pass: avg ≥ 4.0, no dimension < 3.

## Memory writes

| Layer | When | Shape |
|---|---|---|
| L4 | After analysis | `.ai-assets-memory/env-reports/<run-id>/baseline.json` — container states, resource usage, timestamps (for drift detection across runs) |

## Failure modes

- **Docker not installed:** graceful skip; report N/A for that scope
- **K8s connection refused:** report as connection error; offer manual debugging guidance
- **Auto-fix action fails:** rollback if possible; report outcome and manual steps
- **Log parsing error (corrupted logs):** skip that log; report as anomaly (log corruption suspected)

## Observability events

- `workflow_start` — env-analyze + scope
- `agent_spawned` × 2 (sre, devops)
- `auto_fix_action` — per action if `--auto-fix` enabled
- `workflow_end` — `COMPLETE` with anomaly count

## Integration

- **Spawns**: `sre-engineer`, `devops-engineer` (both with Bash + Read + Grep + Glob)
- **Schemas**: `plugin/schemas/spawn-payload.schema.json` (G7 spawn payloads)
- **Hooks**: `tool-output-normalize.py` (G2 on large bash output), `subagent-start-budget.py` (G7 validation + budget)
- **Used by**: `/bugfix` Step 2 (local-Docker diagnostic), `/team-bugfix` (optional pre-pipeline context-gathering), `/migrate` (pre-flight env check)
- **Carried alternative**: `/analyze-local` (existing skill, still works) — `/env-analyze` is the renamed B12 deliverable per Round 4 N2 with G7 + G2 pre-wired
