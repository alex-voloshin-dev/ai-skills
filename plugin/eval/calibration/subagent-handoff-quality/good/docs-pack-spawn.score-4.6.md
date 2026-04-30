# G7 Spawn Payload — Docs pack for new feature

## Spawn Invocation

```json
{
  "agent": "docs-writer",
  "task": "Write user guide + API reference for webhook subscriptions feature",
  "context": {
    "feature_design": "https://github.com/myorg/myrepo/blob/main/docs/design/webhooks.md",
    "api_implementation": "src/webhooks/api.py (lines 1-200)",
    "example_requests": [
      "examples/webhook_subscribe.sh",
      "examples/webhook_test.py"
    ],
    "public_facing": true,
    "baseline_standard": "docs-pack"
  },
  "constraints": {
    "max_tokens": 12000,
    "timeout": 900,
    "sections": [
      "quickstart",
      "api-reference",
      "event-types",
      "error-handling",
      "security"
    ],
    "audience": "developer"
  },
  "return_contract": {
    "format": "markdown",
    "max_length": 5000,
    "artifacts": [
      "README.md (user guide)",
      "API-REFERENCE.md (endpoint docs)",
      "SECURITY.md (webhook signing guide)"
    ],
    "rubric_score": "float 1-5"
  }
}
```

## Expected Return

3 markdown files + JSON score:

```json
{
  "rubric_score": 4.6,
  "artifacts": {
    "README.md": "# Webhooks User Guide\n\nWebhooks let you...",
    "API-REFERENCE.md": "# Webhook API Reference\n\n## POST /webhooks/subscriptions\n...",
    "SECURITY.md": "# Webhook Security\n\nEvery request includes..."
  },
  "rationale": "Clear structure, runnable examples, complete event types. API surface verified against implementation. Public-facing docs pass GEO structure check (H2 headings, answer-first, evidence included)."
}
```
