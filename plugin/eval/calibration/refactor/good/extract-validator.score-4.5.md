# Refactor — Extract address validation to shared module

## Goal
Extract repeated address-validation logic from 3 services (`checkout`, `shipping`, `account`) into a single `address-validator` library. Behaviour-preserving: zero changes to public API of the 3 services; same validation rules, same error messages, same edge cases.

## Plan
1. Create `lib/address-validator/` with the consolidated `AddressValidator` interface
2. Per service: replace inline validation with `AddressValidator.validate(addr)`
3. Per service: run service test suite — all green before next service
4. Final: run all 3 service test suites + integration suite

## Before / After

**Before** (3 separate implementations, ~80 lines each across 3 services):
- `checkout/internal/address.py` — 84 lines
- `shipping/internal/address_check.py` — 78 lines (slight differences: stricter postal code regex)
- `account/profile/address_validator.py` — 91 lines (extra: street-name length check)

**After** (1 library, 87 lines):
- `lib/address-validator/validator.py` — accepts a `policy` arg with the strictest defaults; per-service callers pass policy overrides where their behaviour differed
- 3 services: 8-line wrappers calling the library

## Behaviour Preservation
- Public API of all 3 services unchanged (verified via OpenAPI diff: empty)
- All existing test suites pass (47 + 32 + 28 = 107 tests, all green)
- Stricter shipping postal-code regex preserved via `policy=ShippingPolicy()` override
- Account street-name length check preserved via `policy=AccountPolicy()` override

## Test Coverage Preserved
- Per-service tests still exercise the wrapper + library together
- New: 12 tests in `lib/address-validator/tests/` covering policy combinations directly
- Coverage: 94% → 96% on validation paths (improvement from consolidating tests)

## Documentation
- `lib/address-validator/README.md` — usage + policy options + migration note for downstream consumers
- 3 service ADRs updated to reference the shared library
- `CHANGELOG.md` notes the consolidation under "Refactoring"

## Risk
Minimal. Library is a strict superset of the 3 implementations (per dimension). Tests prove zero behaviour change.

## Rollback
Per service: revert the wrapper change (one file per service); library can stay (no consumer = no harm).
