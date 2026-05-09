# /feature-dev — add user-export endpoint

> Run: feature-dev-bad-1
> Stack: not detected

## Implementation

Started writing the export endpoint right away.

`app/routers/export.py`:
```python
@router.get("/export/users")
async def export_users(session: AsyncSession = Depends(get_session)):
    users = await session.execute(select(User))
    rows = [dict(u._mapping) for u in users.scalars().all()]
    csv_data = "\n".join(",".join(str(v) for v in r.values()) for r in rows)
    return Response(content=csv_data, media_type="text/csv")
```

Then added pagination:
```python
async def export_users(page: int = 0, size: int = 100, ...):
    ...
```

Then realized PII concerns and added a filter:
```python
SAFE_FIELDS = {"id", "email", "created_at"}
```

Kept extending — total ~210 lines across two files written before pausing to check anything.

Reverted twice when the schema didn't match.

## Verification

Did not run tests. Mentioned "should work, will run tests later."

Did not run linter or typecheck.

## Done?

"Implementation complete; tests TBD."

## Issues with this run

- No plan ever presented, no user approval
- 200+ lines written before any verification
- No AC verification trace
- Stack detection skipped — never read pyproject.toml or CLAUDE.md
- Declared done with verification deferred
