---
name: test-local
description: Local dev testing workflow — verify test environment, provision infrastructure (Docker, Testcontainers), run multi-level test suite (unit → integration → E2E), coverage analysis, quality gate. Applies QA Engineer role. Use when running a full local QA cycle before commit or PR.
context: fork
argument-hint: "service name or test scope"
---

# Test Local

Full QA cycle for local development environments. Verifies test infrastructure, provisions dependencies, runs tests at all levels (unit → integration → E2E), analyzes coverage, and applies quality gates. Orchestrated by `Agent(qa-engineer)`.

**Key difference from `/run-tests`**: This workflow manages the full local test environment lifecycle (setup → test → report → cleanup). `/run-tests` is a lightweight sub-workflow that only executes and analyzes tests.

Per-stack test runners and commands — see `@test-runners-by-stack`.

## 1. Define Scope

Read `TESTING.md` at the project root (and per-service `TESTING.md` in monorepos) for test infrastructure, commands, credentials, and organization. This is the authoritative source for how to test the project.

Ask the user (or extract from context):

- **Test scope**: Full suite / specific module / specific test level (unit / integration / E2E)
- **What changed**: New feature / bug fix / refactor / pre-commit check / full regression
- **Known issues**: Any tests expected to fail? Any infra known to be down?

If invoked by another workflow — extract scope from parent context.

## 2. Apply Roles

**Primary**: `Agent(qa-engineer)` — owns test strategy, quality gates, and test infrastructure decisions.

**Secondary** (applied as needed during test execution):

| Need | Role |
|---|---|
| Fix failing unit/integration tests | Stack-specific: `Agent(java-engineer)` / `Agent(python-engineer)` / `Agent(frontend-engineer)` |
| Docker/compose/infra issues | `Agent(devops-engineer)` |
| Test data / database schema | `Agent(db-engineer)` |
| General debugging | `Agent(software-engineer)` |

## 3. Detect Project Stack

Read `CLAUDE.md` and scan project files to determine the stack and matching runner. Detection signals, runners, and Testcontainers tools — see `@test-runners-by-stack`.

Also detect:

- **Docker Compose**: `docker-compose.yml`, `docker-compose.test.yml`, `compose.yaml`
- **Test config files**: `.env.test`, `jest.config.*`, `vitest.config.*`, `playwright.config.*`, `pytest.ini`, `conftest.py`
- **CI config**: `.github/workflows/`, `Jenkinsfile`, `.gitlab-ci.yml` — extract test commands used in CI for parity

## 4. Verify Local Environment

Before running tests, verify the local environment is ready.

**4a. Docker daemon** — run `docker version` (turbo). If not running, notify user and stop; container-backed tests will fail.

**4b. Port conflicts** — check ports needed by test services using `lsof -i :<port>` (macOS/Linux), `ss -tulnp | grep :<port>` (Linux), or `netstat -ano | findstr ":<port>"` (Windows). Common test ports: 5432 (PostgreSQL), 6379 (Redis), 27017 (MongoDB), 9092 (Kafka), 3306 (MySQL). Report which process holds any conflicting port and suggest resolution.

**4c. Environment variables** — verify root `.env` exists and contains `test_` prefixed variables (e.g., `test_user`, `test_db_host`); compare with `.env.example` and flag missing test variables. Read only `.env.example` for reference — never log or output actual `.env` values.

**4d. Dependencies** — verify installation using the per-stack check command (see `@test-runners-by-stack`). If stale, suggest the stack-appropriate install command (`npm install` / `pip install -r requirements.txt` / etc.).

## 5. Provision Test Infrastructure

Based on project config, set up test dependencies.

**5a. Testcontainers (preferred)** — no manual setup; containers start/stop per test suite. Verify Docker daemon (Step 4a), any `.testcontainers.properties` config, and that required images are available or pullable.

**5b. Docker Compose** — for `docker-compose.test.yml` or similar:

```
docker compose -f docker-compose.test.yml up -d
docker compose -f docker-compose.test.yml ps
```

Wait for healthy status. If any service is unhealthy — collect logs and diagnose using `Agent(devops-engineer)`.

**5c. Seed data** — locate seed scripts (check `CLAUDE.md`, `package.json` scripts, `Makefile`, `scripts/`), run them after infrastructure is ready, and verify success.

**5d. No infrastructure** — if the project uses only mocks/stubs for unit tests, skip to Step 6.

## 6. Run Tests

