# Prompt Technique Guide: Core Methods

## 1. Zero-Shot

Use when the task is simple, deterministic, and easy to constrain.

Pattern:

```text
[task]
[output constraints]
[input]
```

Best practices:

- make the output contract explicit
- use enums or fixed labels when possible
- state edge-case behavior
- add negative constraints when extra prose is harmful

## 2. Few-Shot

Use when zero-shot is close but not reliably shaped.

Best practices:

- use 3-5 diverse examples
- cover typical, edge, and adversarial cases
- keep formatting identical across examples
- prefer high-quality examples over many examples

Skip few-shot if structured outputs already solve the problem with zero-shot quality.

## 3. Chain-of-Thought

Use for reasoning-heavy tasks where the model benefits from an explicit path.

Best practices:

- define the reasoning structure instead of only saying "think step by step"
- separate reasoning from the final answer
- avoid CoT for trivial extraction and classification tasks

## 4. Self-Consistency

Use when accuracy matters more than cost and multiple reasoning paths are plausible.

Pattern:

1. generate several independent reasoning paths
2. extract the final answers
3. vote or compare for stability

Good fit:

- math
- logic
- high-stakes analysis

Poor fit:

- deterministic extraction
- formatting tasks

## 5. Constrained Generation

Use when downstream systems require exact structure.

Preferred constraints:

- JSON Schema
- tool/function schemas
- enums
- grammar-based outputs when supported

Rules:

- use `additionalProperties: false`
- describe every field
- define an explicit structured error path
- test empty, long, and adversarial inputs

## Quick Anti-Patterns

- adding CoT to trivial tasks
- packing dozens of few-shot examples into the prompt
- relying on prose-only formatting instructions when schema constraints are available
- escalating to complex techniques before measuring whether the simple version already works
