# Environment Diagnostic — local Docker compose

> Scope: local | Auto-fix: disabled

## Summary

5 services running, 1 unhealthy (`redis`). Root cause identified: port-conflict from a leftover `redis-stack` container from a prior project. 1 anomaly fixable manually.

## Container Status

| Service | State | Restarts | Uptime | Health |
|---|---|---|---|---|
| api | running | 0 | 2h 14m | healthy |
| worker | running | 0 | 2h 14m | healthy |
| postgres | running | 0 | 2h 14m | healthy |
| redis | restarting | 47 | 2m 03s | unhealthy |
| minio | running | 0 | 2h 14m | healthy |

## Logs (last 10 lines per error-filtered service)

### redis (`docker logs redis-1 --tail=20 --since=5m`)
```
1:M 22 Apr 2026 18:23:01.443 # Could not create server TCP listening socket *:6379: bind: Address already in use
1:M 22 Apr 2026 18:23:01.443 # Failed to listen on port 6379
[same line repeating ~47 times]
```

### Other services: no errors in last 5m.

## Resource Saturation

- CPU: 12% across all containers
- Memory: 1.4GB / 8GB (ample headroom)
- Disk: 23% used on shared volume

## Network Sanity

- DNS: `docker exec api ping postgres` → resolves + 0.4ms RTT
- Port availability: `5432`, `9000`, `9001` available; **`6379` HELD by external process**

## Identified Anomalies

| Anomaly | Severity | Evidence |
|---|---|---|
| `redis` cannot bind 6379 | HIGH | Restart loop + log `Address already in use` |
| Port 6379 held by non-compose process | HIGH | `lsof -i :6379` shows `redis-server (PID 4218)` outside compose |

## Root Cause

Standalone `redis-server` process (PID 4218) from a prior `docker run` (likely a leftover from `redis-stack` testing yesterday) is holding port 6379. The compose `redis` service can't bind. This is a port-conflict, not a redis-image problem.

## Recommended Actions (manual — `--auto-fix` not enabled)

1. **Stop the conflicting process:**
   ```
   docker stop $(docker ps -q --filter "name=redis-stack") || true
   docker rm $(docker ps -aq --filter "name=redis-stack") || true
   ```
   Reversibility: high — restartable from image.
2. **Restart the compose redis service:**
   ```
   docker compose restart redis
   ```
3. **Verify health** post-restart:
   ```
   docker compose ps redis  # should show "healthy" within 30s
   ```

## Memory Write

Baseline snapshot saved to `.ai-skills-memory/env-reports/<run-id>/baseline.json` for drift detection on next run.

## Out-of-Scope (would require manual action)

- None this run. Suggested actions are container-level safe.
