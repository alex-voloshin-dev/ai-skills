# G7 Spawn — Unclear request

```json
{
  "agent": "code-review",
  "task": "Review the code",
  "context": {
    "files": "src/",
    "standard": "general"
  },
  "return_contract": {
    "format": "anything",
    "expected": "feedback"
  }
}
```

Problems:
- No PR link or specific context
- "Review the code" undefined (all files? just changed? against what standard?)
- "general" is not a valid rubric
- Return format "anything" is meaningless
- No timeout or token budget specified
- No list of actual files or change scope
- Subagent has no idea what to evaluate
