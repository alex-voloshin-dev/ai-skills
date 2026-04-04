# Prompt Technique Guide: Agentic and Advanced Methods

## 1. Tree of Thoughts

Use when the model needs to explore several candidate approaches before committing.

Best fit:

- planning
- search
- design alternatives

Guardrails:

- define an evaluation heuristic
- cap breadth and depth
- prune weak branches early

## 2. ReAct

Use when the task requires iterative tool use.

Pattern:

```text
Thought -> Action -> Observation -> Next decision
```

Rules:

- keep tool descriptions precise
- constrain the available toolset
- define tool failure handling
- cap loop count

## 3. Prompt Chaining

Use when the work naturally decomposes into validated stages.

Rules:

- one objective per stage
- validate intermediate outputs
- pass only the minimum context forward
- keep every stage retryable

## 4. Reflection

Use when the first draft is often nearly correct but needs explicit critique.

Pattern:

1. generate
2. critique against named criteria
3. revise

Reflection is useful for code generation, long-form writing, and review flows.

## 5. Step-Back Prompting

Use when the model gets lost in details and needs principle-first reasoning.

Good fit:

- policy questions
- domain reasoning
- architecture tradeoffs

## 6. Skeleton-of-Thought

Use for long outputs where speed matters and sections can be expanded independently.

Pattern:

1. generate outline
2. expand sections in parallel
3. merge and normalize

## 7. RAG Prompt Design

Use when the answer must be grounded in retrieved evidence.

Rules:

- tell the model to use only provided context
- separate context from instructions with hard delimiters
- require explicit fallback when context is insufficient
- attach source metadata for citations

## 8. Meta-Prompting

Use when you have an eval dataset and need systematic optimization at scale.

Requirements:

- a measurable objective
- a stable baseline
- held-out evaluation data

## 9. Capability and Provider Guidance

Reasoning models:

- keep prompts short and testable
- emphasize verification over decorative reasoning instructions

Large-context models:

- still curate aggressively
- keep critical constraints at the start and key evidence near the end

Tool-using models:

- move safety into tool schemas and runtime validation
- expose when not to use a tool

Provider notes:

- Anthropic: XML tags work well
- OpenAI: structured outputs and function schemas are strong defaults
- Gemini: long-context synthesis is useful but still needs curation
- Open models: formatting sensitivity is higher, so test exact prompt shape

## Composition Patterns

- RAG + CoT for grounded reasoning
- ReAct + Reflection for tool-driven correction loops
- Few-shot + Constrained generation for format reliability
- Chaining + Self-consistency for high-stakes workflows
