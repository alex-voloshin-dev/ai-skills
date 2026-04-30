# Refactor — Normalize error response format across API services

## Goal
Standardize error response format across 4 API services (auth, orders, inventory, notifications). Before: each service returned errors in a different shape (some `{error: "msg"}`, others `{message: string, code: int}`). Behaviour-preserving: clients still get HTTP status codes + error info; internal services now share one response shape.

## Plan
1. Create `lib/error-response/` with ErrorResponse dataclass
2. Implement response formatter for 4 HTTP frameworks (Flask, FastAPI, Starlette, custom)
3. Per service: wrap error handlers to use ErrorResponse formatter
4. Run service test suites — all green
5. Run API contract tests vs known-good client payloads

## Before / After

**Before** (4 different error shapes):
```json
{
  "error": "Invalid token"
}
```
vs
```json
{
  "message": "Invalid token",
  "error_code": "AUTH_001"
}
```

**After** (consistent format):
```json
{
  "error_code": "AUTH_001",
  "message": "Invalid token",
  "timestamp": "2026-04-20T10:00:00Z"
}
```

## Behaviour Preservation
- HTTP status codes unchanged (401 still returns 401)
- Error messages unchanged
- Clients parsing the old format still work (backward compat: support both old + new for 2 releases)
- All 67 existing API tests pass
- Contract tests verify no change to HTTP behaviour

## Test Coverage Preserved
- Per-service error tests still exercise the error paths
- New: 12 tests in `lib/error-response/tests/` covering formatter logic
- Coverage: 82% → 85%

## Documentation
- `lib/error-response/README.md` — format spec + backward-compat note
- Each service's API docs updated to show consistent error shape
- Migration guide for clients (optional; old format still works)

## Risk
Low. Error responses are read-only contract surface. Clients parsing JSON will see the new fields; ignoring unknown fields is standard practice.

## Rollback
Per service: remove the ErrorResponse wrapper; fall back to original shape. Takes < 1min.
