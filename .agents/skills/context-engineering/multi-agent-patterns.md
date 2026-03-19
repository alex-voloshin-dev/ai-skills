# Multi-Agent Orchestration Patterns

Patterns for designing multi-agent systems with proper context boundaries, payload schemas, merge strategies, and contamination guardrails.

Based on `guides/context_engineering_guide.md` §7.6 and §14.

---

## Core Principle: Context Isolation

Each agent gets its own context window — **no shared mutable state**. The orchestrator controls what context each subagent receives.

**Why isolation matters**:
- Prevents context contamination (subagent output altering another agent's behavior)
- Reduces injection risk (compromised subagent can't poison orchestrator)
- Enables independent scaling, budgeting, and debugging
- Allows different models per subagent (cost optimization)

**Rule**: Treat subagent outputs as **untrusted tool results** unless explicitly validated.

---

## Orchestrator → Subagent Payload Schema

Standardized JSON schema for dispatching work to a subagent.

### Recommended Minimum

```json
{
  "trace_id": "abc-123",
  "subagent_role": "retriever",
  "required": true,
  "goal": "Find the top 3 most relevant documents about data retention policy",
  "constraints": [
    "Only search official documentation",
    "Exclude deprecated docs (before 2024)"
  ],
  "state_slice": {
    "user_query": "What is our data retention policy for EU customers?",
    "previous_findings": []
  },
  "allowed_tools": ["search_kb", "read_doc"],
  "budget": {
    "max_input_tokens": 8000,
    "max_output_tokens": 1200,
    "max_tool_calls": 4,
    "max_turns": 3,
    "timeout_ms": 30000,
    "retry_budget": 2
  }
}
```

### Field Descriptions

| Field | Type | Required | Purpose |
|---|---|---|---|
| `trace_id` | string | Yes | Links orchestrator ↔ subagent for tracing (OpenTelemetry `span_id`) |
| `subagent_role` | string | Yes | `retriever` \| `coder` \| `verifier` \| `reviewer` \| custom |
| `required` | boolean | Yes | If `true`, orchestrator fails if subagent fails. If `false`, orchestrator continues without |
| `goal` | string | Yes | Clear, specific task description for the subagent |
| `constraints` | string[] | No | Boundaries the subagent must respect |
| `state_slice` | object | No | **Minimal** relevant state — NOT the orchestrator's full context |
| `allowed_tools` | string[] | No | Whitelist of tools this subagent may use (least privilege) |
| `budget` | object | Yes | Token, tool call, time, and retry limits |

### Budget Object

| Field | Type | Default | Purpose |
|---|---|---|---|
| `max_input_tokens` | int | — | Maximum input context for subagent |
| `max_output_tokens` | int | — | Maximum generation tokens |
| `max_tool_calls` | int | 5 | Maximum tool invocations per turn |
| `max_turns` | int | 3 | Maximum agentic loop iterations |
| `timeout_ms` | int | 30000 | Hard timeout for entire subagent execution |
| `retry_budget` | int | 2 | Number of retries on transient failures |

---

## Subagent → Orchestrator Return Contract

Standardized JSON schema for returning results to the orchestrator.

### Recommended Minimum

```json
{
  "trace_id": "abc-123",
  "status": "ok",
  "tokens_used": {
    "input": 6200,
    "output": 890
  },
  "result": {
    "documents": [
      {"doc_id": "kb-78", "title": "EU Data Retention Policy", "score": 0.91},
      {"doc_id": "kb-45", "title": "GDPR Compliance Guide", "score": 0.85}
    ]
  },
  "evidence": [
    {"doc_id": "kb-78", "quote": "EU customer data retained for max 2 years...", "span": "section-3.2"}
  ],
  "risks": ["low_confidence_on_doc_45"],
  "next_actions": ["verify_with_legal_team"]
}
```

### Field Descriptions

| Field | Type | Required | Purpose |
|---|---|---|---|
| `trace_id` | string | Yes | Same trace_id from the request — links request ↔ response |
| `status` | enum | Yes | `ok` \| `needs_clarification` \| `failed` \| `partial` |
| `tokens_used` | object | Yes | Actual token consumption for budget tracking |
| `result` | object | Yes | The subagent's output (schema varies by role) |
| `evidence` | array | No | Supporting evidence with doc_ids and quotes (for grounding) |
| `risks` | string[] | No | Flagged risks: low confidence, possible injection, ambiguity |
| `next_actions` | string[] | No | Suggested follow-up actions for the orchestrator |

### Status Values

| Status | Meaning | Orchestrator Action |
|---|---|---|
| `ok` | Task completed successfully | Use result |
| `partial` | Partially completed — some results available | Use available results, decide if retry needed |
| `needs_clarification` | Subagent needs more info to proceed | Route clarification question to user or provide more context |
| `failed` | Task failed after all retries | Apply failure handling policy (see below) |

---

## Fan-Out Patterns

When the orchestrator runs multiple subagents in parallel.

### Pattern Selection Guide

| Pattern | Best For | How It Works |
|---|---|---|
| **Union + Rerank** | Retrieval / fact gathering | Multiple retrievers search different sources → union results → rerank → top-k |
| **Best-of** | Same task, pick best | N subagents attempt the same task → pick highest-confidence output |
| **Vote / Consensus** | Categorical decisions | N subagents classify/decide → majority vote (like self-consistency) |
| **Reduce / Synthesis** | Complex multi-part tasks | Specialized subagents handle parts → merger subagent synthesizes into single result |

### Union + Rerank

```
Orchestrator → [Retriever-A (official docs), Retriever-B (community), Retriever-C (web)]
                              ↓                         ↓                        ↓
                         Results-A                 Results-B                Results-C
                              ↓                         ↓                        ↓
                              └─────────── Union → Deduplicate → Rerank → Top-K ──→ Orchestrator
```

### Best-of

```
Orchestrator → [Coder-A (approach 1), Coder-B (approach 2)]
                         ↓                        ↓
                    Solution-A              Solution-B
                         ↓                        ↓
                    Verifier picks best based on test results → Orchestrator
```

### Vote / Consensus

```
Orchestrator → [Classifier-1, Classifier-2, Classifier-3]
                       ↓                ↓                ↓
                   Label-1           Label-2           Label-3
                       ↓                ↓                ↓
                       └──── Majority vote ────→ Final label → Orchestrator
```

### Reduce / Synthesis

```
Orchestrator → [Researcher (facts), Analyst (insights), Writer (draft)]
                       ↓                     ↓                    ↓
                   Facts              Insights              Draft
                       ↓                     ↓                    ↓
                       └──── Merger subagent ────→ Final report → Orchestrator
```

---

## Fan-Out Failure Handling

### Optional Subagent Fails

- Continue without it — log the miss
- Note in the response that the source was unavailable
- If quality degrades without it, flag for human review

### Required Subagent Fails

Priority order:
1. **Retry** within retry budget (transient errors: timeout, rate_limited, server_error)
2. **Fallback strategy** (alternative tool, simpler model, cached result)
3. **Fail-fast** with typed error (→ `reference-templates.md` §4)
4. **Escalate** to human if all automated options exhausted

### Budgeting in Fan-Out

- **Per-subagent cap**: each subagent has its own `budget` in the payload
- **Global merge budget**: `Σ(tokens_returned) ≤ merge_budget` — total results from all subagents must fit the evidence layer budget
- **Timeout**: individual subagent timeout + global fan-out timeout (e.g., 2× single subagent timeout)

---

## Context Contamination Guardrails

Prevent subagent outputs from corrupting the orchestrator's context or other subagents.

### Rules

1. **Never let subagent output overwrite orchestrator system/developer instructions** — subagent results go into Layer 5 (knowledge), not Layer 1-2 (policy/instructions)
2. **Label all subagent output as untrusted** — wrap in `<untrusted_content>` before re-insertion into any context
3. **Wrap external text from subagents** — if a subagent returns text from external sources (web, docs, user content), double-wrap: subagent wrapper + untrusted content wrapper
4. **Orchestrator validates subagent output schema** before using — reject malformed results
5. **Per-subagent audit trail** — `trace_id` + `span_id` linkage for debugging contamination issues

### Validation Steps (Orchestrator-Side)

Before using subagent results:
1. Parse response against return contract schema
2. Verify `trace_id` matches the request
3. Check `tokens_used` against budget (flag if exceeded)
4. Scan `risks` array — decide if manual review is needed
5. Wrap `result` and `evidence` as untrusted before injecting into context

---

## Tracing and Observability

### Required Trace Fields

Every subagent call must include:
- `trace_id`: Unique identifier for the entire orchestration session
- `span_id`: Unique identifier for this specific subagent call
- `parent_span_id`: The orchestrator's span ID (for fan-in/fan-out reconstruction)

**Format**: OpenTelemetry-compatible for integration with standard observability tools.

### What to Log Per Subagent Call

- Request payload (goal, constraints, budget)
- Response (status, tokens_used, risks)
- Latency (request → response)
- Retry count
- Merge decision (if fan-out: which results were used, which dropped)

---

## Anti-Patterns

- **Shared context between agents** — mutable shared state causes contamination, race conditions, debugging nightmares
- **No budget limits per subagent** — a single subagent can exhaust the entire token/cost budget
- **Trusting subagent output without validation** — schema validation and untrusted wrapping are mandatory
- **Fan-out without merge strategy** — results from parallel subagents are lost or inconsistently combined
- **No trace_id propagation** — impossible to debug orchestration issues, correlate logs, or audit decisions
- **Orchestrator's full context passed to subagent** — unnecessary token cost, contamination risk, injection surface
- **No failure policy for required subagents** — orchestrator hangs waiting for a dead subagent
- **Same model for all subagents** — waste of budget. Route simple subagents to cheaper models
