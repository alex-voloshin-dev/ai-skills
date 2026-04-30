# How to optimize Postgres queries for your business metrics

You're tracking user engagement metrics in a Postgres database, and some queries run too slow. Let's fix that.

## The slow query problem

The query below pulls engagement data for your dashboard. It joins users, events, and metrics tables — but without good indexes, it scans millions of rows.

```sql
SELECT u.name, COUNT(e.id) as event_count, AVG(m.score) as avg_score
FROM users u
LEFT JOIN events e ON u.id = e.user_id
LEFT JOIN metrics m ON e.id = m.event_id
WHERE u.created_at > NOW() - INTERVAL '30 days'
GROUP BY u.id, u.name
ORDER BY event_count DESC;
```

Running this takes 45 seconds. Your dashboard times out.

## What's slowing it down

The database is doing a full table scan on events because there's no index on `event_id`. It also scans the entire users table before filtering by creation date.

## Three fixes

**Add an index on events(user_id).** This lets Postgres find all events for a specific user without scanning the whole table.

```sql
CREATE INDEX idx_events_user_id ON events(user_id);
```

**Add an index on metrics(event_id).** Same idea — avoids a full table scan when joining metrics.

```sql
CREATE INDEX idx_metrics_event_id ON metrics(event_id);
```

**Add an index on users(created_at).** Speeds up the WHERE clause filter.

```sql
CREATE INDEX idx_users_created_at ON users(created_at DESC);
```

## Results

After adding these three indexes, the same query runs in 1.2 seconds. Your dashboard loads instantly.

If you're running other similar queries, these indexes help those too — we're not building anything query-specific, just removing the full-table-scan bottleneck.

## Next steps

Run ANALYZE to update table statistics. Postgres will use them to pick better execution plans.

```sql
ANALYZE;
```

