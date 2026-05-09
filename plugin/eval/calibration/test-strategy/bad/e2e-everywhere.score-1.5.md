# Test Strategy — Calculator Library

## Stack
TypeScript library with pure math functions: `add`, `subtract`, `multiply`, `divide`, `tax`, `discount`, `roundCurrency`.

## Shape

Inverted pyramid — E2E first.

| Tier | Ratio |
|---|---|
| E2E (Playwright spinning up a sample SPA that imports the library) | 80% |
| Integration | 15% |
| Unit | 5% |

We will write Playwright specs that visit a demo page, type numbers into form fields, click "calculate", and assert the result on screen. This is the most realistic.

## Why

End-to-end tests catch the most bugs because they test the whole stack. Unit tests are usually too narrow and miss real issues.

## Coverage

Aim for 100% coverage everywhere. We will measure coverage by counting Playwright specs that touch each function.

## Speed

Tests will take a long time but that's the price of high confidence.

## Tools

Playwright + Chrome only.
