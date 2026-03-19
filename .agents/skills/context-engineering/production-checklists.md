# Production AI Checklists

8 checklists for production readiness of AI/LLM systems. All 8 must pass before production deployment of AI features. Items marked N/A require documented justification.

Based on `guides/context_engineering_guide.md` §11.

---

## 1. Context Design Checklist

- [ ] Layers are separated: policy vs instructions vs knowledge vs memory
- [ ] Every dynamic insert has provenance metadata (source, timestamp, confidence)
- [ ] Token budget is explicit and enforced per layer
- [ ] Position effects applied: critical constraints at beginning (L1-2), output contract at end (L8)
- [ ] Output format contract is strict (JSON Schema / structured outputs)
- [ ] Model uncertainty handling is specified ("say 'unknown' + ask for data")
- [ ] Few-shot examples dynamically selected (or justified why static)
- [ ] Cacheable prefix designed: static content (L1-3) grouped first, dynamic appended after
- [ ] Context overflow strategy defined: which layers truncate first, which are protected
- [ ] No "lost-in-the-middle" pattern: must-follow requirements not buried in long sections

## 2. RAG Checklist

- [ ] Retrieval pipeline documented: normalize → rewrite → retrieve → rerank → pack → ground → cite
- [ ] Hybrid retrieval or strong lexical fallback exists (vector + BM25)
- [ ] Reranking is enabled (cross-encoder or LLM-based) or justified why not
- [ ] Chunking strategy defined: size, overlap, semantic boundaries, parent-child if applicable
- [ ] Deduplication and diversity packing exist
- [ ] Grounding envelopes used for all retrieved documents (doc_id, title, url, published_at, excerpt)
- [ ] Citations are required and validated post-generation
- [ ] Retrieval degradation signals instrumented:
  - [ ] Stale evidence (published_at exceeds freshness threshold)
  - [ ] Low top-1 confidence (reranker score below threshold)
  - [ ] High score spread (top-1 >> top-2, ambiguous results)
  - [ ] Topic drift after query rewrite
  - [ ] Duplicate dominance (near-duplicate top chunks)
- [ ] Dynamic k adjustment implemented or justified why not
- [ ] SLO degradation ladder defined (latency thresholds → reduce k → skip reranking → lexical fallback)
- [ ] "Answer impossible" path exists: model says "insufficient context" when evidence is lacking

## 3. Memory Checklist

- [ ] Memory taxonomy defined: which types are used (session, working, long-term, organizational, tool-output)
- [ ] Memory schema defined and versioned (structured key/value with metadata, not raw transcripts)
- [ ] Write filters prevent sensitive or transient data from being stored
- [ ] Every memory item has metadata: `source`, `created_at`, `last_confirmed_at`, `scope`, `confidence`
- [ ] TTL / decay policy exists: stale memories are expired or downweighted
- [ ] Conflict resolution is deterministic and logged:
  1. Prefer user-asserted over model-inferred
  2. Prefer higher confidence (Δ ≥ 0.2)
  3. Prefer more recently confirmed
  4. If ambiguous, ask once and persist resolution
- [ ] Context compression strategy exists for growing history:
  - [ ] Summarization rollups for old conversation turns
  - [ ] Selective forgetting based on relevance × confidence × recency score
  - [ ] Artifact externalization (large outputs → external storage + pointer)
- [ ] User deletion pathway exists (right to be forgotten)
- [ ] Multi-tenant scoping: `tenant_id` in retrieval filters and memory scope

## 4. Security Checklist (OWASP 2025 Aligned)

→ Primary reference: `prompt-engineering` skill → `security-checklist.md` (full OWASP LLM Top 10 mapping)

**Context engineering additions**:
- [ ] All 5 defense layers implemented (not just one):
  1. Input sanitization (clean/normalize before insertion)
  2. Context isolation (untrusted wrappers, delimiter separation)
  3. Model-level rules (system prompt safety instructions)
  4. Output validation (schema check, sanitization before downstream use)
  5. Side-effect controls (HITL, tool permissions, rate limits)
- [ ] Untrusted content wrapper used for ALL external data:
  - [ ] Retrieved documents (RAG)
  - [ ] Tool outputs
  - [ ] User-uploaded files
  - [ ] Web search results
- [ ] Multimodal injection defense:
  - [ ] PDF/DOCX: hidden/white text stripped, metadata cleaned
  - [ ] Images: OCR output wrapped as untrusted
  - [ ] CSV/JSON: instruction-like strings in cells not echoed raw into context
- [ ] Prompt leakage defenses: no secrets in prompts, server-side auth enforcement
- [ ] Vector DB protected against poisoning and exfiltration (write access restricted, provenance tracked)
- [ ] Tool privileges are least-privilege and scoped per task
- [ ] Prompt injection test suite runs in CI (direct, indirect, multimodal, multi-turn escalation)

## 5. Evaluation Checklist

→ Companion reference: `prompt-engineering` skill → `eval-and-testing-guide.md` (graders, A/B testing, regression gates)

**Context engineering additions**:
- [ ] Golden set covers happy path + edge cases + adversarial (≥50 examples)
- [ ] Retrieval evals exist and monitored: recall@k, MRR, nDCG
- [ ] Faithfulness eval: are all claims supported by retrieved context? (separate from citation correctness)
- [ ] Citation correctness eval: does each [Source N] match the content it references?
- [ ] Context health metrics tracked (alert on **trend over time window**, not single-point thresholds):
  - [ ] `context_utilization` = input_tokens / max_context_window (alert: p95 > 0.7 for 24h)
  - [ ] `cache_prefix_ratio` = cached_tokens / total_input_tokens (alert: p95 < 0.1 for 24h)
  - [ ] `evidence_density` = evidence_tokens / total_input_tokens (alert: p95 < 0.3 for 24h)
  - [ ] `output_to_input_ratio` = output_tokens / input_tokens (alert: p95 > 2.0 for 24h)
