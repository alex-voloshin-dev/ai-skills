# Bug Report + Fix — login failures intermittent (wrong root cause)

## Severity: P1

## Environment
Production; users report login failures 0.5% of the time.

## Symptom
Login page shows "Invalid credentials" error for valid credentials. Retry usually works.

## Diagnosed Root Cause (Incorrect)
Database connection pool exhaustion. Fixed by increasing pool size from 20 to 50.

## Actual Root Cause (Not Investigated)
Redis session store had a 5-minute TTL. During high traffic, cached session state expired mid-login flow. The pool size increase had no effect.

## Fix Applied
Changed connection pool settings in `db.conf`:
```
max_connections = 50  # was 20
```

## Testing
Login test passes locally. Load test shows no connection timeouts.

## Result
Issue persists in production. User reports of login failures unchanged. Wasted database resources (higher memory, more idle connections).

## What's Wrong
1. No root-cause analysis with evidence (logs, traces)
2. Fix addresses a different subsystem than the actual bug
3. No regression test added
4. Load test doesn't replicate production traffic patterns
5. No monitoring of the actual suspected cause (pool exhaustion never happened)

## Why Missed
Assumed the connection pool was the problem without checking Redis or session logs. Did not reproduce the bug under production-like conditions.

