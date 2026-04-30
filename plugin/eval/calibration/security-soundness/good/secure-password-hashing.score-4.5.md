# Code Sample — Secure password handling

```python
"""User authentication with bcrypt hashing and safe comparison."""

import bcrypt
from hmac import compare_digest


class UserAuth:
    """Manages user authentication with secure password storage."""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt (cost=12, default).
        
        Args:
            password: plaintext password from user input
            
        Returns:
            bcrypt hash (includes salt), safe to store in database
        """
        # bcrypt.hashpw() includes salt generation internally
        salt = bcrypt.gensalt(rounds=12)  # 12 rounds = ~100ms on modern CPU
        return bcrypt.hashpw(password.encode(), salt).decode()
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verify password against bcrypt hash.
        
        Uses constant-time comparison to prevent timing attacks.
        
        Args:
            password: plaintext password to verify
            hashed: stored bcrypt hash from database
            
        Returns:
            True if password matches, False otherwise
        """
        try:
            # bcrypt.checkpw() uses constant-time comparison
            return bcrypt.checkpw(password.encode(), hashed.encode())
        except (ValueError, TypeError):
            # Hash format invalid; treat as failed auth
            return False


# Threat analysis
# 1. Offline attacks: bcrypt cost=12 = 100ms/attempt; 1M attempts = 1.2 days
#    (acceptable for high-entropy passwords; recommend 12+ char min)
# 2. Timing attacks: bcrypt.checkpw() is constant-time built-in
# 3. Rainbow tables: bcrypt includes unique salt per hash; rainbow tables infeasible
# 4. Accidental plaintext leaks: passwords never logged, only hashes stored
```
