---
name: run-tests
description: Run tests workflow — execute test suite, analyze failures, auto-fix obvious issues, re-run. Sub-workflow for /develop, /bugfix, /pre-commit. Uses the `test-strategy` skill. Use when verifying code by running tests, analyzing failures, or coverage gaps.
---

<!-- ARCHITECTURAL NOTE: intentional model-invocable companion — deliberately no `context: fork` and no `disable-model-invocation`. Reusable sub-workflow composed into the caller's main thread by `/develop`, `/bugfix`, and `/pre-commit`; forking it would break that composition and disabling model-invocation would stop auto-load on test-verification tasks. Not a defect — do not reclassify. -->

# Run Tests

Execute the project's test suite, analyze failures, attempt fixes, and re-run. Designed as a reusable sub-workflow called by `/develop`, `/bugfix`, and `/pre-commit`.

Uses `test-strategy` skill for test writing patterns and coverage targets.

## 1. Detect Test Stack

Read `TESTING.md` (if exists) for test commands, infrastructure, and credentials. Fall back to `CLAUDE.md` and project config to determine:

| Signal | Stack | Runner |
|---|---|---|
| `package.json` + vitest/jest | TypeScript/JS | `npx vitest run` / `npx jest` |
| `pom.xml` / `build.gradle` | Java | `mvn test -q` / `gradle test` |
| `pyproject.toml` / `pytest.ini` | Python | `pytest -x -q` |
| `go.mod` | Go | `go test ./...` |
| `*.csproj` | .NET | `dotnet test` |

## 2. Run Tests

Execute the test suite:

```
// turbo
<test-command>
```

Capture:
- **Exit code**: 0 = all pass, non-zero = failures
- **Output**: Test names, pass/fail counts, error messages, stack traces

**Test runner stdout > 2000 tokens is normalized** by the `tool-output-normalize.py` hook (G2) before injection back into context — large failure dumps get summarized envelope metadata + extracted top-k failures rather than raw dump. This protects context budget on noisy suites.

## 3. Analyze Failures

If tests fail, for each failure:

1. **Read the failing test** — understand what it asserts
2. **Read the error message and stack trace** — identify the actual vs expected
3. **Classify the failure**:

| Classification | Action |
|---|---|
| **Code bug** — test is correct, implementation is wrong | Fix the implementation (Step 4) |
| **Test bug** — test is wrong or outdated | Fix the test (Step 4) |
| **Environment issue** — missing dependency, port conflict, DB down | Report to user (Step 5) |
| **Flaky test** — passes on re-run without changes | Flag for investigation |

## 4. Fix and Re-Run

For auto-fixable failures:

1. Apply the appropriate stack-specific role (`Agent(frontend-engineer)`, `Agent(java-engineer)`, `Agent(python-engineer)`, etc.)
2. Apply the minimal fix — do not refactor unrelated code
3. Re-run the failing test(s) specifically:

| Stack | Run Single Test |
|---|---|
| Vitest | `npx vitest run <test-file>` |
| Jest | `npx jest <test-file>` |
| pytest | `pytest <test-file>::<test-name> -v` |
| JUnit/Maven | `mvn test -pl <module> -Dtest=<TestClass>#<method>` |
| Go | `go test -run <TestName> ./path/...` |

4. If the fix works, re-run the full suite to check for regressions
5. **Max 3 fix attempts per failure** — if still failing after 3 tries, escalate to user

## 5. Coverage Check (if available)

Run coverage report:

| Stack | Command |
|---|---|
| Vitest | `npx vitest run --coverage` |
| Jest | `npx jest --coverage` |
| pytest | `pytest --cov=<package> --cov-report=term-missing` |
| Go | `go test -coverprofile=coverage.out ./... && go tool cover -func=coverage.out` |
| JUnit | `mvn jacoco:report` |

Compare against `test-strategy` skill targets:
- Line coverage ≥ 80% (hard minimum 60%)
- Branch coverage ≥ 75% (hard minimum 50%)
- New code coverage ≥ 90%

## 6. Summary

```
## Test Results

| Metric | Value |
|--------|-------|
| Total tests | X |
| Passed | X |
| Failed | X |
| Skipped | X |
| Duration | Xs |
| Coverage | X% (target: 80%) |

### Failures Fixed
- [test name] — [what was wrong] — [fix applied]

### Remaining Failures (needs attention)
- [test name] — [error] — [classification]

### Coverage Gaps
- [file/module] — [current%] — [uncovered lines]

**Overall**: ✅ PASS / ❌ FAIL — [action needed]
```

## Integration

- **Called by**: `/develop`, `/bugfix`, `/pre-commit`
- **Skills**: `test-strategy` skill
- **Roles**: `Agent(qa-engineer)` (test strategy), stack-specific role (implementation)
- **Hooks**: `tool-output-normalize.py` (G2 normalization for test runner stdout per Step 2)
