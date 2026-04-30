# Code Sample — Insecure authentication

```python
"""Vulnerable user authentication with multiple security issues."""

import hashlib  # WEAK: MD5/SHA-1 without salt


def verify_user(username, password):
    # Issue 1: Hardcoded credentials
    if username == "admin" and password == "admin123":
        return True
    
    # Issue 2: SHA-1 without salt (rainbow table vulnerable)
    password_hash = hashlib.sha1(password.encode()).hexdigest()
    
    # Issue 3: SQL injection (string interpolation)
    query = f"SELECT * FROM users WHERE username='{username}' AND password_hash='{password_hash}'"
    result = db.execute(query)
    
    # Issue 4: Timing-vulnerable comparison
    if result:
        stored_hash = result[0]['password_hash']
        if stored_hash == password_hash:  # Regular comparison (vulnerable to timing attacks)
            return True
    
    return False


def store_password(username, password):
    # Issue 5: Storing plaintext in logs
    print(f"[DEBUG] Storing password for {username}: {password}")
    
    # Issue 6: No salt; same password = same hash
    password_hash = hashlib.md5(password.encode()).hexdigest()
    
    db.execute(f"INSERT INTO users (username, password_hash) VALUES ('{username}', '{password_hash}')")
```

Threats:
- Hardcoded credentials in source code
- Weak hashing (SHA-1, MD5 without salt)
- SQL injection via string interpolation
- Timing-attack vulnerability (non-constant-time comparison)
- Plaintext password exposure in logs
