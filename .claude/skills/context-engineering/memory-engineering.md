# Memory Engineering

Patterns for managing memory in LLM agent systems. Covers taxonomy, CRUD lifecycle, conflict resolution, compression strategies, and operational best practices.

Based on `guides/context_engineering_guide.md` §6.

---

## Memory Taxonomy

5 distinct memory types. A system may use any combination depending on complexity.

| Type | Scope | Lifetime | Storage | Example |
|---|---|---|---|---|
| **Session memory** | Single conversation | Ephemeral (session end) | In-context / short-term store | Recent messages, current tool outputs |
| **Working memory** | Current task | Ephemeral (task completion) | Structured state blob | Current plan, scratchpad, intermediate results |
| **Long-term memory** | Cross-session | Durable (explicit deletion) | Vector store, key-value DB | User preferences, stable facts, learned patterns |
| **Organizational memory** | Team/org-wide | Durable (versioned) | Knowledge base, wiki, policies | Product specs, policies, KB articles, conventions |
| **Tool-output memory** | Per tool call | Varies (reuse window) | Cache, reference store | Important tool result IDs + summaries (not raw dumps) |

### When to Use Each Type

- **Session**: Always present. Conversation history within current interaction
- **Working**: When agent has multi-step tasks. Store plan, progress, artifacts, assumptions as structured JSON
- **Long-term**: When users interact repeatedly. Store preferences, corrections, facts that persist across sessions
- **Organizational**: When agents operate over shared knowledge. Versioned, curated, not user-specific
- **Tool-output**: When tool results are expensive to re-fetch or needed across turns. Store IDs + summaries, not raw output

---

## Memory CRUD Lifecycle

### Write (Extract → Validate → Enrich → Store)

1. **Extract candidates** from interaction:
   - User-stated preferences ("I prefer TypeScript")
   - Corrections ("actually, the deadline is Friday")
   - Stable facts ("our API uses OAuth2")
   - Important decisions ("we chose PostgreSQL over MySQL because...")

2. **Validate** before storing:
   - Is this stable information (not transient)?
   - Does it contain sensitive data (PII, credentials)? → reject or redact
   - Is user intent clear? If ambiguous, confirm before storing
   - Is it a duplicate of existing memory? → merge instead of create

3. **Enrich** with metadata:
   ```json
   {
     "key": "preferred_language",
     "value": "TypeScript",
     "source": "user_stated",
     "confidence": 0.95,
     "created_at": "2025-11-15T10:30:00Z",
     "last_confirmed_at": "2025-11-15T10:30:00Z",
     "scope": {"level": "project", "tenant_id": "org-abc", "project_id": "proj-123"},
     "tags": ["preference", "tech_stack"]
   }
   ```

4. **Store** in appropriate backend:
   - Structured key-value for preferences and facts
   - Vector store for semantic retrieval of complex memories
   - Never store raw conversation transcripts as memory

### Read (Retrieve → Filter → Rank → Inject)

1. **Retrieve** potentially relevant memories based on current context
2. **Filter** by scope: `tenant_id`, `user_id`, `session_id`, `project_id` — server-side enforcement
3. **Rank** by composite score: `relevance × confidence × recency_weight`
4. **Inject** top-k into context at Layer 6 of the context stack

**Recency weighting formula** (starter heuristic — calibrate per domain):

```
recency_weight(days_old) = 1 / (1 + log(1 + days_old))
```

Where `days_old` = days since `last_confirmed_at`.

### Update (Merge → Resolve → Version)

1. **Check for existing memory** on the same key/topic (semantic dedup)
2. **Merge**: update value, bump `last_confirmed_at`, adjust `confidence`
3. **Resolve conflicts** if contradiction detected (see Conflict Resolution below)
4. **Version**: keep history of changes for audit trail

### Delete (User-Requested | TTL Expiry | Decay)

- **User-requested**: immediate deletion from all stores (raw records + vector embeddings)
- **TTL expiry**: memories with `last_confirmed_at` older than TTL threshold
- **Confidence decay**: memories whose score drops below threshold for N consecutive days
- **Archival**: before deletion, optionally move to cold storage with pointer

---

## Conflict Resolution

When memory entries contradict (e.g., two preferences, two "facts"), resolve deterministically and **always log the decision**.

### Priority Order

