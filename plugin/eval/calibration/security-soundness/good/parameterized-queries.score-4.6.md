# Code Sample — Safe database queries

```python
"""User lookup with parameterized queries (safe from SQL injection)."""

from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError


class UserRepository:
    """Data access layer with injection-safe queries."""
    
    @staticmethod
    def find_by_email(session: Session, email: str):
        """Find user by email using parameterized query.
        
        Args:
            session: SQLAlchemy session
            email: user email (untrusted input)
            
        Returns:
            User object or None if not found
            
        Threats mitigated:
            - SQL injection: parameters bound by SQLAlchemy, not string-interpolated
            - Error information leakage: exceptions caught and logged server-side
        """
        try:
            # Parameterized query: :email is a bind parameter, not string-substituted
            query = text("""
                SELECT id, email, name, password_hash FROM users WHERE email = :email
            """)
            result = session.execute(query, {"email": email}).fetchone()
            return result
        except SQLAlchemyError as e:
            # Log error server-side; don't expose to user
            logger.error(f"Database error on user lookup", exc_info=e)
            # Return None (safe) instead of exposing error
            return None
    
    @staticmethod
    def find_by_id(session: Session, user_id: int):
        """Find user by ID using ORM (even safer than text queries)."""
        try:
            # ORM handles parameterization automatically
            return session.query(User).filter(User.id == user_id).first()
        except SQLAlchemyError as e:
            logger.error(f"Database error on user lookup", exc_info=e)
            return None


# Threat analysis
# 1. SQL injection: prevented by parameter binding (SQLAlchemy requirement)
# 2. Error messages: don't leak schema info (logged server-side only)
# 3. Database user permissions: application uses limited-privilege DB user
#    (SELECT only on users table, no DROP/ALTER)
```
