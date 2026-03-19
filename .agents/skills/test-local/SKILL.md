---
name: test-local
description: Execute a full local QA cycle by validating local test prerequisites, running layered tests, diagnosing failures, and reporting readiness.
---

# Test Local

## Workflow

1. Read `TESTING.md`, `AGENTS.md`, and local service setup docs.
2. Verify required services or containers are available.
3. Run unit tests, then integration tests, then E2E or smoke checks as applicable.
4. Diagnose failing tests with logs and context.
5. Summarize local readiness and remaining blockers.