- [ ] Prompt-injection tests run in CI
- [ ] Observability dashboards exist for token/latency/error rates
- [ ] Scheduled eval sweeps configured (weekly + on model/corpus update) to detect silent degradation
- [ ] LLM-as-judge evals use **positional bias mitigation**: shuffle candidate order, use blinded evaluation prompts, run each judgment twice with swapped positions
- [ ] Context pipeline tests exist:
  - [ ] Unit: context assembly, token budget enforcement, memory filtering
  - [ ] Integration: end-to-end pipeline with fixtures and stub model
  - [ ] Adversarial: injection strings in retrieved docs, PDFs with hidden instructions

## 6. Agent Harness Checklist

- [ ] Init vs continuation prompt separation designed
- [ ] Structured state representation for continuations (JSON blob with goal, plan, artifacts, assumptions)
- [ ] Token budget tracked per layer per turn (prefix, state, evidence, conversation)
- [ ] Input AND output token limits set per request type
- [ ] Tool output normalized before injection:
  - [ ] Size-capped (truncate to token budget)
  - [ ] Key information extracted / summarized if oversized
  - [ ] Wrapped as untrusted data with metadata (tool_name, call_id, timestamp, status)
- [ ] Tool error envelopes use typed `error_type` vocabulary:
  `timeout` | `not_found` | `auth_failed` | `rate_limited` | `schema_invalid` | `server_error` | `content_filtered`
- [ ] Loop detection implemented: same (tool, args_hash) repeating N times → stop
- [ ] Failure taxonomy defined and handled:
  - [ ] Context overflow → rollup + reduce k + re-inject constraints
  - [ ] Tool loop → loop breaker + hard caps
  - [ ] Goal drift → re-anchor goal + prune plan
  - [ ] Hallucinated tool args → schema validation + reject + retry with grounding
  - [ ] Injection escape → tighten wrappers + post-call assertions
  - [ ] Cascade failure → circuit breaker + error propagation policy
- [ ] Prompt version logged in every trace
- [ ] Cache hit rate monitored (`cache_prefix_ratio`)
- [ ] Context health metrics monitored: `context_utilization`, `cache_prefix_ratio`, `output_to_input_ratio`

## 7. Multi-Agent Checklist

- [ ] Agent boundaries defined: non-overlapping responsibilities, minimal context per subagent
- [ ] Orchestrator → subagent payload schema defined:
  `trace_id`, `goal`, `constraints`, `state_slice`, `allowed_tools`, `budget` (max_input_tokens, max_output_tokens, max_tool_calls, timeout_ms)
- [ ] Subagent → orchestrator return contract defined:
  `trace_id`, `status` (ok|needs_clarification|failed), `tokens_used`, `result`, `evidence`, `risks`, `next_actions`
- [ ] Per-subagent token/cost budget enforced
- [ ] Global merge budget: Σ(tokens_returned) ≤ merge_budget
- [ ] Subagent outputs tagged as untrusted tool results
- [ ] `trace_id` + `span_id` propagate across orchestrator ↔ subagent calls (OpenTelemetry-friendly)
- [ ] Fan-out merge strategy selected and documented:
  - Union+rerank (retrieval/fact gathering)
  - Best-of (same task, pick highest confidence)
  - Vote/consensus (categorical decisions)
  - Reduce/synthesis (merger subagent combines outputs)
- [ ] Failure handling for fan-out:
  - Optional subagent fails → continue + log
  - Required subagent fails → retry → fallback → fail-fast with typed error
- [ ] Context contamination guardrails:
  - [ ] Subagent output never overwrites orchestrator system instructions
  - [ ] External text from subagents wrapped in `<untrusted_content>`
  - [ ] Orchestrator validates subagent output schema before using

## 8. Privacy & Compliance Checklist

- [ ] Tenant isolation enforced **server-side** at retrieval time, not model-side:
  - [ ] Every vector query filtered by `tenant_id` (namespace-based or metadata filter)
  - [ ] Memory items never retrieved cross-tenant
  - [ ] Prefer namespace-per-tenant for strong isolation
- [ ] Memory scope includes `tenant_id` for multi-tenant deployments
- [ ] Retrieval-time permission checks: never retrieve items the current user cannot access
- [ ] Need-to-know packing: accessible but unnecessary docs not included in context
- [ ] Inference logs treated as potentially personal data:
  - [ ] Minimized and redacted
  - [ ] Retention policy defined
  - [ ] Region-pinned where required
- [ ] User memory review / edit / delete pathway implemented
- [ ] "Right to be forgotten" covers:
  - [ ] Raw records
  - [ ] Vector store embeddings
  - [ ] (Fine-tuning data if applicable — avoid training on personal data without governed process)
- [ ] Data residency requirements mapped to vendor capabilities
- [ ] Purpose separation: memory for support ≠ billing ≠ personalization
- [ ] Trace access control: restrict who can view traces (contain sensitive data), separate retention policies
- [ ] Transparency: log what was retrieved and why

---

## Combined Readiness Gate

All 8 checklists must pass before production deployment of AI features.

**Minimum passing criteria**: All checkbox items either checked or explicitly marked N/A with documented reason.

**Review cadence**:
- **Before launch**: Full review of all 8 checklists
- **On model change**: Re-run checklists 1, 4, 5, 6 (context design, security, eval, agent harness)
- **On corpus update**: Re-run checklists 2, 5 (RAG, eval)
- **Quarterly**: Full review of all 8 checklists for drift
