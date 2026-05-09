# Local Diagnostic — `api` cannot bind port 5432

> Scope: local Docker compose | Read-only

## Summary

`api-1` healthy but cannot connect to `postgres`. Root cause: port 5432 on the host is held by a process outside Docker (a system-installed `postgresql.service`); the compose `postgres` service silently never started because its `ports: 5432:5432` mapping fails. Pattern: `<common_issues>` "port already allocated".

## Container State

```
$ docker compose ps
NAME       STATUS                    PORTS
api-1      Up 4 minutes (healthy)    0.0.0.0:8080->8080/tcp
worker-1   Up 4 minutes (healthy)
```

`postgres` is not in the listing. `docker compose up postgres` output (re-run for evidence):
```
Error response from daemon: driver failed programming external connectivity on
endpoint compose-postgres-1: Bind for 0.0.0.0:5432 failed: port is already allocated
```

## Port Holder

```
$ sudo lsof -i :5432
COMMAND    PID   USER   FD   TYPE DEVICE SIZE/OFF NODE NAME
postgres  1842 postgres   5u  IPv4  41882      0t0  TCP *:postgresql (LISTEN)
```

PID 1842 is the host's `postgresql.service` (`systemctl status postgresql` confirms). It's outside Docker.

## USE Method (resource axes)

| Axis | api-1 | postgres-1 |
|---|---|---|
| Utilization | nominal (8% CPU, 120/512MB) | N/A — never started |
| Saturation | 0 | N/A |
| Errors | connection-refused to `postgres:5432` (47 in last 4m) | bind failure on start |

`docker logs api-1 --tail=8 --since=2m`:
```
2026-04-25 14:30:11 [error] db.connect: dial tcp postgres:5432: connect: connection refused
[same line repeats]
```

## Healthcheck Awareness

`api-1` healthcheck passes (HTTP /health doesn't touch DB). `postgres-1` has no health state because it never started. Restart count for `postgres-1` is 0 (unstarted not crashlooping).

## Anomalies

| Anomaly | Severity | Evidence |
|---|---|---|
| Port 5432 held by host `postgresql.service` | HIGH | `lsof -i :5432` PID 1842 outside Docker |
| `postgres-1` never started | HIGH | `docker compose ps` does not list it |
| `api-1` retrying connections | MEDIUM | log spam; harmless but noisy |

## Root Cause

Host has `postgresql.service` listening on 5432. Docker Compose cannot bind the host-side of the published port. Compose treats this as a fatal start error, so the container is removed, not retried.

## Remediation (manual)

1. **Pick one of two paths:**
   - **Path A — stop the host service** (preferred for dev machines that don't otherwise use Postgres):
     ```
     sudo systemctl stop postgresql
     sudo systemctl disable postgresql   # optional, prevents reboot recurrence
     ```
   - **Path B — remap the compose port** (preferred if the host service is needed):
     ```yaml
     postgres:
       ports:
         - "55432:5432"   # was 5432:5432
     ```
     And update the `DATABASE_URL` env var to point at host `:55432` instead of `:5432`. Reversibility: full.
2. **Restart the stack:**
   ```
   docker compose up -d postgres
   ```
3. **Verify:**
   ```
   docker compose ps postgres                     # Up
   docker compose logs api --tail=5 --since=1m    # no connection-refused
   ```

## Out of Scope

- Production K8s services typically don't have this class of issue (services run in pods); if the same symptom appeared in K8s, escalate to `/env-analyze`.
