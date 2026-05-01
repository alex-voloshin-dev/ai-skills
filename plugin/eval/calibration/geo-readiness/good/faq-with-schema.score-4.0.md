# Frequently Asked Questions — API authentication

> Updated 2026-04-20

**What authentication methods does the API support?** We support OAuth 2.0, API keys, and JWT tokens. OAuth 2.0 is recommended for third-party integrations; API keys for internal services; JWT tokens for single-page applications. Each method supports the same endpoint permissions.

**How do I rotate my API key?** Generate a new key in your account settings. Both old and new keys work during a 7-day overlap period (giving you time to update your applications). After 7 days, old keys expire automatically. You can revoke an old key immediately without waiting.

**Can I use the same token for multiple requests?** Yes. JWT tokens last 8 hours. During that time, you can make unlimited requests with the same token. When it expires, get a fresh token from the `/auth/refresh` endpoint without re-authenticating.

**What should I do if I accidentally commit a token to git?** Revoke it immediately in your account settings. Then generate a new token and update your code. The old token is invalid within 10 seconds. You don't need to rotate all your tokens, just the exposed one.

**How should I handle token expiration in my app?** When you get a 401 response, your token expired. Call `/auth/refresh` to get a new one, then retry the original request. We recommend refresh tokens instead: your app gets a long-lived refresh token (valid 90 days), which it uses to fetch short-lived access tokens (8h). This limits exposure if an access token leaks.

---

**JSON-LD Schema**

```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "What authentication methods does the API support?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "We support OAuth 2.0, API keys, and JWT tokens..."
      }
    },
    {
      "@type": "Question",
      "name": "How do I rotate my API key?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Generate a new key in your account settings..."
      }
    }
  ]
}
```