1. **Prefer user-explicitly-stated** over model-inferred (unless user later corrects)
2. **Prefer higher confidence** — if `Δconfidence ≥ 0.2`, take the higher one
3. **Prefer more recently confirmed** over merely "created recently" (`last_confirmed_at` > `created_at`)
4. **If still ambiguous**: ask the user once, then persist the resolution

### Conflict Log (required)

Every conflict resolution must produce a log entry:

```json
{
  "memory_key": "preferred_database",
  "winner_id": "mem-456",
  "loser_id": "mem-123",
  "reason": "user_stated_override",
  "timestamp": "2025-11-15T10:35:00Z",
  "trace_id": "trace-abc-789"
}
```

### Edge Cases

- **Same user contradicts themselves**: prefer the more recent statement. Update existing memory, don't create duplicate
- **Model infers vs user states**: user statement always wins, even if model inference had higher "confidence"
- **Organizational vs personal**: personal memory overrides organizational for that user, unless organizational is marked as policy (non-overridable)

---

## Context Compression Strategies

When conversation + artifacts + tool outputs exceed the context window, use controlled compression — never truncate blindly.

### Strategy 1: Summarization Rollups (Structured)

Compress older conversation turns into a **structured rollup** that preserves decisions, constraints, and open issues:

```json
{
  "rollup": {
    "turn_range": "1-20",
    "goal": "Implement user authentication with OAuth2",
    "decisions": [
      {"topic": "auth_provider", "decision": "Google OAuth2", "date": "2025-11-10"},
      {"topic": "session_storage", "decision": "Redis with 24h TTL", "date": "2025-11-10"}
    ],
    "constraints": ["Must support mobile SSO", "No third-party cookie dependency"],
    "completed": ["OAuth2 flow implemented", "Token refresh working"],
    "open_questions": ["Should we support SAML for enterprise?"],
    "artifacts": [
      {"id": "file-auth-service", "type": "code", "path": "src/auth/service.ts"}
    ]
  }
}
```

**When to trigger**: After every N turns (e.g., 20), or when conversation tokens exceed 60% of context budget for Layer 6.

### Strategy 2: Selective Forgetting (Decay + Archiving)

Score memory items and archive low-value ones:

```
score = relevance_to_current_goal × confidence × recency_weight
```

**Thresholds** (calibrate per domain):
- Archive when `score < 0.15` for 7 consecutive days AND item not referenced in last N sessions
- Below archive threshold, move to long-term storage (vector store) and keep only a pointer + 1-sentence summary in active memory

### Strategy 3: Artifact Externalization

Move large intermediate results out of context:

- **Large tool outputs** (tables, logs, API responses) → external storage, keep `ID + 1-2 sentence summary` in context
- **Generated code files** → save to filesystem, keep `path + description` in context
- **Analysis results** → save as artifact, keep `conclusion + key metrics` in context

**Rule**: if a single item exceeds 500 tokens in context, consider externalizing it.

---

## Memory as Data Product

Treat memory as a **data product** with engineering rigor:

### Schema + Versioning
- Define explicit schema for memory items (fields, types, allowed values)
- Version the schema — migration plan when schema evolves
- Never store unstructured blobs without metadata

### Audits
- Periodic review for staleness (items not confirmed in N days)
- Check for contradictions (conflicting memories on same topic)
- Scan for sensitive data leakage (PII, credentials that slipped through write filters)

### Impact Measurement
- Measure accuracy/safety deltas **with and without** memory enabled
- Track: does memory improve task success rate? Reduce user corrections?
- If memory doesn't measurably improve outcomes, simplify or remove

### Access Control
- RBAC for traces and memory (they can contain sensitive data)
- Purpose separation: memory for support ≠ billing ≠ personalization
- Audit trail: who read/wrote/deleted which memory items

---

## Anti-Patterns

- **Unbounded memory growth** — no TTL, no cleanup, no compression → context overflow
- **Free-text blobs** — storing raw conversation chunks without structure or metadata → poor retrieval
- **No conflict resolution** — contradictory memories coexist → model gets confused
- **Memory injection without filtering** — dumping all memories into context → token waste, noise
- **No user controls** — user can't view, edit, or delete their memories → compliance risk
- **Storing transient data as memory** — "the weather is nice today" is not a memory → noise
- **No scope enforcement** — memories leak across tenants/users → privacy violation
- **Storing raw tool outputs** — 4000-token API responses stored verbatim → use summaries + IDs
