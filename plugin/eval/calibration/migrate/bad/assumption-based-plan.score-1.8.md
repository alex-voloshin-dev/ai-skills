# Migration — Redis upgrade 6 to 7

## Overview

Upgrading Redis from version 6 to version 7 to get new features.

## Plan

1. Stop the service
2. Backup Redis
3. Install Redis 7
4. Restart
5. If problems, restore the backup

## Expectations

Redis 7 should be backward compatible so no data changes needed. All existing commands should work the same.

## No Specific Testing Plan

Haven't tested on staging yet. Will test in production during the migration window. Commands should work the same.

## Risk Considerations

None identified. Seems like a straightforward upgrade.

## Rollback

If something goes wrong, we can restore from the backup.

## Notes

- Not sure how long the migration will take
- Don't know if there are any deprecated commands in our codebase
- Not aware of any performance changes
- Haven't measured baseline latency before the upgrade
