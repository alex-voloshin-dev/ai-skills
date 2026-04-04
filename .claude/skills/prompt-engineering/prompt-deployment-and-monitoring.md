# Prompt Deployment and Monitoring

Companion to `eval-and-testing-guide.md`. Covers context pipeline testing, prompt change deployment (semantic diff, canary rollout), eval tooling, and production monitoring.

## Context Pipeline Testing

Evaluation measures **answer quality**; testing validates **your code**. You need both.

### Unit Tests (fast, deterministic)

- **Retrieval**: Mock vector DB / BM25; use fixture documents; assert top-k contains expected doc_ids
- **Context assembly**: Assert layer order, token caps per layer, dedup applied, `<untrusted_content>` wrappers enforced
- **Memory**: Test write filters, TTL/decay, conflict resolution, conflict-log emissions

### Integration Tests (component wiring)

- Run the full pipeline with fixtures and a stub model
- Assert: `input_tokens ≤ cap`, `max_tool_calls` honored, tool error envelopes emitted, fallbacks triggered

### Adversarial Fixtures (security regression)

- Prompt injection strings inside retrieved docs / tool outputs
- PDF/DOCX with hidden instructions
- Ensure the system refuses instruction override and logs the trigger

Treat these tests like **CI gates** for prompt/context releases.

## Prompt Change Deployment

### Semantic Diff (pre-deployment review)

Textual diffs miss behavioral changes in prompts. Before deploying any prompt change, generate an **LLM-based semantic diff** that answers:

1. "Which **instructions** changed?" (added, removed, modified)
2. "Which **constraints** were added or removed?"
3. "What new **failure modes** might this change introduce?"

Store the semantic diff alongside the Git diff. Include in PR reviews. Flag changes that remove constraints or add tool permissions as **high-risk**.

→ Full pattern and registry schema: `prompt-template-patterns.md` §Prompt Registry & Versioning

### Canary Deployment for Prompts

Never deploy prompt changes to 100% of traffic immediately. Use gradual rollout:

| Stage | Traffic | Duration | Gate |
|---|---|---|---|
| Canary | 5% | 1-4 hours | All metrics within threshold |
| Expansion | 25% | 4-24 hours | No regressions vs baseline |
| GA | 100% | — | All gates passed |

**Gate metrics** (must not degrade vs baseline):
- Hallucination / ungrounded-claim rate
- Schema / tool-call error rate
- Latency p95 and token cost deltas
- Task success rate (from eval golden set)

**Automatic rollback**: If any gate metric degrades > threshold, revert to the previous prompt version. Log `rollback_reason` in the prompt registry.

### Eval Tooling

| Tool | Best For | Link |
|---|---|---|
| **RAGAS** | RAG evaluation: faithfulness, answer relevance, context precision/recall | `docs.ragas.io` |
| **TruLens** | Agent tracing + eval: groundedness, relevance, safety | `trulens.org` |
| **LangSmith** | Prompt management, versioning, tracing, eval datasets | `docs.langchain.com/langsmith` |
| **Langfuse** | Open-source prompt management, tracing, scoring | `langfuse.com/docs` |
| **Braintrust** | Eval framework with prompt playground and scoring | `braintrust.dev` |

Use these alongside custom eval scripts. RAGAS + TruLens are particularly strong for RAG faithfulness evaluation.

## Production Monitoring

### Key Metrics to Track

| Metric | What It Measures | Alert Threshold |
|---|---|---|
| **Task success rate** | % of requests producing correct output | < 90% |
| **Parse success rate** | % of outputs matching expected schema | < 95% |
| **Hallucination rate** | % of outputs with fabricated claims | > 5% |
| **Tool-call correctness** | % of correct tool selections and params | < 85% |
| **Latency p50/p95/p99** | Response time distribution | p95 > 5s |
| **Cost per request** | Token usage × price | > budget × 1.2 |
| **Safety rejection rate** | % of requests triggering safety filters | Monitor trend |
| **User satisfaction** | Thumbs up/down, explicit feedback | < 80% positive |
| **Context utilization** | input_tokens / max_context_window | > 0.7 p95 for 24h |
| **Cache prefix ratio** | cached_tokens / total_input_tokens | < 0.1 sustained |

### Monitoring Setup

1. **Trace every request**: prompt version, model, input tokens, output tokens, latency, tool calls, output
2. **Tag by prompt version**: enables version-level analysis
3. **Automated alerts**: on metric threshold breaches
4. **Weekly review**: trend analysis, error categorization, dataset refresh
5. **Data flywheel**: curate successful interactions → add to eval dataset

### Incident Response

When metrics degrade:

1. **Detect**: Automated alert fires
2. **Isolate**: Which prompt version? Which model? Which input category?
3. **Rollback**: Revert to last known-good prompt version
4. **Diagnose**: Analyze failed cases — new input patterns? Model behavior change? Data quality?
5. **Fix**: Update prompt, add to regression test suite, deploy with eval gate
6. **Postmortem**: Document root cause, add to adversarial eval dataset
