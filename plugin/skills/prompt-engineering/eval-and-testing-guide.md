# Prompt Eval and Testing Guide

Framework for evaluating and testing prompts. Covers eval dataset design, grader types, regression gates, A/B testing, and continuous monitoring.

## Eval-First Principle

**Never deploy a prompt change without defining how to measure its impact.**

Every prompt change requires:
1. **Baseline metrics** — current performance on the eval dataset
2. **Eval dataset** — representative inputs with expected outputs
3. **Graders** — automated or human scoring functions
4. **Regression criteria** — what must NOT get worse
5. **Success criteria** — what must improve and by how much

## Eval Dataset Design

### Dataset Size Guidelines

| Stage | Min Size | Composition |
|---|---|---|
| **Rapid iteration** | 10-20 | Core scenarios + edge cases |
| **Pre-deployment** | 50-100 | Full distribution + adversarial |
| **Production benchmark** | 200+ | Statistically significant sample |

### Dataset Composition

Every eval dataset must include:

1. **Typical cases** (60%) — representative of actual usage distribution
2. **Edge cases** (20%) — boundary conditions, unusual inputs, empty inputs, very long inputs
3. **Adversarial cases** (10%) — injection attempts, prompt extraction, hallucination probes
4. **Regression cases** (10%) — known past failures that were fixed

### Dataset Format

```json
{
  "id": "eval-001",
  "category": "typical|edge|adversarial|regression",
  "input": {
    "user_message": "What is the refund policy for digital products?",
    "context": "[retrieved documents if RAG]",
    "conversation_history": "[prior turns if multi-turn]"
  },
  "expected": {
    "output": "Digital products can be refunded within 14 days...",
    "output_schema_valid": true,
    "tools_called": ["search_knowledge_base"],
    "contains": ["14 days", "refund"],
    "must_not_contain": ["I don't know", "as an AI"],
    "sentiment": "helpful",
    "grounding": "all claims cited"
  },
  "metadata": {
    "created": "2025-01-15",
    "source": "production_log",
    "priority": "high"
  }
}
```

### Dataset Curation Process

1. **Seed from production** — sample real user queries (anonymized, PII removed)
2. **Augment with edge cases** — manually craft boundary conditions
3. **Add adversarial** — use red-team test cases from `security-checklist.md`
4. **Label with ground truth** — expert-reviewed expected outputs
5. **Version the dataset** — track changes over time. Never modify in-place
6. **Split**: 80% eval / 20% held-out test — prevent overfitting to eval set

## Grader Types

### 1. Exact Match

**When**: Classification, extraction, yes/no questions.

```python
def exact_match(expected, actual):
    return expected.strip().lower() == actual.strip().lower()
```

**Pros**: Deterministic, fast, cheap.
**Cons**: Fragile — fails on paraphrasing, formatting differences.

### 2. Contains / Regex Match

**When**: Output must include specific information but format may vary.

```python
def contains_all(expected_phrases, actual):
    return all(phrase.lower() in actual.lower() for phrase in expected_phrases)

def regex_match(pattern, actual):
    return bool(re.search(pattern, actual))
```

**Pros**: More flexible than exact match. Still deterministic.
**Cons**: May miss semantic equivalents.

### 3. Schema Validation

**When**: Structured outputs (JSON, XML). Verifies format compliance.

```python
def schema_valid(schema, actual):
    try:
        parsed = json.loads(actual)
        jsonschema.validate(parsed, schema)
        return True
    except (json.JSONDecodeError, jsonschema.ValidationError):
        return False
```

**Pros**: Catches structural issues (missing fields, wrong types).
**Cons**: Doesn't validate semantic correctness of content.

### 4. Semantic Similarity

**When**: Output meaning matters more than exact wording.

```python
# Libraries: sentence-transformers (embed), sklearn.metrics.pairwise (cosine_similarity)
def semantic_similarity(expected, actual, threshold=0.85):
    expected_emb = embed(expected)  # e.g., SentenceTransformer("all-MiniLM-L6-v2").encode()
    actual_emb = embed(actual)
    similarity = cosine_similarity(expected_emb, actual_emb)
    return similarity >= threshold
```

**Pros**: Handles paraphrasing.
**Cons**: Embedding quality varies. Threshold tuning needed.

### 5. LLM-as-Judge

**When**: Complex quality assessment. Nuance, tone, completeness.

```
You are an expert evaluator. Score the following response on a scale of 1-5:

<criteria>
- Accuracy: Are all facts correct?
- Completeness: Does it address all parts of the question?
- Clarity: Is it well-structured and easy to understand?
- Safety: Does it avoid harmful content?
</criteria>

<question>{{question}}</question>
<expected_answer>{{expected}}</expected_answer>
<actual_answer>{{actual}}</actual_answer>

Score each criterion 1-5 and provide brief justification.
Output as JSON: {"accuracy": N, "completeness": N, "clarity": N, "safety": N, "justification": "..."}
```

**Pros**: Handles nuanced quality. Scales better than human review.
**Cons**: Non-deterministic. Judge model may have biases. Costs money.

**Best practices for LLM-as-Judge**:
- Use a stronger model as judge than the model being evaluated
- Provide explicit rubric — not just "rate quality"
- Include reference answer for comparison
- Run judge multiple times and average for stability
- Calibrate against human ratings

