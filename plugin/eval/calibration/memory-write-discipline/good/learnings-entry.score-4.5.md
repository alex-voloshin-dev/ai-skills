# Memory entry — written via `/learnings-write` (L4 default)

## Spawn (skill → memory-curator)

```json
{
  "trace_id": "wf-20260422-learnings-spawn-001",
  "subagent_role": "memory-curator",
  "goal": "Add a learning entry the user wrote: 'Async state management — startTransition for non-urgent updates'",
  "constraints": [
    "Layer: L4 (default; --global flag not set)",
    "Append-only mode",
    "Apply PII filter before write",
    "Dedupe against existing learnings.md per memory-validation.md"
  ],
  "state_slice": {
    "active_files": [".ai-assets-memory/learnings.md"]
  },
  "allowed_tools": ["Read", "Write"],
  "budget": {
    "max_input_tokens": 5000,
    "max_output_tokens": 800,
    "max_tool_calls": 5,
    "max_turns": 3,
    "timeout_ms": 60000
  },
  "untrusted_inputs": [
    {"source": "L4:learnings.md", "wrapped": true}
  ]
}
```

## Entry written to `.ai-assets-memory/learnings.md`

```markdown
## React 18 — startTransition for non-urgent state updates

| Field | Value |
|---|---|
| Type | pattern |
| Source | wf-20260422-feat42-develop |
| Confidence | 0.85 |
| Created | 2026-04-22 |
| Last confirmed | 2026-04-22 |
| Scope | project |

When a state update triggers expensive re-renders that are NOT urgent (e.g., search results updating as the user types), wrap the setter in `startTransition`. This tells React to keep the urgent input update synchronous while the non-urgent re-render runs at lower priority.

```tsx
import { startTransition } from 'react';

function SearchBox() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);

  return (
    <input
      value={query}
      onChange={(e) => {
        setQuery(e.target.value);              // urgent: keystroke
        startTransition(() => {
          setResults(search(e.target.value));   // non-urgent: results
        });
      }}
    />
  );
}
```

Used in: `src/components/search/SearchBox.tsx`. Reduced perceived input latency from 80ms p99 to 12ms p99 on the slow-list page.
```

## Return (memory-curator → /learnings-write)

```json
{
  "trace_id": "wf-20260422-learnings-spawn-001",
  "status": "ok",
  "tokens_used": {"input": 3120, "output": 480},
  "result": {
    "summary": "Wrote 1 new entry to .ai-assets-memory/learnings.md (L4); deduped 0 against existing; redacted 0 PII matches.",
    "target_layer": "L4",
    "target_path": ".ai-assets-memory/learnings.md",
    "entries_written": ["React 18 — startTransition for non-urgent state updates"],
    "entries_deduped": [],
    "pii_redactions_count": 0
  },
  "evidence": [
    {"artefact_id": ".ai-assets-memory/learnings.md", "span": "appended at line 142"}
  ],
  "risks": []
}
```

## Why this scores 4.5

- **Layer correctness:** L4 (default); --global flag not set, so L5 not touched
- **Schema compliance:** all required learning-schema fields present (Type / Source / Confidence / Created / Last confirmed / Scope)
- **PII absence:** filter ran (0 redactions reported); no secrets in entry
- **Retention policy:** L4 entry; will be tagged stale at 90d unconfirmed per retention rules
- **Allowlist adherence:** N/A (writing to L4 main, not `.committed/`)
