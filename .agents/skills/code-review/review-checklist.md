# Code Review Checklist

General-purpose review checklist for all code changes. Apply systematically — check every item, mark as pass/fail/N/A.

## Architecture & Design

- [ ] Change aligns with existing architecture patterns
- [ ] No unnecessary coupling between modules/services
- [ ] Responsibilities are correctly assigned (no god classes/functions)
- [ ] Public API surface is minimal and well-defined
- [ ] Breaking changes are documented and versioned
- [ ] Feature flags used for gradual rollout where appropriate

## Code Quality

- [ ] Functions/methods have a single clear responsibility
- [ ] No dead code, unused imports, or commented-out blocks
- [ ] Variable and function names are descriptive and consistent
- [ ] No magic numbers — constants are named and documented
- [ ] Error handling is explicit (no swallowed exceptions)
- [ ] Edge cases are handled (null, empty, boundary values)
- [ ] No code duplication — shared logic is extracted
- [ ] Complexity is reasonable (no deeply nested logic)

## Testing

- [ ] New logic paths have corresponding tests
- [ ] Tests are meaningful (not just asserting true)
- [ ] Edge cases and error paths are tested
- [ ] Tests are deterministic (no flaky tests)
- [ ] Test names describe the scenario being tested
- [ ] Existing tests still pass (no regressions)
- [ ] Integration/E2E tests updated if behavior changed
- [ ] Test coverage does not decrease

## API & Data

- [ ] API contracts are backward-compatible (or versioned)
- [ ] Input validation is present and thorough
- [ ] Database migrations are reversible
- [ ] Queries are optimized (no N+1, proper indexes)
- [ ] Data serialization handles all expected formats
- [ ] Pagination implemented for list endpoints

## Performance

- [ ] No obvious performance regressions (O(n²) where O(n) is possible)
- [ ] Large data sets handled with streaming/pagination
- [ ] Expensive operations are cached where appropriate
- [ ] Async operations used for I/O-bound work
- [ ] No unnecessary memory allocations in hot paths
- [ ] Database queries are efficient (checked with EXPLAIN if needed)

## Documentation

- [ ] Public APIs are documented (parameters, return types, errors)
- [ ] Complex logic has inline comments explaining "why"
- [ ] README updated if setup/usage changed
- [ ] Changelog entry added for user-facing changes
- [ ] Migration guide provided for breaking changes

## Observability

- [ ] Logging added for important operations and errors
- [ ] Log levels are appropriate (ERROR vs WARN vs INFO vs DEBUG)
- [ ] No sensitive data in logs (PII, secrets, tokens)
- [ ] Metrics/traces added for new critical paths
- [ ] Health check endpoints updated if new dependencies added

## Context Engineering (AI/LLM Features)

Apply when the change involves prompts, RAG, agents, memory, or LLM integrations. Mark N/A for non-AI changes.

- [ ] Context stack layers are separated (policy vs knowledge vs examples vs output contract)
- [ ] Token budget enforced per layer — no unbounded context injection
- [ ] Retrieved content and tool outputs wrapped as untrusted data (`<untrusted_content>`)
- [ ] Grounding envelopes used for retrieved documents (doc_id, title, published_at, relevance_score)
- [ ] Memory operations have write filters (no PII/transient data stored), conflict resolution, TTL/decay
- [ ] Tool error envelopes use typed `error_type` vocabulary (→ `context-engineering` skill → `reference-templates.md`)
- [ ] Agent loops have iteration limits, cost caps, and failure mode detection
- [ ] Output schema uses `additionalProperties: false`, `required` fields, confidence/error objects
- [ ] Multi-tenant isolation: retrieval filtered by `tenant_id` server-side
- [ ] Context health metrics tracked: `context_utilization`, `cache_prefix_ratio`, `evidence_density`
- [ ] Prompt version logged in traces for every request