### 6. Human Review

**When**: Subjective quality, safety-critical outputs, judge calibration.

**Process**:
1. Sample outputs for review (stratified by confidence/category)
2. Provide rubric with examples of each score level
3. Multiple reviewers per sample (inter-annotator agreement)
4. Track reviewer consistency over time

**Pros**: Gold standard for quality.
**Cons**: Slow, expensive, doesn't scale.

## Grader Selection Matrix

| What to Measure | Grader | When |
|---|---|---|
| Classification accuracy | Exact match | Always |
| Required information present | Contains | Always |
| Output format compliance | Schema validation | Structured outputs |
| Answer quality (paraphrasing OK) | Semantic similarity | Flexible outputs |
| Nuanced quality (tone, completeness) | LLM-as-Judge | Complex outputs |
| Safety, edge cases | Human review + LLM-as-Judge | High stakes |
| Tool call correctness | Exact match on tool name + params | Agentic |
| Hallucination rate | LLM-as-Judge with "verify claims" rubric | RAG, factual |

## Regression Testing

### Regression Gate Rules

Before deploying any prompt change:

1. **No regression on existing metrics** — accuracy, parse rate, safety score must not decrease
2. **Threshold**: Allow ≤2% regression on non-critical metrics if primary metric improves ≥5%
3. **Zero tolerance**: Safety and security metrics must never regress
4. **Statistical significance**: For A/B tests, require p < 0.05 on primary metric

### Regression Test Suite Structure

```
eval/
├── datasets/
│   ├── core-v1.json          # Main eval dataset (versioned)
│   ├── adversarial-v1.json   # Security/safety cases
│   └── regression-v1.json    # Known past failures
├── graders/
│   ├── schema_grader.py
│   ├── semantic_grader.py
│   └── llm_judge.py
├── baselines/
│   └── prompt-v2.3-results.json  # Baseline metrics for comparison
└── run_eval.py                # Eval runner script
```

## A/B Testing

### When to A/B Test

- Major prompt rewrites (not minor wording changes)
- Model version upgrades (GPT-4 → GPT-4o)
- New technique adoption (adding CoT, switching to chaining)
- Changes affecting >10% of production traffic

### A/B Test Protocol

1. **Hypothesis**: "Prompt B will improve [metric] by [X%] over Prompt A"
2. **Primary metric**: One metric that defines success
3. **Guardrail metrics**: Metrics that must not regress (safety, cost, latency)
4. **Sample size**: Calculate required sample for statistical power (typically 1000+ per variant)
5. **Duration**: Run for ≥7 days to capture daily/weekly patterns
6. **Analysis**: Statistical significance test (chi-squared for rates, t-test for means)
7. **Decision**: Ship if primary metric improves significantly AND guardrails hold

### A/B Test Checklist

- [ ] Hypothesis documented
- [ ] Primary metric defined
- [ ] Guardrail metrics defined
- [ ] Sample size calculated
- [ ] Random assignment verified
- [ ] Monitoring dashboard set up
- [ ] Rollback plan ready
- [ ] Statistical analysis completed before decision

## Faithfulness vs Citation Correctness

These are **distinct** eval dimensions — don't confuse them:

| Dimension | Question | How to Measure |
|---|---|---|
| **Faithfulness** | Are ALL claims in the answer supported by retrieved context? | LLM-as-judge or NLI-style claim verification against evidence |
| **Citation correctness** | Does each [Source N] actually match the content it references? | Extract citations → compare to source text |
| **Answer relevance** | Does the answer address the user's question? | LLM-as-judge with rubric |
| **Context precision** | Did the model actually *use* the retrieved chunks? | Compare answer claims to retrieved chunks |
| **Context recall** | Were relevant chunks retrieved at all? | Compare needed evidence to retrieved set |

A system can "cite" a source yet still hallucinate extra details not supported by the cited text. Always evaluate faithfulness separately from citation.

**Caveat**: LLM judges can show *positional bias* (preferring the first draft). Mitigate by shuffling candidate order and using blinded evaluation prompts.

## Context Health Metrics

Beyond standard production metrics, track these **derived ratios** as context pipeline health signals (→ `context-engineering` skill):

| Metric | Formula | What a Rising Trend Means | Alert Threshold |
|---|---|---|---|
| `context_utilization` | `input_tokens / max_context_window` | Agent approaching overflow | > 0.7 for 24h (p95) |
| `cache_prefix_ratio` | `cached_tokens / total_input_tokens` | Stable prefix changing (or broken) | < 0.1 sustained |
| `evidence_density` | `evidence_tokens / total_input_tokens` | Retrieval degrading vs fixed overhead | < 0.3 |
| `output_to_input_ratio` | `output_tokens / input_tokens` | Potential goal drift or injection | > 2.0 |

Alert on **trends**, not hard absolutes — calibrate by model and product SLO.

**Silent degradation detection**: Guardrail hooks miss gradual quality decay. Detect via **scheduled eval sweeps** against the live retrieval stack (weekly + on any model/corpus update).


See [prompt-deployment-and-monitoring.md](prompt-deployment-and-monitoring.md) for context pipeline testing, prompt change deployment, eval tooling, and production monitoring.
