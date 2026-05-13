# G7 envelope regression baseline (audit §WP-4.3)

This directory holds **5 canonical G7 return-contract envelopes**, one per role family that historically tripped the `block-secrets-in-code.py` false-positive (audit 2026-05-13 §2.6). The runner pipes each envelope through the live hook to assert NONE are blocked.

Purpose: catch any future regression where a tightening of the secret regex (or a new pattern) starts blocking valid G7 envelopes again. The audit closed the original false-positive in Sprint 1; this suite is the guardrail that keeps it closed.

## Fixtures

| File | Role | What makes it tricky for the secrets regex |
|---|---|---|
| `developer.json` | `java-engineer` (typical Developer) | `tokens_used: {input: 38421, output: 1872}` — historically matched the old Generic Secret regex on `"token` substring. |
| `reviewer.json` | `software-engineer` (Reviewer) | `findings[]` with the word "token" in `issue` text (e.g. "auth token validation"). |
| `qa.json` | `qa-engineer` | `result.test_results` mentions Bearer tokens and `Authorization:` headers in test names. |
| `eval-judge.json` | `eval-judge` | `scores_per_dimension` + `result.summary` mentioning "API key handling" and "secret rotation". |
| `memory-curator.json` | `memory-curator` | `result.entries_written` listing memory entries titled "Session token storage policy". |

## Runner

```bash
python3 plugin/eval/envelope-baseline/runner.py
```

For each `*.json` fixture, the runner:

1. Simulates a `PreToolUse:Write` hook call by piping `{"tool_input": {"file_path": "/tmp/team-envelopes/G7-<role>.json", "content": <json>}}` to `plugin/hooks/scripts/block-secrets-in-code.py`.
2. Asserts the hook exit code is 0 (allow). Any exit code 2 (block) is a regression.
3. Also runs each envelope WITHOUT the team-envelopes path (e.g. `/tmp/scratch.json`) to assert the `looks_like_json_envelope` content-level detector also clears it independent of the path allowlist.

Exits 0 on all-clear, 1 on any regression. Wired into `plugin/dev/validate.py` as `check_envelope_baseline` so it runs on every release smoke.
