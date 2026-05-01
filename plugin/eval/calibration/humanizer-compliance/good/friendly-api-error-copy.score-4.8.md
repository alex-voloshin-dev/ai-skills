# API Error Messages — Friendly and Clear

When your API request fails, you get back a JSON response explaining what went wrong. These messages are designed to help you fix the problem quickly.

## 400 Bad Request

You sent invalid data. The response tells you which field is wrong.

```json
{
  "error": "invalid_request",
  "message": "Email address is invalid. Must match user@example.com pattern.",
  "field": "email"
}
```

Fix: Check the email format. Does it have an `@` symbol and a domain?

## 401 Unauthorized

Your authentication token is missing or expired. Log in again.

```json
{
  "error": "invalid_token",
  "message": "Token expired. Please log in again."
}
```

Fix: Call the login endpoint to get a new token.

## 409 Conflict

The resource you're trying to create or update conflicts with something that already exists.

```json
{
  "error": "duplicate_key",
  "message": "A user with email alice@example.com already exists."
}
```

Fix: Use a different email address, or update the existing user instead.

## 429 Too Many Requests

You're sending requests too fast. Slow down and try again in a few seconds.

```json
{
  "error": "rate_limited",
  "message": "You've made 101 requests in the last minute. Limit is 100 per minute. Try again in 45 seconds."
}
```

Fix: Wait for the time shown, then retry. Consider spreading your requests over more time if you're doing bulk operations.

## 500 Internal Server Error

Something broke on our end. Your request is fine — we'll fix it.

```json
{
  "error": "server_error",
  "message": "We're having trouble processing your request. Support has been notified. Reference: err_5a7c9f2d"
}
```

Fix: Contact support with the reference ID. Don't retry immediately — the issue is server-side, not client-side.

