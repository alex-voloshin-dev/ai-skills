# Test Writing Guide

Practical patterns and examples for writing effective tests across common tech stacks. Reference this guide when writing unit, integration, or E2E tests.

## Universal Patterns

### Arrange-Act-Assert (AAA)

Every test follows this structure:

```
// Arrange — set up preconditions and inputs
// Act — execute the behavior under test
// Assert — verify the expected outcome
```

### Naming Convention

Use descriptive names that document behavior:

```
// Pattern: should_[expected_behavior]_when_[condition]

should_return_empty_list_when_no_items_exist
should_throw_validation_error_when_email_is_invalid
should_send_notification_when_order_is_completed
should_deny_access_when_token_is_expired
```

### Test Data

- Use factories/builders for complex objects — avoid raw constructors in tests
- Use meaningful values (not `"test"`, `"abc"`, `123`) — they serve as documentation
- Isolate test data — each test creates its own state
- Clean up after integration tests (transactions, temp files, test containers)

## Unit Test Patterns

### Pure Function Tests

```
// Test all paths: happy path, edge cases, error cases
// Input → Output — no side effects to verify

test_calculate_discount_for_premium_user
test_calculate_discount_returns_zero_for_guest
test_calculate_discount_caps_at_maximum
test_calculate_discount_throws_for_negative_price
```

### Mocking Strategy

- **Mock external dependencies** (APIs, databases, file system, time)
- **Do NOT mock the unit under test**
- **Do NOT mock value objects** (DTOs, entities without behavior)
- **Prefer stubs over mocks** — verify state, not interactions
- **One mock per test** — if you need many mocks, the unit has too many dependencies

### Error Handling Tests

Always test:
- Expected exceptions are thrown with correct type and message
- Error recovery paths work correctly
- Retry logic respects limits
- Timeout behavior is correct

## Integration Test Patterns

### Database Tests

- Use transactions that roll back after each test (or test containers)
- Test actual queries — do not mock the database in integration tests
- Verify constraints (unique, foreign key, not null)
- Test migrations forward and backward

### API Tests

- Test request validation (missing fields, wrong types, boundary values)
- Test response format (status code, content type, body structure)
- Test authentication and authorization for each endpoint
- Test error responses (404, 400, 401, 403, 500)
- Test pagination, filtering, sorting if applicable

### Service Integration Tests

- Test with real dependencies (or test containers) — not mocks
- Test timeout and circuit breaker behavior
- Test retry logic with transient failures
- Test data consistency across service boundaries

## E2E Test Patterns

### When to Write E2E Tests

- Critical user journeys (sign up, login, checkout, core workflow)
- Smoke tests for deployments (health check, basic navigation)
- Regression tests for high-impact bugs

### E2E Best Practices

- Use page object model or similar abstraction
- Wait for elements explicitly — never use `sleep()`
- Test on realistic data (seeded, not production)
- Keep E2E suite small and focused (< 50 tests ideally)
- Run E2E in CI on every PR (or at minimum on main branch)

## Anti-Patterns to Avoid

| Anti-Pattern | Problem | Fix |
|---|---|---|
| Testing implementation details | Breaks on refactor | Test behavior/outcomes |
| Shared mutable state between tests | Flaky, order-dependent | Isolate test data |
| Overly broad assertions | False positives | Assert specific values |
| Copy-paste test setup | Maintenance burden | Extract fixtures/factories |
| Testing framework code | Wasted effort | Trust well-tested libraries |
| `sleep()` in tests | Slow, flaky | Use explicit waits/polling |
| No assertion in test | False confidence | Every test must assert |
| Catching and ignoring exceptions | Hides failures | Let tests fail loudly |

## Stack-Specific Notes

### JavaScript/TypeScript (Vitest, Jest, Playwright)

- Use `describe` blocks to group related tests
- Prefer `toBe` for primitives, `toEqual` for objects
- Use `beforeEach` for common setup, not `beforeAll` (isolation)
- Playwright: use `page.waitForSelector()` over fixed timeouts

### Java (JUnit 5, Mockito, Testcontainers)

- Use `@Nested` classes for test organization
- Use `@ParameterizedTest` for data-driven tests
- Testcontainers for database/Redis/Kafka integration tests
- `assertThrows` for exception verification

### Python (pytest, unittest.mock)

- Use `pytest.fixture` with appropriate scope
- `@pytest.mark.parametrize` for data-driven tests
- `pytest-asyncio` for async test support
- `conftest.py` for shared fixtures (scoped by directory)

### Go (testing, testify)

- Table-driven tests for multiple scenarios
- `t.Helper()` in test utilities
- `t.Parallel()` where safe for speed
- Subtests with `t.Run("scenario", func(t *testing.T) {...})`
