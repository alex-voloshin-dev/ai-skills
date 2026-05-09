# Local Test Sweep — `inventory-api` (developer machine)

## Stack Scope

| Tier | Tool | Status |
|---|---|---|
| Unit | go test | PASS (218/218) |
| Integration | go test (with Testcontainers Postgres) | PASS (34/34) |
| E2E | not in scope (no UI in this service) — explicitly skipped |
| Load | hey — 100 RPS for 30s | PASS |
| a11y | not applicable (API service) — explicitly skipped |

## Infrastructure

`docker compose up -d --wait` with healthchecks on Postgres and Redis. Service waits for `condition: service_healthy` before tests run.

Testcontainers used for the integration tier — `testcontainers-go` with a Postgres 16 container per test package, reused across tests within the package.

## Cross-Platform Port Check

Detected developer environment: macOS 14.7 on Apple Silicon. The pre-flight port check verifies that ports 5432, 6379, and 8080 are free before `docker compose up`.

Helper used:

```bash
case "$(uname -s)" in
  Darwin) listeners="$(lsof -nP -iTCP:5432 -sTCP:LISTEN)";;
  Linux)  listeners="$(ss -tlnp 'sport = :5432')";;
  MINGW*|MSYS*|CYGWIN*) listeners="$(powershell.exe -NoProfile -Command \
            'Get-NetTCPConnection -LocalPort 5432 -State Listen' 2>NUL)";;
  *) echo "Unknown OS — cannot check ports"; exit 1;;
esac
```

On the macOS run, used `lsof`. The same helper has been verified on Windows 11 + WSL2 and on the GitHub Actions Linux runner — works on all three.

If a port is occupied, the helper prints the offending PID + process and aborts before running `docker compose up`. No silent failure.

## Cleanup

`trap 'docker compose down -v --remove-orphans' EXIT` ensures the compose stack is torn down whether the run succeeds or aborts. Testcontainers Go containers stop via deferred `Terminate(ctx)` — also runs on panic.

Idempotent re-run check: `docker ps -a -q --filter label=com.docker.compose.project=inventory-api | xargs -r docker rm -f` before each fresh run.

## Quality Gate

| Check | Threshold | Actual | Status |
|---|---|---|---|
| Unit pass rate | 100% | 100% | PASS |
| Integration pass rate | 100% | 100% | PASS |
| Line coverage | ≥ 85% | 88.4% | PASS |
| Branch coverage | ≥ 80% | 82.1% | PASS |
| go vet | clean | clean | PASS |
| staticcheck | clean | clean | PASS |
| Load p99 | < 200ms | 142ms | PASS |

**Overall verdict: PASS — proceed to commit.**
