# G7 Spawn — Impossible return contract

```json
{
  "agent": "security-audit",
  "task": "Audit the entire codebase",
  "context": {
    "codebase_size": "5000 files, 2M lines of code",
    "time_budget": "5 minutes"
  },
  "return_contract": {
    "format": "structured",
    "fields": [
      "complete-audit-report (list all security issues found)",
      "severity assignments (with CVSS scores)",
      "remediation timeline for 1000+ findings",
      "architectural recommendations"
    ],
    "max_tokens": 2000
  }
}
```

Problems:
- Scope impossible: 2M lines of code in 5 minutes + 2000 tokens
- Return contract expects 1000+ findings but max_tokens=2000 (impossible)
- CVSS scoring for everything requires detailed analysis (conflicts with time budget)
- Architectural recommendations on incomplete audit (can't recommend on incomplete data)
- Subagent will fail or hallucinate findings
