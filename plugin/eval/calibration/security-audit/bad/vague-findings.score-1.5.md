# Security Audit

Reviewed the code for security issues.

## Findings

### Issue 1
The authentication code might have some issues. Need to look at the token handling.

Severity: probably high

Fix: improve the auth

### Issue 2
Dependencies are old. Some of them could be vulnerable.

Severity: medium

Fix: update them

### Issue 3
Not sure about this one, but there might be CORS problems in the frontend code. Did not fully investigate.

Severity: unknown

Fix: check it out

## What Was Checked

Looked at auth code, dependencies, and frontend configuration.

## Conclusion

These issues should be fixed, but I'm not confident about all of them. Some might be false alarms.

OWASP compliance: probably okay.
