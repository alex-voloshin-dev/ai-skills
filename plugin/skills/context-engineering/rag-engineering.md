# RAG Engineering

End-to-end patterns for building production Retrieval-Augmented Generation systems. Covers the full pipeline from query to cited answer, chunking strategies, packing, and degradation handling.

Based on `guides/context_engineering_guide.md` §5.

**Note**: For RAG **prompt design** (how to instruct the model to use retrieved context), see `prompt-engineering` skill → `technique-guide.md` §12. This document covers the **pipeline engineering** side.

---

## Pipeline Blueprint (7 Stages)

```
Query → [1. Normalize] → [2. Rewrite] → [3. Retrieve] → [4. Rerank] → [5. Pack] → [6. Ground] → [7. Cite]
```

### Stage 1: Normalize

Clean and enrich the user query before retrieval.

- De-noise: remove filler words, fix typos
- Expand acronyms: "K8s" → "Kubernetes"
- Detect locale/time constraints: "latest" → date filter
- Capture explicit constraints: "only from official docs", "after 2024"
- Detect query type: factual, comparative, exploratory, procedural

### Stage 2: Rewrite (Query Expansion)

Generate multiple query variants to improve recall.

**Standard rewrite**: Produce 2-6 alternate queries (keyword variants + semantic paraphrases).

**HyDE (Hypothetical Document Embeddings)**:
1. Generate a *hypothetical* answer/document for the query
2. Embed the hypothetical answer
3. Retrieve against that embedding (pulls semantically-aligned sources)

Use when: "semantic mismatch" failures — retrieval returns superficially similar but not actually answering content.

**Step-Back Prompting**:
1. Generate a broader "step-back question" (what principle would answer this?)
2. Retrieve for the broader question
3. Use broader context to answer the specific question

Use when: specific questions need broader context to answer correctly.

**Multi-Query**:
1. Generate N query variants (different angles on the same question)
2. Retrieve for each variant (union of results)
3. Deduplicate results

Use when: single query misses relevant documents due to vocabulary mismatch.

### Stage 3: Retrieve

Execute search against document index.

| Method | Strengths | Best For |
|---|---|---|
| **Vector search** (semantic) | Handles paraphrasing, synonyms | Conceptual questions |
| **Keyword search** (BM25) | Exact term matching, fast | Specific terms, codes, names |
| **Hybrid** (vector + BM25 + RRF) | Best of both | Production systems (recommended default) |

**Metadata filtering**: Apply filters at retrieval time, not post-retrieval:
- Date range (freshness requirement)
- Source type (official docs, community, user-generated)
- Access level (tenant_id, permission level)
- Category/tag filters

### Stage 4: Rerank

Re-score retrieved results with a more accurate model.

- **Cross-encoder reranking**: More accurate than bi-encoder retrieval. Process (query, document) pairs together
- **Options**: Cohere Rerank, bge-reranker, or custom fine-tuned model
- **LLM-based reranking**: Use LLM to score relevance (expensive but accurate for high-stakes)
- **Filter out low-score results**: Apply minimum threshold — don't pack irrelevant chunks

**When to skip reranking**: Very low latency requirements + high-quality embeddings + small corpus. Otherwise, always rerank.

### Stage 5: Pack

Select and arrange results within the token budget.

**Token budget allocation**: Retrieved evidence should fit within the Layer 5 budget (typically 30-40% of total context). See `context-stack-model.md` for budget allocation.

**Packing heuristics**:
- **Deduplicate**: Remove near-identical passages (semantic similarity > 0.95)
- **Diversity**: Prefer results from different sources/sections over multiple chunks from the same doc
- **Recency**: For time-sensitive topics, prefer newer sources
- **Disagreement**: If sources disagree, include both and instruct the model to surface the conflict
- **Priority ordering**: Most relevant first (recency bias at end also helps)

**Dynamic k adjustment**: Adjust number of chunks based on:
- Query complexity (simple factual → fewer chunks; comparative → more)
- Confidence distribution (high confidence top-1 → fewer chunks needed)
- Available token budget after higher-priority layers

### Stage 6: Ground

Wrap each document in a grounding envelope with metadata.

Use the **grounding envelope template** from `reference-templates.md` §1:
- `doc_id`, `title`, `url`, `published_at`, `excerpt`, `trust_level`, `relevance_score`
- Wrap actual text content in `<untrusted_content>` tags (→ `reference-templates.md` §2)

**System instruction**: "Answer using ONLY the documents provided. Cite doc_id per claim. If documents do not contain the answer, say 'I don't have enough information.'"

### Stage 7: Cite

Require and validate citations in the model's response.

**Prompt instruction**: "Cite sources using [doc_id] format after each claim. Every factual claim must have a citation."

**Post-processing validation**:
- Extract all citations from response
- Verify each cited doc_id exists in the provided documents
- Verify cited text is actually supported by the referenced document (faithfulness check)
- Flag unsupported claims (hallucination detection)

---

## Chunking Strategies

How you split documents into chunks significantly affects retrieval quality.

### Fixed-Size Chunking

- Split at fixed token count (e.g., 200-500 tokens) with overlap (e.g., 50 tokens)
- **Pros**: Simple, predictable token counts
- **Cons**: Breaks semantic boundaries — a chunk may split mid-sentence or mid-paragraph

