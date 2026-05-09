# Test Local Rubric

## Overview

Evaluates `/test-local` output — full local QA sweep across unit / integration / E2E / load / a11y, including ephemeral infra (Docker, Testcontainers). Six dimensions × five levels. Distinct from `/run-tests` (single-suite execution) and `/test-strategy` (design).

## Dimensions

### Dimension 1: Stack Scope
Covered unit + integration + E2E + load + a11y as the project warrants.

- **Level 1:** Unit only on a multi-tier stack
- **Level 2:** Two tiers covered; gaps unacknowledged
- **Level 3:** Tiers present; some shallow
- **Level 4:** All applicable tiers covered; non-applicable explicitly skipped with reason
- **Level 5:** All of L4 + per-tier duration + pass/fail status in summary

### Dimension 2: Testcontainers Usage
Used Testcontainers for integration where applicable (real DB / queue / cache) — not mocks for things you can spin up.

- **Level 1:** Mocks where Testcontainers is the right tool
- **Level 2:** Mix of real + mock without rationale
- **Level 3:** Testcontainers for primary stores; mocks acknowledged
- **Level 4:** Testcontainers for stores + queues + caches; lifecycle scoped per-suite
- **Level 5:** All of L4 + reuse strategy for fast feedback (singleton container per JVM / pytest-xdist coordination)

### Dimension 3: Health-Check Awareness
Waited for `condition: service_healthy` / readiness probes before running tests.

- **Level 1:** Sleeps then runs; race conditions inevitable
- **Level 2:** Polls a port; no health check
- **Level 3:** Uses healthcheck condition
- **Level 4:** Healthcheck + per-service timeout + log-on-fail
- **Level 5:** All of L4 + dependency graph respected (DB ready before app, app ready before tests)

### Dimension 4: Cross-Platform Commands
Cross-platform port-check / process-check (lsof on macOS/Linux, netstat / Get-NetTCPConnection on Windows) instead of OS-specific ones.

- **Level 1:** Windows-only command on macOS (or vice versa) with silent failure
- **Level 2:** OS-specific without detection
- **Level 3:** Detects OS; branches command
- **Level 4:** OS-aware helper functions; Windows-PowerShell aware
- **Level 5:** All of L4 + uses Python / Node helpers where shelling out is fragile

### Dimension 5: Cleanup Discipline
Tore down ephemeral infra on completion (containers / volumes / networks / temp dirs).

- **Level 1:** Leaves dangling containers and volumes
- **Level 2:** Cleans containers; leaves volumes / networks
- **Level 3:** All ephemeral resources torn down on success
- **Level 4:** Cleanup runs on success AND failure (try/finally or trap)
- **Level 5:** All of L4 + idempotent cleanup re-runnable for stragglers from prior aborts

### Dimension 6: Coverage + Quality Gate
Quality gate output with clear PASS / FAIL / SKIP per check before declaring "ready to commit".

- **Level 1:** "Looks good" with no gate output
- **Level 2:** Some checks reported; gate verdict missing
- **Level 3:** Gate verdict present per check
- **Level 4:** Gate table (check / status / threshold / actual) + overall verdict
- **Level 5:** All of L4 + gate result wired to commit advice (proceed / fix-first / hold)

## Scoring Logic

- **Aggregate:** average of D1–D6
- **Pass threshold:** 4.0
- **Judge model:** Sonnet (multi-tier judgement benefits from broader stack reasoning)

## Anti-Patterns (Auto-Fail)

- Mocked-out integration where a real container is feasible (defeats integration testing)
- Leaves dangling Docker containers / volumes after run
- OS-specific port-check on the wrong OS with silent failure
- "All green" verdict without gate table
- Sleep-instead-of-healthcheck for service readiness

## Calibration Reference

- **Known-good:** `plugin/eval/calibration/test-local/good/*`
- **Known-bad:** `plugin/eval/calibration/test-local/bad/*`
