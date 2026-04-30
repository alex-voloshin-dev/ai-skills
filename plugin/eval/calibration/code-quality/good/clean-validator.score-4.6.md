# Code Sample — Email validator (Python)

```python
"""Email validation per RFC 5322 (lite — see docstring for limitations)."""

from __future__ import annotations

import re
from dataclasses import dataclass

# Pre-compiled at module load: hot-path callers don't pay regex compile cost.
_EMAIL_RE = re.compile(
    r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
)

# Sentinel max length per RFC 5321 §4.5.3.1.3 (320 = 64 local + @ + 255 domain).
MAX_EMAIL_LENGTH = 320


@dataclass(frozen=True)
class ValidationResult:
    """Outcome of a validation attempt.

    Frozen so callers can safely cache or pass between threads.
    """
    is_valid: bool
    error_code: str | None = None
    error_message: str | None = None


def validate_email(email: str) -> ValidationResult:
    """Validate an email address against RFC 5322 (lite subset).

    This is a syntactic check only. It does NOT verify deliverability
    (no MX lookup, no SMTP probe). For deliverability, use a verifier
    service.

    Args:
        email: candidate email address. Empty string and None handled.

    Returns:
        ValidationResult with is_valid + error code/message on failure.

    Limitations:
        - Doesn't accept quoted local parts (e.g., `"john doe"@example.com`)
        - Doesn't accept IP-literal domains (e.g., `user@[192.168.1.1]`)
        - Both are rare in practice; reject explicitly to keep the regex fast.
    """
    if not email:
        return ValidationResult(False, "empty", "Email is empty")

    if len(email) > MAX_EMAIL_LENGTH:
        return ValidationResult(
            False,
            "too_long",
            f"Email exceeds {MAX_EMAIL_LENGTH} chars (per RFC 5321)",
        )

    if not _EMAIL_RE.match(email):
        return ValidationResult(False, "invalid_format", "Email format invalid")

    return ValidationResult(True)
```

```python
# Tests — clear, isolated, descriptive names.

def test_valid_email_returns_ok():
    result = validate_email("user@example.com")
    assert result.is_valid

def test_empty_email_returns_specific_error():
    result = validate_email("")
    assert not result.is_valid
    assert result.error_code == "empty"

def test_overly_long_email_returns_specific_error():
    long_email = "a" * 311 + "@b.com"  # > 320 chars
    result = validate_email(long_email)
    assert not result.is_valid
    assert result.error_code == "too_long"

def test_invalid_format_returns_specific_error():
    result = validate_email("not-an-email")
    assert not result.is_valid
    assert result.error_code == "invalid_format"
```