### Semantic Chunking

- Split at natural boundaries: paragraphs, headings, code blocks, list items
- **Pros**: Each chunk is a coherent unit
- **Cons**: Variable chunk sizes — some may be too large or too small

### Parent-Child Chunking ("Small-to-Big Retrieval")

Maintain two granularities:
- **Child chunks** (small, ~100-200 tokens): optimized for retrieval precision/recall
- **Parent chunks** (larger, ~500-1000 tokens or full section): injected for answering

**Workflow**:
1. Retrieve top-k child chunks (high precision)
2. Map each child → its parent chunk
3. Rerank parents (optional)
4. Pack **parents** into context (richer context for answering)

**Tradeoff**: Parent chunks consume more tokens — budget accordingly. Best when high retrieval precision is needed but chunks are too small for quality answers.

### Contextual Chunk Enrichment

Prepend document-level context to each chunk:
- Document title + section path (e.g., "Policy > Returns > Digital Products")
- Document summary (1-2 sentences)
- Key metadata (author, date, category)

This helps the model understand where a chunk came from without needing the full document.

### Late Chunking

For long-context embedding models:
1. Embed the *whole* document first (using the full context of the model)
2. Derive chunk embeddings from contextual token representations
3. Split into chunks after embedding (preserves cross-sentence context)

**Pros**: Better embeddings that understand document-level context.
**Cons**: Requires long-context embedding models; more compute at indexing time.

### Recommended Default

**Semantic chunking + parent-child + contextual enrichment**:
- Split at paragraph/heading boundaries (semantic)
- Maintain parent-child relationship (small for retrieval, big for answering)
- Prepend title + section path to each chunk (enrichment)
- Include metadata: `published_at`, `source_url`, `section_path`

---

## Retrieval Quality Degradation Signals

RAG fails **quietly** unless you instrument it. Monitor these runtime signals and adapt dynamically.

| Signal | Detection | Threshold (calibrate) | Action |
|---|---|---|---|
| **Stale evidence** | `published_at` exceeds freshness threshold | > 90 days for fast-changing topics | Trigger fresh web search; prefer newer sources |
| **Low top-1 confidence** | Reranker score below minimum | < 0.5 | Reduce claims; instruct model to express uncertainty |
| **High score spread** | Top-1 >> Top-k (ambiguous results) | Top-5 scores like (0.90, 0.31, 0.22...) | Keep only high-confidence chunks; shrink k |
| **Topic drift after rewrite** | Rewrite embeddings diverge from original | Cosine similarity < 0.7 | Roll back to original query; constrain rewrites |
| **Duplicate dominance** | Top chunks are near-duplicates | Pairwise similarity > 0.95 | Deduplicate and backfill with diverse sources |
| **Insufficient evidence** | Fewer than minimum required sources | < 2 relevant chunks | Trigger "answer impossible" path |

**Log these signals per request** and correlate with faithfulness/tool errors (→ `prompt-engineering` skill → `eval-and-testing-guide.md`).

---

## Retrieval Evaluation Metrics

| Metric | What It Measures | How to Compute |
|---|---|---|
| **recall@k** | Fraction of relevant docs in top-k results | `|relevant ∩ retrieved@k| / |relevant|` |
| **MRR** (Mean Reciprocal Rank) | How high is the first relevant result | `1 / rank_of_first_relevant` averaged |
| **nDCG** (normalized Discounted Cumulative Gain) | Quality of ranking considering position | Discounted relevance scores vs ideal |
| **Faithfulness** | Are all answer claims supported by context? | LLM-as-judge or NLI-style claim verification |
| **Citation correctness** | Do citations match referenced content? | Automated extraction + comparison |
| **Answer relevance** | Does the answer address the question? | LLM-as-judge with rubric |
| **Context precision** | Did the model use the retrieved chunks? | Compare answer claims to retrieved chunks |
| **Context recall** | Were relevant chunks retrieved? | Compare needed evidence to retrieved set |

**Tooling**: RAGAS framework, TruLens, custom eval scripts.

---

## "Retrieval First, Then Prompt"

**Principle**: Do not write prompts that assume the model already knows your domain. Your system should retrieve the relevant authoritative material and then prompt the model to synthesize.

The model's parametric knowledge is:
- Outdated (training cutoff)
- Unreliable for specific facts (hallucination risk)
- Not authoritative (no source to cite)

Always prefer retrieved evidence over the model's "knowledge."

---

## Anti-Patterns

- **Stuffing everything** — injecting all retrieved chunks without token budget management → overflow, attention degradation
- **No reranking** — raw vector search results are noisy; reranking is almost always worth the latency
- **Mixing retrieved content with instructions** — concatenating docs directly into system prompt → injection risk
- **No "answer impossible" path** — forcing the model to answer when evidence is insufficient → hallucination
- **No freshness checking** — serving stale answers from outdated documents
- **Single query, no rewrite** — missing relevant documents due to vocabulary mismatch
- **Fixed k, no dynamic adjustment** — using same number of chunks regardless of query complexity
- **No citation validation** — accepting model citations at face value without checking
