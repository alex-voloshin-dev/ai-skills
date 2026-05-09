# Local Diagnostic — `frontend` image pull failing

> Scope: local Docker compose | Read-only

## Summary

`frontend-1` cannot start; image pull from Docker Hub fails with HTTP 429. Root cause: anonymous Docker Hub pull rate limit (100 pulls / 6h / IP) exhausted by CI shared egress IP. Workaround: authenticate `docker login` for a 200/6h limit, or mirror the image. Pattern matches `<common_issues>` "Docker Hub rate limit on first pull".

## Container State

```
$ docker compose ps
NAME           STATUS
api-1          Up 6 minutes (healthy)
postgres-1     Up 6 minutes (healthy)
frontend-1     Created
```

`frontend-1` stuck in `Created` state — never transitioned to `Running`.

## Pull Evidence

```
$ docker compose up frontend
[+] Running 1/1
 ! frontend Warning: pull access denied, repository does not exist or may require 'docker login'
Error response from daemon: toomanyrequests: You have reached your pull rate limit. You may
increase the limit by authenticating and upgrading: https://www.docker.com/increase-rate-limits
```

```
$ docker compose pull frontend 2>&1 | tail -3
node:20-alpine: Pulling from library/node
toomanyrequests: You have reached your pull rate limit.
```

## Rate-Limit Confirmation

```
$ TOKEN=$(curl -s "https://auth.docker.io/token?service=registry.docker.io&scope=repository:library/node:pull" | jq -r .token)
$ curl -sI -H "Authorization: Bearer $TOKEN" "https://registry-1.docker.io/v2/library/node/manifests/20-alpine" | grep -i ratelimit
ratelimit-limit: 100;w=21600
ratelimit-remaining: 0;w=21600
```

`ratelimit-remaining: 0` confirms the anonymous pull limit is exhausted on this egress IP.

## USE Method

| Axis | frontend-1 | Verdict |
|---|---|---|
| Utilization | container never created → no CPU / memory | N/A |
| Saturation | image-pull queue blocked (0/1 attempts succeeded in last 10m) | FAIL |
| Errors | HTTP 429 from registry | FAIL |

## Healthcheck Awareness

No health state to check — container was never created, so `OOMKilled`, restart count, and exit code are all moot. Confirmed via `docker inspect frontend-1 --format='{{.State.Status}}'` → `created`.

## Anomalies

| Anomaly | Severity | Evidence |
|---|---|---|
| Docker Hub anonymous pull limit exhausted | HIGH | Registry 429 + `ratelimit-remaining: 0` |
| `frontend` service never reached running state | HIGH | `Status: created`, no `Running` transition |
| Other services unaffected (already pulled) | INFO | `api`, `postgres` images cached locally |

## Root Cause

Shared NAT/VPN egress IP has consumed the 100 anonymous pull quota. Until quota resets in the rolling 6h window, anonymous pulls of any Docker Hub image from this IP will return 429.

## Remediation (manual)

1. **Path A — authenticate (preferred, works immediately):**
   ```
   docker login
   docker compose pull frontend
   docker compose up -d frontend
   ```
   Authenticated quota is 200/6h; usually unblocks immediately. Reversibility: full.
2. **Path B — mirror through internal registry** (preferred for CI):
   - Pull once via `docker login`, retag, push to internal registry
   - Update compose `image:` to `internal-registry.local/node:20-alpine`
   - Side effect: requires registry maintenance.
3. **Path C — wait** for the rolling 6h window to free the quota (passive; useful only if dev cycles allow).

## Verify post-fix

```
docker compose ps frontend                # Up
docker compose logs frontend --tail=5     # serving on port 3000
docker scout quickview node:20-alpine     # confirms locally cached image, no 429
```

## Out of Scope

- Provisioning an internal mirror registry → that's an `/architecture` initiative if it's not already a platform asset.
- CI runner egress IP rotation → ops/devops question, not a local-Docker scope.
