# Advanced Techniques and Model-Specific Prompting

Companion to `technique-guide.md`. Covers RAG prompt design, meta-prompting, model-capability-type adaptations, provider considerations, and technique composition.

## RAG Prompt Design

**When**: Model needs external knowledge. Real-time data. Domain-specific information.

**Pattern**:
```
[System instructions]

Use ONLY the following context to answer. If the context doesn't contain 
the answer, say "I don't have enough information."

<context>
[Retrieved documents with source citations]
</context>

[User question]

Cite sources using [Source N] format.
```

**Best practices**:
- Always instruct: "Use only the provided context" — reduces hallucination
- Include source metadata (title, URL, date) for citation
- Order chunks by relevance — most relevant first
- Set a context budget — don't stuff the entire retrieval result
- Add "if not in context, say so" to prevent fabrication
- Separate retrieved content from instructions with clear delimiters

**Anti-pattern**: Mixing retrieved content with system instructions — injection risk. Always delimit.

## Meta-Prompting / DSPy

**When**: Prompt optimization at scale. Automated prompt tuning. Production systems with eval datasets.

**Approach**:
- Define objective function (eval metric)
- Generate prompt candidates (manual or LLM-generated)
- Evaluate candidates on held-out dataset
- Iterate: select best → mutate → evaluate
- Tools: DSPy, PromptBreeder, APE (Automatic Prompt Engineer)

**Best practices**:
- Requires a good eval dataset (≥50 examples with ground truth)
- Start with manual prompts, then optimize — don't start from random
- Monitor for overfitting to eval set — hold out a test set

**Anti-pattern**: Automated optimization without a solid manual baseline — optimizers amplify flaws in weak starting prompts and eval datasets.

## Model-Capability-Type Prompting

Beyond provider differences, adapt prompts based on the **model's capability type** — the same model family can behave differently depending on which capability you're leveraging.

### Reasoning Models (o1, o3, DeepSeek-R1, QwQ)

- Keep instructions **short and testable** — reasoning models can over-think verbose prompts
- Emphasize **verification** ("validate schema", "cite evidence", "check constraints") over step-by-step prescriptions
- Push complex control logic into **code** (routers, validators, tool harness) — don't encode it in the prompt
- Cap "thinking" tokens explicitly where the API supports it (can be substantial and expensive)
- Minimize few-shot — reasoning models often perform better zero-shot with clear constraints
- For output token budgets, see `context-engineering` skill → `agent-harness-patterns.md` §3

### Large-Context Models (Gemini 1.5/2.5 1M+, Claude 200K)

- Still benefit from **curation** — long context can reduce effective recall ("context rot")
- Keep critical constraints near the **top** (stable prefix) and key evidence near the **end** (tail pack)
- Apply the **"lost-in-the-middle"** principle: don't hide must-follow requirements in the middle of long contexts
- Use **cacheable prefix design**: group static content first, dynamic content after (→ `context-engineering` skill)
- For multi-document tasks, order by relevance — most relevant first and last
- Monitor `context_utilization` metric — approaching window limit degrades quality before hitting it

### Tool-Using Models (GPT-4o+tools, Claude+tools, Gemini+tools)

- Make tool contracts **explicit**: schemas, failure modes, retries — don't rely only on natural language descriptions
- Enforce tool safety **server-side** (validation + permissions), not only in prompt text
- Use `additionalProperties: false` and `enum` in tool schemas to constrain parameters
- Include "when NOT to use" guidance in tool descriptions — prevents false positive tool calls
- Fewer, well-described tools > many vague tools — selection accuracy drops with 50+ tools
- For tool result handling, see `context-engineering` skill → `agent-harness-patterns.md` §5 and `reference-templates.md` §4

## Model-Provider Considerations

| Provider | Key Differences |
|---|---|
| **OpenAI (GPT-4o)** | Native JSON mode, function calling, structured outputs. Strong at following complex instructions. Temperature 0 for deterministic tasks |
| **Anthropic (Claude)** | XML tags for structure, `<thinking>` for CoT. Longer context windows. Strong at nuanced reasoning. Follows system prompts precisely |
| **Google (Gemini)** | Large context windows (1M+ tokens). Native multimodal. Good at synthesis across many documents. Implicit caching (2.5+) |
| **Open source (Llama, Mistral)** | More sensitive to prompt format. May need more examples. Grammar-based generation available. Lower cost |

## Technique Composition

Techniques compose naturally:

- **RAG + CoT**: Retrieve context → reason through it step by step
- **ReAct + Reflection**: Act → observe → critique → adjust approach
- **Few-shot + Constrained**: Examples show format → schema enforces it
- **Chaining + Self-Consistency**: Each chain step uses majority vote for reliability
- **SoT + Parallelism**: Generate skeleton → expand points in parallel API calls
