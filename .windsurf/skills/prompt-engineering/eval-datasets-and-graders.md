# Eval Datasets and Graders

## Dataset Composition

Every eval dataset should include:

- typical cases
- edge cases
- adversarial cases
- regression cases

Suggested sizes:

| Stage | Size |
|---|---|
| Rapid iteration | 10-20 |
| Pre-deployment | 50-100 |
| Production benchmark | 200+ |

## Dataset Design Rules

- seed from real anonymized usage when possible
- label with ground truth
- version datasets instead of editing them in place
- keep a held-out set to avoid optimizing only for the eval slice

## Common Grader Types

### Exact Match

Use for classification and deterministic extraction.

### Contains or Regex

Use when certain facts must appear but formatting can vary.

### Schema Validation

Use for JSON or other structured outputs.

### Semantic Similarity

Use when wording can vary but meaning must stay equivalent.

### LLM-as-Judge

Use for nuanced quality dimensions such as completeness, tone, or faithfulness. Provide an explicit rubric and calibrate against human review.

### Human Review

Use for subjective or safety-critical outputs and for judge calibration.

## Grader Selection Matrix

| Measurement Goal | Preferred Grader |
|---|---|
| Classification accuracy | Exact match |
| Required facts present | Contains or regex |
| Output format validity | Schema validation |
| Flexible meaning match | Semantic similarity |
| Completeness, tone, quality | LLM-as-judge |
| Safety-critical quality | Human review plus LLM-as-judge |
| Tool-call correctness | Exact match on tool name and parameters |

## Evaluation Dimensions Worth Separating

- answer relevance
- faithfulness to retrieved evidence
- citation correctness
- tool-call correctness
- parse success
- safety rejection quality

Do not collapse all of those into one score.
