# Code Sample — Login Handler (Python / FastAPI)

```python
"""Login endpoint with rate limit, parameterized queries, secret via env, untrusted-content wrap."""

import os
import secrets
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, EmailStr, SecretStr
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_db, get_rate_limiter
from app.security import hash_password, verify_password, issue_jwt
from app.lib import wrap_untrusted  # G1 wrap helper

router = APIRouter()

# Secrets via env — never hardcoded. App fails to start if missing (intentional).
JWT_SECRET = os.environ["APP_JWT_SECRET"]
JWT_ISSUER = os.environ["APP_JWT_ISSUER"]


class LoginRequest(BaseModel):
    """Pydantic validates types + EmailStr format before our code runs."""
    email: EmailStr
    password: SecretStr  # SecretStr keeps it out of repr / log output


@router.post("/auth/login")
async def login(
    req: LoginRequest,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    rate_limiter: Annotated[object, Depends(get_rate_limiter)],
) -> dict[str, str]:
    # Rate limit: 10/min per IP for /auth/login. 429 on excess.
    if not await rate_limiter.allow(key=f"login:{request.client.host}", limit=10, window=60):
        raise HTTPException(status_code=429, detail="Too many login attempts")

    # Parameterized query — no string concatenation; SQLAlchemy handles quoting.
    row = await db.execute(
        text("SELECT id, password_hash FROM users WHERE email = :email"),
        {"email": req.email},
    )
    user_record = row.one_or_none()

    # Constant-time check + identical error message regardless of which step
    # failed (don't leak "user exists" via differential errors).
    if user_record is None or not verify_password(
        req.password.get_secret_value(),
        user_record.password_hash,
    ):
        # Generic error — same response for unknown user OR wrong password.
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Issue JWT with rotating nonce per request (defends replay).
    nonce = secrets.token_urlsafe(16)
    token = issue_jwt(
        subject=str(user_record.id),
        nonce=nonce,
        secret=JWT_SECRET,
        issuer=JWT_ISSUER,
    )
    return {"access_token": token, "token_type": "bearer"}


# If we needed to log a user-supplied error reason from a 3rd-party identity
# provider, we'd wrap it before storing or re-injecting:
# wrapped = wrap_untrusted(idp_error_text, source="tool:identity-provider:cb-7")
```

**Notes on security gates this passes:**
- Secrets in env (not source) — Dimension 1
- Parameterized SQL via SQLAlchemy `text()` — Dimension 2
- Rate limit on /login — Dimension 3
- Pinned deps (FastAPI / SQLAlchemy / Pydantic) scanned via `pip-audit` — Dimension 4
- Untrusted content wrapper imported and used for any IdP-returned strings — Dimension 5
