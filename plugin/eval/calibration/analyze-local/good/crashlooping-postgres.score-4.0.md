# Local Diagnostic — `postgres` container crashlooping

> Scope: local Docker compose | Read-only

## Summary

`postgres-1` is in a crash loop (38 restarts in last 10m). Root cause: container OOM-killed by Docker memory limit (`mem_limit: 256m` in compose.yml) — Postgres `shared_buffers` default of 128m + per-connection overhead exceeds limit at our connection count.

## Container State

```
$ docker compose ps
NAME           STATUS                       PORTS
api-1          Up 12 minutes (healthy)      0.0.0.0:8080->8080/tcp
postgres-1     Restarting (137) 8s ago      5432/tcp
worker-1       Up 12 minutes (healthy)
```

State JSON (`docker inspect postgres-1 --format='{{json .State.Health}}{{json .State.OOMKilled}}{{json .RestartCount}}'`):
```json
null
true
38
```

`OOMKilled: true` + restart count 38 + exit 137 → container hit memory limit.

## Logs Evidence

`docker logs postgres-1 --tail=15`:
```
PostgreSQL Database directory appears to contain a database; Skipping initialization
2026-04-25 14:22:01.443 UTC [1] LOG:  starting PostgreSQL 16.2
2026-04-25 14:22:01.448 UTC [1] LOG:  listening on IPv4 address "0.0.0.0", port 5432
2026-04-25 14:22:01.451 UTC [1] LOG:  database system is ready to accept connections
[exits — no crash log; OOMKilled is silent from Postgres' perspective]
```

No application-level error. Pattern matches `<common_issues>` entry "container exit 137 + OOMKilled true = memory limit too low".

## USE Method (resource axes)

| Axis | Postgres | Threshold | Verdict |
|---|---|---|---|
| Utilization | mem 100% (256/256MB at peak) | > 90% sustained = bad | FAIL |
| Saturation | OOMKilled events: 38 in 10m | > 0 = saturation | FAIL |
| Errors | exit code 137 × 38 | > 0 = errors | FAIL |

`docker stats postgres-1 --no-stream` (between restarts, near peak):
```
CONTAINER     CPU%    MEM USAGE / LIMIT      MEM%    NET I/O          BLOCK I/O
postgres-1    18%     254.1MiB / 256MiB      99.3%   1.2MB / 0.8MB    12MB / 4MB
```

## Anomalies

| Anomaly | Severity | Evidence |
|---|---|---|
| `postgres-1` OOMKilled in tight loop | HIGH | `OOMKilled: true`, exit 137, 38 restarts/10m |
| `mem_limit: 256m` undersized for 16.2 default `shared_buffers` | HIGH | Default `shared_buffers=128MB` + 100 conn × ~2MB = > 256MB |

## Root Cause

Postgres 16.2 default `shared_buffers=128MB` plus the connection pool (configured `max_connections=100` in compose's `command:`) exceeds the `mem_limit: 256m` set in `docker-compose.yml:line 18`. Container hits cgroup memory ceiling and is OOM-killed; Postgres restarts; pattern repeats.

## Remediation (manual — read-only diagnostic)

1. **Raise the limit** in `docker-compose.yml`:
   ```yaml
   postgres:
     mem_limit: 1g  # was 256m
   ```
   Side effect: host memory consumption rises by ~750MB. Reversibility: high (revert + recreate).
2. **Recreate the container:**
   ```
   docker compose up -d --force-recreate postgres
   ```
3. **Verify:**
   ```
   docker compose ps postgres   # expect Up + (healthy) within 30s
   docker inspect postgres-1 --format='{{.State.OOMKilled}}'   # expect false
   ```

## Out of Scope

- This is a local-only diagnostic. If the same pattern is suspected in K8s / staging / prod, escalate to `/env-analyze` (K8s scope) or `/analyze-prod`. Handoff payload would include: namespace, pod name, observed restart count, the `mem_limit` mismatch hypothesis.
