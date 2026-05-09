# Test Strategy — Internal API

## Stack
Java 21, Spring Boot.

## Pyramid

Standard pyramid: many unit, fewer integration, very few E2E.

## Coverage

Line coverage 80%. Branch coverage 70%. Run JaCoCo in CI.

## Tools

JUnit 5, Mockito, Spring Boot Test.

## Speed

Tests should run in a reasonable time.

## Approach

Write unit tests for each method. Write integration tests for each endpoint. Run them in CI on every PR.

## Done When

Coverage thresholds met and CI is green.

---

(no mention of mutation testing, property-based testing, contract testing, or Testcontainers; no critical-path identification; no speed budget per tier; no ratchet policy)
