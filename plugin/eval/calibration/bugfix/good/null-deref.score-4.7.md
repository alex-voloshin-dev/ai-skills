# Bug Report + Fix — `OrderService.calculateTotal` NPE on empty cart

## Severity: P2

## Environment
Production (read replica showed exception in error logs starting 2026-04-08 14:32 UTC)

## Bug
`OrderService.calculateTotal(Order)` throws NullPointerException when `order.lineItems` is null (not when empty — when null specifically). Symptom: 500 errors on `POST /api/orders/preview` for users with empty carts visiting checkout from a deep link.

## Root Cause
`Order.lineItems` is initialized only in the constructor that takes a list. The deep-link checkout flow uses `Order(userId)` constructor which leaves `lineItems` null. `calculateTotal` calls `lineItems.stream()` without null-check.

5-whys:
1. Why NPE? `lineItems.stream()` on null
2. Why null? `Order(userId)` doesn't init `lineItems`
3. Why doesn't it init? Two constructors, divergent — the 1-arg version was added in PR #3104 without parity
4. Why no test? `Order(userId)` was added for a different code path; integration test missing for the deep-link flow
5. Why missed in review? PR #3104 changelog said "convenience constructor"; reviewer assumed parity

Class of bug: divergent constructors. Risk of similar in `Cart`, `Invoice` — checked, both safe.

## Fix
- `Order.java`: initialize `lineItems = new ArrayList<>()` in field declaration (defensive default)
- Removed redundant init from existing list-arg constructor
- `calculateTotal`: removed planned null-check (no longer needed; field is now non-null)

## Regression Test
`OrderServiceTest.calculateTotal_emptyOrderFromUserIdConstructor_returnsZero` — fails on the original code, passes with the fix.

Also added: `OrderTest.constructorParity_allConstructorsLeaveListsNonNull` — meta-test that catches future divergent constructors via reflection.

## Verification
- Reproduction steps replayed on staging — bug no longer reproduces
- Full `OrderService` test suite passes (47 tests; 2 new + 45 existing)
- Spotbugs scan: no new warnings
- Linter: clean

## Prevention
Added the meta-test (constructor parity check) so any new constructor that leaves a collection field uninitialized fails CI. Documented the convention in `docs/coding-standards/null-safety.md`.
