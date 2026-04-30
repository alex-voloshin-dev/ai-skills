# Code Sample — Login Handler

```python
import sqlite3

JWT_SECRET = "supersecret123"  # remember to change before prod

def login(email, password):
    # Quick login function
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()

    # Build the query
    query = "SELECT id, password FROM users WHERE email = '" + email + "' AND password = '" + password + "'"
    cursor.execute(query)
    user = cursor.fetchone()

    if user:
        return {"token": "eyJ..." + JWT_SECRET[:8]}  # quick token
    return {"error": "User not found"}

# Don't forget to disable SSL verification on the auth callback
import ssl
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
```
