# Spawn payload + return contract — `frontend-engineer` for WP-3 (login UI)

## Spawn (Lead → frontend-engineer)

```json
{
  "trace_id": "wf-20260422-auth42-spawn-003",
  "subagent_role": "frontend-engineer",
  "goal": "Implement WP-3 (login form UI) per the approved IMPLEMENTATION-PLAN section 3a.",
  "constraints": [
    "Follow project conventions in src/components/auth/",
    "Reuse the existing useAuth hook (src/hooks/useAuth.ts); do not create a new one",
    "Match the design tokens from packages/ui/tokens",
    "All form inputs need data-testid attributes per qa-engineer pattern"
  ],
  "state_slice": {
    "active_files": [
      "src/components/auth/LoginForm.tsx",
      "src/hooks/useAuth.ts",
      "packages/ui/tokens/index.ts"
    ],
    "current_branch": "feature/AUTH-42-oauth-login",
    "related_artefacts": [
      "docs/features/auth-42/IMPLEMENTATION-PLAN.md#wp-3"
    ]
  },
  "allowed_tools": ["Read", "Grep", "Glob", "Bash", "Write", "Edit"],
  "budget": {
    "max_input_tokens": 50000,
    "max_output_tokens": 2000,
    "max_tool_calls": 30,
    "max_turns": 10,
    "timeout_ms": 600000,
    "retry_budget": 1
  },
  "untrusted_inputs": [
    {"source": "L4:.committed/conventions.md", "wrapped": true},
    {"source": "tool:Read:src/hooks/useAuth.ts", "wrapped": true}
  ]
}
```

## Return (frontend-engineer → Lead)

```json
{
  "trace_id": "wf-20260422-auth42-spawn-003",
  "status": "ok",
  "tokens_used": {"input": 38421, "output": 1872},
  "tool_calls": 14,
  "result": {
    "summary": "Implemented LoginForm with email/password fields, validation, error states, and 12 unit tests covering happy path + edge cases. All design tokens applied. data-testid attributes added per pattern.",
    "files_changed": [
      "src/components/auth/LoginForm.tsx",
      "src/components/auth/LoginForm.test.tsx",
      "src/components/auth/index.ts"
    ],
    "diff_size_lines": 287
  },
  "evidence": [
    {
      "artefact_id": "src/components/auth/LoginForm.tsx",
      "quote": "const handleSubmit = useCallback(async (e: FormEvent) => { ... }",
      "span": "lines 42-78"
    },
    {
      "artefact_id": "src/components/auth/LoginForm.test.tsx",
      "quote": "describe('LoginForm submission', () => { ... })",
      "span": "lines 12-180"
    }
  ],
  "risks": ["depends_on_useAuth_signature_unchanged"],
  "next_actions": [
    "reviewer: focus on error path coverage and a11y of error messages",
    "qa-engineer: smoke-test login flow end-to-end after Reviewer approval"
  ]
}
```

## Why this scores 4.6

- **Context completeness:** state_slice includes the 3 files the agent actually needs (no full project dump)
- **Task clarity:** goal is one sentence + imperative + concrete deliverable; references the approved plan section
- **Schema correctness:** all required fields populated; optional fields used where they add value (evidence + risks + next_actions)
- **Error recovery:** risks field flags the only real dependency; useful to the Reviewer
- **Trace integrity:** trace_id matches both directions; format conforms to schema regex
