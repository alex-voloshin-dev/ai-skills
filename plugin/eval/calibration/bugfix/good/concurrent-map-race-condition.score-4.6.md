# Bug Report + Fix — race condition in UserCache.put() on concurrent writes

## Severity: P2

## Environment
Production; intermittently seen in metrics on high-concurrency periods (6+ simultaneous writes to same user).

## Bug
User's profile data sometimes shows stale version after update. Two concurrent updates to the same user cache entry result in one update being silently lost. Symptom: updated email address reverts to old value after profile edit (race window ~100ms).

## Root Cause
`UserCache.put(userId, user)` reads from internal HashMap, checks TTL, then writes back. Between the read and write, another thread can invalidate the entry. No synchronization on the HashMap access.

5-whys:
1. Why lost? Concurrent write overwrites the later update
2. Why concurrent writes? Cache.put called from both main request thread and background sync thread
3. Why no lock? Original implementation used `Collections.synchronizedMap()` but was removed in refactor #3790 for "performance"
4. Why removed unsafely? Refactor PR didn't test concurrent scenarios; used `get-check-put` pattern which is not atomic
5. Why missed? Load test suite runs single-threaded; concurrency tests exist but weren't run pre-merge

Class of bug: unsafe refactor removing synchronization without re-testing concurrency.

## Fix
- `UserCache.java`: replace HashMap with ConcurrentHashMap for thread-safe reads
- Replace `get-check-put` pattern with atomic `putIfPresent(userId, user, ttl)` method using ConcurrentHashMap's atomic operations
- Add explicit synchronization for the TTL check-and-set sequence

## Regression Test
`UserCacheTest.concurrentPuts_lastWriteWins` — spawns 10 threads, each writing to the same user 100 times; verifies final value equals last-write value, fails without fix.

Meta-test: `UserCacheTest.stressTest_1000ThreadsRandomOps` — concurrent reads/writes/invalidates over 5 seconds; no exceptions and consistency maintained.

## Verification
- Load test re-run with 50 concurrent users; no cache inconsistencies
- Full test suite passes (89 tests; 2 new + 87 existing)
- FindBugs scan: no data-race warnings
- Performance: putIfPresent is ~3% slower than naive put; acceptable for correctness

## Prevention
Updated concurrency guidelines doc; added checklist item "concurrent access analyzed and tested" to PR review template. Load tests now always run with min 50 concurrent users.

