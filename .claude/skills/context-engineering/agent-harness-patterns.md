# Agent Harness Patterns

Patterns for building reliable, long-running, tool-using LLM agents. Covers initialization, state management, token budgeting, caching, tool normalization, failure modes, and streaming.

Based on `guides/context_engineering_guide.md` §7.

---

## 1. Init vs Continuation Prompts

Use **different prompt structures** for the first turn vs subsequent turns.

### Initialization Prompt (First Turn)

Full context setup:
- Environment rules and safety constraints (L1)
- Role definition and reasoning protocol (L2)
- Tool schemas and permissions (L3)
- Working directory, artifacts, naming conventions
- Logging + trace IDs
- Full task description and constraints

### Continuation Prompt (Subsequent Turns)

Minimal delta — only what changed:
- **State blob** with updated progress (see §2)
- New observations / tool results from last turn
- Active constraints that still apply
- Relevant memory items (filtered, not all)

**Design pattern**: separate **static prefix** (cacheable, rarely changes) from **dynamic suffix** (per-turn state, new observations).

### Checkpoint Pattern

At turn N, summarize progress into structured state → inject as continuation context. This prevents context growth from unbounded conversation accumulation.

**When to checkpoint**:
- Every N turns (e.g., every 5-10 turns)
- When conversation tokens exceed 50% of Layer 6 budget
- Before switching sub-tasks or tools
- After completing a major plan step

---

## 2. State Representation

Use a **structured state blob** (JSON) injected at each turn for agent continuations.

### State Blob Template

```json
{
  "goal": "Implement OAuth2 login with Google provider",
  "constraints": [
    "Must support mobile SSO",
    "No third-party cookie dependency"
  ],
  "plan": [
    {"step": 1, "action": "Create auth service", "status": "done"},
    {"step": 2, "action": "Implement token refresh", "status": "done"},
    {"step": 3, "action": "Add session management", "status": "in_progress"},
    {"step": 4, "action": "Write integration tests", "status": "todo"}
  ],
  "artifacts": [
    {"id": "auth-service", "type": "code", "path": "src/auth/service.ts"},
    {"id": "auth-config", "type": "config", "path": "src/auth/config.ts"}
  ],
  "assumptions": [
    {"text": "Redis available for session storage", "confidence": 0.9},
    {"text": "Google OAuth2 client ID configured", "confidence": 0.7}
  ],
  "budget_remaining": {
    "input_tokens": 24000,
    "output_tokens": 6000,
    "tool_calls": 8
  }
}
```

### State Update Rules

- **Append** new observations to relevant sections
- **Mark steps** as done/in_progress/todo/blocked
- **Decrement** budget counters after each turn
- **Compress** when state exceeds budget: summarize completed steps into a `completed_summary` field, remove detailed entries

### State Compression

When the state blob grows too large:
1. Replace completed step details with a summary: `"completed_summary": "Steps 1-5 done: auth service, token refresh, session mgmt implemented"`
2. Keep only active/pending steps in full detail
3. Archive old artifacts list — keep only currently relevant ones
4. Collapse assumptions that are confirmed into constraints

---

## 3. Token Budgeting Across Turns

Token budgeting has two sides: **input** (context you feed the model) and **output** (tokens the model generates). Both drive cost, latency, and UX.

### Input Budget by Layer

Track token usage per context stack layer per turn:

| Category | What It Tracks | Typical Budget % |
|---|---|---|
| Prefix tokens | System prompt + tools (L1-3) | 15-25% |
| State tokens | Structured state blob (L4) | 5-10% |
| Evidence tokens | Retrieved docs + tool results (L5) | 30-40% |
| Conversation tokens | Recent turns + memory (L6) | 10-20% |
| Examples + output contract (L7-8) | Few-shot + schema | 5-15% |

### Output Budget by Task Type

Set `max_output_tokens` explicitly per request type:

| Task Type | Typical `max_output_tokens` |
|---|---|
| Summarization | 300–600 |
| Q&A / RAG answer | 500–1000 |
| Report / explanation | 800–1500 |
| Code generation (single function) | 1500–2500 |
| Complex analysis | 2000–4000 |

For **reasoning models** (o1, o3, DeepSeek-R1), "thinking" tokens can be substantial. Cap them explicitly where the API supports it.

### Guardrails

- **Hard caps per layer**: never exceed allocated % per category
- **Max tool calls per turn**: typically 3-10 depending on task
- **Max retries per tool**: 2-3 attempts before fallback
- **Loop detection**: if `(tool_name, args_hash)` repeats N times in M steps, stop
- **Total turn budget**: input + output combined should not exceed threshold

### Monitoring

Add `max_output_tokens` (and thinking budget if applicable) to:
- Subagent budget schemas (→ `multi-agent-patterns.md`)
- Per-turn orchestration policies
- Monitoring dashboards (p95 output tokens is a leading indicator of drift)

---

## 4. Context Caching

Most major providers support **prompt/context caching** (prefix reuse of KV states). Proper cache design significantly reduces cost and latency.

### Cacheable Prefix Design

- **Group static content first**: system policy (L1) + developer instructions (L2) + tool schemas (L3)
- **Append dynamic content after**: user request, state, retrieved docs, memory, examples, output contract
- **Never interleave** static and dynamic blocks — breaks cache hit potential

### Provider Support

