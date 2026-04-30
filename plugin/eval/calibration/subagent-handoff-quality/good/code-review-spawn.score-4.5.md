# G7 Spawn Payload — Code review subagent

## Spawn Invocation

```json
{
  "agent": "code-review",
  "task": "Review PR for security vulnerabilities and style",
  "context": {
    "pr_url": "https://github.com/myorg/myrepo/pull/1234",
    "pr_title": "feat(auth): add TOTP two-factor auth",
    "pr_description": "Implements time-based one-time passwords for 2FA per RFC 6238",
    "files_changed": [
      "src/auth/totp.py",
      "src/auth/verification.py",
      "tests/auth/test_totp.py"
    ],
    "baseline_standard": "security-soundness"
  },
  "constraints": {
    "max_tokens": 8000,
    "timeout": 600,
    "focus_areas": [
      "cryptographic correctness",
      "secret handling",
      "error messages don't leak info"
    ]
  },
  "return_contract": {
    "format": "structured",
    "fields": [
      "summary",
      "findings (list of {severity, location, description, remediation})",
      "rubric_score (float 1-5)",
      "pass_threshold": 4.0
    ]
  }
}
```

## Expected Return

```json
{
  "summary": "PR implements RFC 6238 correctly. 1 finding: hardcoded secret in test fixture not marked as example.",
  "findings": [
    {
      "severity": "LOW",
      "location": "tests/auth/test_totp.py:12",
      "description": "Test fixture contains hardcoded secret 'secret-key-12345'. Mark as example or test-only.",
      "remediation": "Add comment or use test constant: SECRET_FOR_TESTS = '...'"
    }
  ],
  "rubric_score": 4.5,
  "rationale": "Cryptographic logic correct (HMAC-SHA1, 30s window, 6-digit codes per RFC). Error messages don't leak validation steps. One minor test-only issue."
}
```
