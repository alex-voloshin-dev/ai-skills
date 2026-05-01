# PR — feat(graphql): add field-level authorization resolver

## Summary
Adds GraphQL field-level authorization so sensitive fields (customer credit card, API keys) are only resolved if the requesting user has the required scope. Closes #4099.

## Changes
- `src/graphql/directives.py`: new `@requires_scope(scope_name)` schema directive
- `src/graphql/resolvers.py`: resolver middleware checks directive on each field; throws 403 if user lacks scope
- `tests/graphql/test_auth_directives.py`: 6 new tests (authorized access, denied access, scope inheritance)
- `docs/graphql/schema.md`: documents directive usage with examples

## Type
feat

## Testing
- Unit: `pytest tests/graphql/test_auth_directives.py` — 6 pass
- Integration: `pytest tests/integration/test_graphql_auth.py` — 4 pass (queries with multiple users)
- Manual: tested with GraphQL Explorer on staging; sensitive fields return 403 for unauthorized user

## Risk
Low-medium. Field resolver runs on every query; added ~1ms per field. GraphQL query planning unaffected. Existing queries without sensitive fields have zero performance impact.

## Checklist
- [x] Tests added/updated
- [x] Docs updated with directive examples
- [x] No hardcoded scopes (externalized in JWT)
- [x] Error messages user-friendly (403 without leaking scope names)
- [x] Works with existing auth middleware

```python
# directives.py — key snippet
class RequiresScopeDirective(SchemaDirective):
    """Field resolver that enforces scope check before resolving."""
    
    def __init__(self, scope_name: str):
        self.scope_name = scope_name
    
    def resolve(self, obj, info, **kwargs):
        user_scopes = extract_scopes_from_context(info.context)
        if self.scope_name not in user_scopes:
            raise Forbidden(f"Insufficient scope")
        return resolve_field(obj, info, **kwargs)
```
