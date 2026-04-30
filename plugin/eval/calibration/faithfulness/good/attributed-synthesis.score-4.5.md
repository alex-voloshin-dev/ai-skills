# Summary of Two Sources — Attributed Synthesis

Source 1: OWASP Top 10 (2021), A02 Cryptographic Failures
Source 2: CWE-327 "Use of Broken or Risky Cryptographic Algorithm"

## Summary

Both OWASP and CWE identify weak cryptography as a critical vulnerability category. OWASP A02 states that over 40% of applications fail to encrypt sensitive data in transit (citing industry penetration tests from 2020-2021). CWE-327 lists MD5, DES, and RC4 as broken algorithms; OWASP reinforces this, noting that "SHA-1 and MD5 should not be used for hashing passwords" (A02 guidance, 2021).

Industry consensus: modern systems should use TLS 1.3 for transport, AES-256 for storage, and bcrypt/argon2 for password hashing.

## Fact Checks

1. **OWASP A02 exists and is titled "Cryptographic Failures"**
   - Source 1, OWASP Web Top 10 (2021): confirmed. Title exact match.

2. **40% of applications fail to encrypt sensitive data in transit**
   - Source 1, A02 introductory statistics: "Over 40% of assessment-covered organizations failed to encrypt sensitive data in transit". Attributed directly; included quote marks.

3. **MD5, DES, RC4 listed as broken by CWE-327**
   - Source 2, CWE-327 description: "Examples: MD5, DES, RC4...". All three present. Accurate.

4. **SHA-1 and MD5 not recommended for password hashing per OWASP**
   - Source 1, A02 mitigation guidance: "Use bcrypt, scrypt, or argon2 for passwords; avoid MD5, SHA-1". Paraphrased accurately; core guidance correct.

## Confidence

High. Synthesized claims are attributed to source, direct quotes used where appropriate, paraphrases marked as such.
