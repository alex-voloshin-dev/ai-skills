# Migration Plan — Database schema migration v3 to v4

## Forward Procedure

1. Run the migration script
2. Application should continue working
3. Monitor for issues

## Rollback

If needed, restore from database backup.

## Performance Impact

Unknown. Have not measured baseline.

## Data Integrity

The migration script includes ALTER TABLE statements but we haven't verified that all rows survive the migration. The script adds a NOT NULL constraint to a column but doesn't set default values for existing rows. This might fail.

No checksums captured. No row-count verification planned.

## Testing

Only tested on a small dev database. Production has 50x more data so behavior might be different.

## Risks

- The script might take longer than expected on large table
- Some queries might break with the new schema
- Rollback procedure never tested
- Not sure how long restore from backup takes

## Questions Unanswered

- How much disk space is needed during the migration?
- Will locks cause table unavailability?
- What's the expected downtime?
- How do we know the migration succeeded?