Execute tests in pyramid order: unit → integration → E2E. Stop at first failing level unless user requested full suite. Per-stack unit / integration / E2E / specialized commands — see `@test-runners-by-stack`.

**Test runner stdout > 2000 tokens normalized by `tool-output-normalize.py` hook (G2)** before injection — large multi-suite outputs become envelope metadata + top-k extracted failures rather than raw dumps.

**6a. Unit tests** — fast (< 2 min), high pass rate. If unit tests fail, fix before proceeding. Delegate to `/run-tests` for analysis and auto-fix (Step 3–4 of that workflow).

**6b. Integration tests** — run only if unit tests pass (or user explicitly requested). Moderate speed (< 10 min). Tests interact with real dependencies (DB, APIs via containers).

**6c. E2E tests** — run only if integration tests pass (or user explicitly requested). Prerequisites: application running locally (dev server or Docker), E2E config pointing at local URL, browser binaries installed (Playwright: `npx playwright install`).

**6d. Specialized tests (optional)** — performance, security, and accessibility — run only when user requests or project has them configured. Commands listed in `@test-runners-by-stack`.

## 7. Coverage Analysis

After all tests pass, run the per-stack coverage command (see `@test-runners-by-stack`) and compare against `test-strategy` skill targets:

| Metric | Target | Hard Minimum | Status |
|---|---|---|---|
| Line coverage | ≥ 80% | ≥ 60% | [pass/fail] |
| Branch coverage | ≥ 75% | ≥ 50% | [pass/fail] |
| New code coverage | ≥ 90% | ≥ 80% | [pass/fail] |

Flag modules with coverage below hard minimum.

## 8. Quality Gate

Evaluate overall test quality:

| Gate | Criteria | Result |
|---|---|---|
| **Unit tests** | All pass | ✅ / ❌ |
| **Integration tests** | All pass (if run) | ✅ / ❌ / ⏭️ skipped |
| **E2E tests** | All pass (if run) | ✅ / ❌ / ⏭️ skipped |
| **Coverage** | Meets targets | ✅ / ⚠️ below target / ❌ below minimum |
| **No flaky tests** | Zero retried tests | ✅ / ⚠️ |
| **No new warnings** | Lint + type checks clean | ✅ / ❌ |

**Decision**:

| Result | Action |
|---|---|
| All gates pass | ✅ **PASS** — safe to commit/PR |
| Coverage warning only | ⚠️ **PASS with notes** — consider adding tests |
| Any test failure | ❌ **FAIL** — fix before commit |
| Flaky tests detected | ⚠️ **PASS with action** — file flaky test issue |

## 9. Cleanup

After testing completes:

1. **Stop test containers** (if Docker Compose was used):
   ```
   docker compose -f docker-compose.test.yml down -v
   ```
2. **Remove test data** (if seed scripts ran outside containers)
3. **Report leftover containers** (if any test containers weren't cleaned up)

Testcontainers handles its own cleanup automatically — verify no orphaned containers remain.

## 10. Summary

```
## Local Test Summary

### Environment
- **Stack**: [detected stack]
- **Docker**: [version] | Test infra: [Testcontainers / Docker Compose / none]
- **Env issues**: [none / list]

### Test Results
| Level | Total | Passed | Failed | Skipped | Duration |
|-------|-------|--------|--------|---------|----------|
| Unit | X | X | X | X | Xs |
| Integration | X | X | X | X | Xs |
| E2E | X | X | X | X | Xs |

### Coverage
| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Line | X% | 80% | ✅/❌ |
| Branch | X% | 75% | ✅/❌ |
| New code | X% | 90% | ✅/❌ |

### Coverage Gaps
- [file/module] — [current%] — [uncovered areas]

### Quality Gate: ✅ PASS / ❌ FAIL
- [gate details]

### Failures Fixed (if any)
- [test] — [issue] — [fix]

### Remaining Issues
- [issue] — [action needed]

### Follow-up
- [recommendations]
```

## Integration

- **Roles**: `Agent(qa-engineer)` (primary), stack-specific roles (test fixes), `Agent(devops-engineer)` (infra issues)
- **Skills**: `test-strategy` skill (test patterns, coverage targets), `test-runners-by-stack` (per-stack commands)
- **Sub-workflows**: `/run-tests` (test execution and auto-fix for failures)
- **Called by**: `/develop` (pre-commit testing), `/bugfix` (verify fix)
- **Follow-up**: `/pre-commit` (quality gate), `/create-pr` (submit changes)
- **Hooks**: `tool-output-normalize.py` (G2 normalization for test runner stdout per Step 6)
