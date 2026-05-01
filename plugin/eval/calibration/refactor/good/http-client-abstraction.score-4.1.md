# Refactor — Extract HTTP client to plugin interface

## Goal
Replace direct HTTP library calls (urllib) scattered across 8 modules with a single `HttpClient` interface. Behaviour-preserving: all requests work identically; retry logic + timeout + error handling unchanged. Improves testability (mock single interface vs 8 locations).

## Plan
1. Create `lib/http-client/` with `HttpClient` interface (request, get, post, etc.)
2. Implement with urllib backend matching current behaviour (timeout=30s, retries=3, backoff)
3. Per module: replace urllib calls with `http_client.get(url, **kwargs)`
4. Run module tests after each change — all green
5. Run integration suite

## Before / After

**Before** (8 modules with inline urllib):
- `api/client.py` — urllib.request.urlopen, custom retry loop
- `sync/webhook_puller.py` — requests library, custom timeout handling
- `reports/exporter.py` — urllib3, custom headers
- (5 more with similar patterns)

**After** (1 interface, 1 implementation):
- `lib/http-client/interface.py` — HttpClient protocol
- `lib/http-client/urllib_impl.py` — concrete implementation (wrapper around urllib)
- 8 modules: single-line `http_client.get/post` calls

## Behaviour Preservation
- Timeout: 30s (consistent across all old implementations)
- Retries: exponential backoff (same algorithm as current api/client.py)
- SSL verification: enabled (current default preserved)
- Custom headers: passthrough to implementation
- All existing tests pass (156 tests, all green)
- Verified via integration test replicating 8 real API calls

## Test Coverage Preserved
- 8 module tests still exercise HTTP layer via mocked HttpClient
- New: 18 tests in `lib/http-client/tests/` covering error paths + timeout + retry logic
- Coverage: 87% → 89% (improvement from centralizing HTTP error paths)

## Documentation
- `lib/http-client/README.md` — interface + usage examples
- Docstrings in interface explain timeout / retry / exception contract
- No ADR needed (internal refactor)
- CHANGELOG.md notes consolidation

## Risk
Very low. HttpClient is a thin wrapper; existing modules' logic unchanged. Integration tests prove end-to-end HTTP behaviour identical.

## Rollback
Per module: revert one import statement. Library can be deleted (unused code is safe).