| Provider | Mechanism | Notes |
|---|---|---|
| Anthropic | Explicit prompt caching API | Mark cache breakpoints |
| OpenAI | Automatic prefix caching, predicted outputs | Longest prefix match |
| Google Gemini | Implicit caching (2.5+), explicit context caching API | Automatic for repeated prefixes |

### Cache Invalidation

- Version bump on rule/role/tool changes → prefix changes → cache miss (expected)
- Track `cache_prefix_ratio = cached_tokens / total_input_tokens`
- **Target**: > 0.3 for cost efficiency
- **Alert**: < 0.1 sustained → prefix is changing too often or poorly designed

### Measurement

Track alongside token/latency metrics:
- Cache hit rate per request type
- Cost savings from caching vs non-cached baseline
- Latency reduction from cache hits

---

## 5. Tool Result Normalization

Raw tool outputs are often too large, noisy, or poorly structured. **Normalize before context injection**.

### Normalization Steps

1. **Extract signal**: keep top-k items and 1-2 sentence excerpts; drop irrelevant fields
2. **Summarize if oversized**: if raw output exceeds token ceiling (e.g., > 1000 tokens), run fast summarization (small model or deterministic heuristics)
3. **Annotate metadata**: tool name, `call_id`, timestamp, confidence/score, truncation flags, token estimates
4. **Wrap as untrusted**: tool outputs are data, not instructions (→ `reference-templates.md` §2)

### Normalized Envelope

```json
{
  "tool": "search_kb",
  "call_id": "tc-456",
  "status": "ok",
  "summary": "3 relevant chunks found on data retention policy",
  "results": [
    {"doc_id": "kb-78", "score": 0.91, "excerpt": "..."},
    {"doc_id": "kb-12", "score": 0.74, "excerpt": "..."}
  ],
  "truncated": true,
  "original_size_tokens": 4200,
  "injected_tokens": 380
}
```

Track `injected_tokens` per tool call as part of token budget accounting.

### For Failed Tool Calls

Use the typed **tool error envelope** (→ `reference-templates.md` §4) with standardized `error_type` vocabulary.

---

## 6. Agent Failure Modes and Detection

Production agents fail in predictable ways. Detect early, mitigate automatically.

| Failure | Symptom | Detection Signal | Mitigation |
|---|---|---|---|
| **Context overflow** | Earlier constraints ignored | Token budget exceeded; constraint re-check fails | Rollup + reduce k; re-inject constraints at top |
| **Tool loop** | Same tool+args called repeatedly | `(tool, args_hash)` repeats N times in M steps | Loop breaker + hard cap on iterations |
| **Goal drift** | Agent deviates from original goal | Plan-step embedding diverges from goal embedding | Re-anchor goal + prune irrelevant plan steps |
| **Hallucinated tool args** | Invented parameters not in state/evidence | Schema validation fails; args not grounded | Reject + retry with explicit grounding instruction |
| **Injection escape** | Untrusted content changes behavior | Behavior diff vs baseline; unexpected policy violations | Tighten wrappers + post-call assertions |
| **Cascade failure** | Subagent error poisons orchestrator state | Error flag not handled; repeated downstream failures | Circuit breaker + error propagation policy |
| **Cost runaway** | Token consumption spiraling across turns | Per-turn cost exceeds threshold; cumulative budget exhausted | Per-turn cost limits + budget remaining in state |

### Implementation

Implement detection as **guardrail hooks** in the agent loop, not as afterthoughts:
- Check after every tool call
- Check after every model response
- Check before injecting tool results into context
- Log all detections with `trace_id` for debugging

---

## 7. Streaming & Incremental Delivery

Streaming changes how you stage context and degrade under latency pressure.

### Pattern A: Two-Pass Answer

1. **Fast pass** (cache-only / small-k): answer quickly using cached prefix + minimal retrieval, clearly labeling uncertainty
2. **Quality pass** (full retrieval + rerank): refine/verify the answer once evidence arrives; update citations and correct mistakes

Best for: user-facing chat where perceived latency matters.

### Pattern B: Speculative Prefill

Start generation with stable prefix + user request while retrieval runs. When retrieval returns:
- Continue with "evidence append" + self-correction instruction, OR
- Restart generation with full evidence if first draft is too weak

Best for: systems where retrieval is the latency bottleneck.

### Pattern C: SLO Degradation Ladder

Define thresholds and deterministic fallbacks:

| Condition | Action |
|---|---|
| Retrieval > 300ms p95 | Reduce k (fewer chunks) |
| Retrieval > 800ms p95 | Skip reranking |
| Retrieval > 1.5s p95 | Lexical-only fallback or cached snippets |
| Retrieval unavailable | Answer from general knowledge (if allowed), otherwise ask for input |

Log which degradation tier was used per request. Track impact on faithfulness and tool errors.

---

## Anti-Patterns

- **No iteration limits** on agentic loops → agent runs forever, burns tokens
- **Raw tool output injected** without size cap or wrapping → context overflow, injection risk
- **No structured state** → agent "forgets" what it already did, repeats work
- **Full system prompt repeated every turn** → no caching benefit, wasted tokens
- **No failure mode handling** → agent hangs or produces garbage silently
- **State blob never compressed** → grows unbounded across turns
- **No output token limits** → model generates 10K tokens for a simple answer
- **Interleaved static/dynamic content** → cache misses, higher cost
