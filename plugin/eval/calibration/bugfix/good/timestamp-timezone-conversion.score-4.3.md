# Bug Report + Fix — timestamps stored as UTC but rendered in UTC instead of user's local timezone

## Severity: P2

## Environment
Production; affects all users with non-UTC timezones viewing scheduled task times.

## Bug
Users in PST see a 8:00 AM scheduled task listed as 4:00 PM instead of 8:00 AM. The task executes at the correct UTC time, but the UI displays the wrong local time.

## Root Cause
Timeline service stores all task times as UTC (correct). Rendering layer calls `ScheduledTask.getTime()` which returns a UTC Instant. The Vue component renders it directly without timezone conversion. The timezone info is available in the JWT (`user.timezone_hint`) but not passed to the renderer.

5-whys:
1. Why wrong time? Rendered as UTC without conversion
2. Why not converted? Renderer doesn't have timezone context
3. Why doesn't it? Component initialization doesn't extract user timezone from JWT
4. Why not? Timezone prop was removed in refactor PR #3847 (scope creep)
5. Why missed? PR reviewer approved a "UI cleanup" without checking if removed props were actually unused

Class of bug: scope-creep refactor removing context from child components.

## Fix
- `ScheduledTask.java`: add method `getTimeInUserTimezone(ZoneId tz)` that returns ZonedDateTime
- Vue component: extract `user_timezone` from JWT at mount time; pass to formatter function
- `time-formatter.js`: update to accept ZonedDateTime or Instant + ZoneId; render in local timezone

## Regression Test
`ScheduledTaskTest.renderTime_respectsUserTimezone_pst` — renders 2026-04-20T16:00:00Z with PST timezone, expects 08:00, fails on original code.

Also added: `TimeFormatterTest.formatWithTimezone_roundtrip` — proves formatting survives serialization/deserialization without UTC loss.

## Verification
- Reproduction: manually tested on staging with mock user in PST; time now displays correctly
- Full test suite passes (112 tests; 2 new + 110 existing)
- Browser Dev Tools verified rendered HTML contains correct time string
- No new timezone-related warnings from linter

## Prevention
Added JSDoc example to time-formatter showing required timezone parameter; linter now enforces it on all formatter calls. Updated component initialization checklist to include timezone extraction.

