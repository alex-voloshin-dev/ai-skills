# PR — feat(auth): add `Secure` and `SameSite=Lax` to session cookies

## Summary
Hardens session cookies against CSRF and accidental cleartext leakage by setting `Secure` and `SameSite=Lax` attributes. Closes #4218.

## Changes
- `src/auth/session.py`: cookie builder now sets `secure=True`, `samesite="Lax"` on prod and staging; dev keeps `Lax` only (no HTTPS in dev)
- `tests/auth/test_session.py`: 4 new tests cover the flag matrix per env (prod / staging / dev)
- `docs/security/cookies.md`: documents the policy + dev exemption

## Type
fix

## Testing
- Unit: `pytest tests/auth/test_session.py` — 14 pass (10 existing + 4 new)
- Integration: `pytest tests/integration/test_login_flow.py` — 6 pass
- Manual: verified with browser DevTools on staging — `Set-Cookie` shows `Secure; SameSite=Lax`

## Risk
Low. Cookies still issued on existing domain; `SameSite=Lax` allows top-level navigations (login redirects unaffected). No client changes needed.

## Checklist
- [x] Tests added/updated
- [x] Docs updated
- [x] No secrets in code
- [x] Security-soundness rubric passes (`secure=True` + `SameSite=Lax`)
- [x] Behaviour preserved on dev (no breakage in local docker-compose flow)

```python
# session.py — relevant snippet
def make_session_cookie(value: str, env: str) -> CookieAttrs:
    return CookieAttrs(
        name="session",
        value=value,
        secure=(env in ("prod", "staging")),
        samesite="Lax",
        httponly=True,
        max_age=timedelta(hours=8),
    )
```
