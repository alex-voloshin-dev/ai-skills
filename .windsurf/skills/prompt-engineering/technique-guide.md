# Prompt Technique Guide

Comprehensive taxonomy of prompt engineering techniques. Use the decision tree to select the simplest effective approach. Escalate complexity only when simpler methods fail.

## Decision Tree

```
Task → Is the task simple (extraction, classification, formatting)?
  ├─ YES → Zero-Shot with output constraints (schema, enum, regex)
  │         └─ Not working? → Add few-shot examples (3-5 diverse)
  └─ NO → Does it require reasoning?
           ├─ Single-step reasoning → Chain-of-Thought (CoT)
           │   └─ High stakes? → Self-Consistency (multiple CoT + majority vote)
           ├─ Multi-step with exploration → Tree of Thoughts (ToT)
           ├─ Needs tool use → ReAct (reason + act + observe loop)
           ├─ Complex, decomposable → Prompt Chaining (sequential sub-prompts)
           └─ Needs self-correction → Reflection (generate + critique + revise)

Quality not sufficient?
  ├─ Output format issues → Constrained Generation (grammar/regex/schema)
  ├─ Missing context → RAG (retrieve → augment → generate)
  ├─ Wrong abstraction level → Step-Back Prompting (abstract first)
  ├─ Slow generation → Skeleton-of-Thought (parallel outline → fill)
  └─ Scale optimization needed → Meta-Prompting / DSPy
```

## Technique Catalog

### 1. Zero-Shot

**When**: Simple extraction, classification, formatting, transformation.

**Pattern**:
```
[Clear task instruction]
[Output constraints: format, schema, enum values]
[Input data]
```

**Best practices**:
- Be explicit about output format — never assume the model knows
- Use enums for classification: "Classify as one of: positive, negative, neutral"
- Add negative constraints: "Do NOT include explanations. Output ONLY the JSON."
- Specify edge cases: "If the input is empty, return null"

**Anti-pattern**: Adding CoT or examples to simple tasks — wastes tokens, adds latency, no quality gain.

### 2. Few-Shot

**When**: Output style or format needs demonstration. Model makes consistent mistakes in zero-shot.

**Pattern**:
```
[Task instruction]

Example 1:
Input: [representative input]
Output: [desired output]

Example 2:
Input: [edge case input]
Output: [desired output for edge case]

Example 3:
Input: [adversarial input]
Output: [correct handling]

Now process:
Input: [actual input]
Output:
```

**Best practices**:
- 3-5 examples minimum. Include: typical case, edge case, adversarial case
- Diverse examples — cover the distribution, not just easy cases
- Consistent formatting — identical structure across all examples
- Order matters: place most representative examples first
- Label quality matters more than quantity — every example must be correct

**Dynamic example selection** (preferred for production systems):
1. Maintain a curated **example library** — input→output pairs tagged by task type and output contract version
2. At request time, retrieve **top-k most similar** examples via embedding search over the library
3. Pack only examples that fit the **remaining token budget** after evidence (Layer 5) is packed
4. Re-evaluate the library periodically — stale examples can contradict current output contracts

**Negative examples** ("what NOT to do") are often more effective for format compliance than additional positive examples. Include 1-2 showing common mistakes and their correct alternatives.

**When to skip few-shot entirely**: For instruction-tuned models with strict output schema (JSON Schema, structured outputs), zero-shot often matches few-shot quality with fewer tokens. Run an A/B eval — if few-shot yields < ~2% quality gain, remove it and reclaim tokens for evidence. See `context-engineering` skill → `context-stack-model.md` Layer 7 for budget guidance.

**Anti-pattern**: Dozens of similar examples — the model learns the pattern from 3-5. More examples waste context.

### 3. Chain-of-Thought (CoT)

**When**: Complex reasoning, math, multi-step logic, causal analysis.

**Trigger phrases**:
- "Think step by step before answering"
- "Show your reasoning, then provide the final answer"
- "Break this problem into steps"
- "Let's work through this systematically"

**Pattern**:
```
[Task instruction]

Think step by step:
1. First, identify [what]
2. Then, analyze [what]
3. Based on the analysis, determine [what]
4. Finally, provide your answer in this format: [format]

[Input data]
```

**Best practices**:
- Specify the reasoning structure — don't just say "think step by step"
- Separate reasoning from final answer with a clear delimiter
- For extraction tasks: CoT in a `<thinking>` block, final answer outside
- Zero-shot CoT works well for strong models (GPT-4, Claude 3.5+). Weaker models need few-shot CoT

**Anti-pattern**: CoT for simple tasks (classification, extraction) — adds latency with no accuracy gain.

### 4. Self-Consistency

**When**: High-stakes accuracy. No single clear reasoning path. Math, logic, code analysis.

**Pattern**:
1. Generate N independent CoT paths (N=5-10, temperature > 0)
2. Extract final answer from each path
3. Majority vote or weighted vote on final answers

**Best practices**:
- Useful when CoT alone is unreliable — variance across paths indicates uncertainty
- Cost scales linearly with N — use only for high-value decisions
- Can be implemented as parallel API calls for speed

**Anti-pattern**: Self-consistency for deterministic tasks — majority vote adds nothing when the answer is obvious.

### 5. Tree of Thoughts (ToT)

**When**: Planning, search, multi-branch exploration. Creative problem-solving with backtracking.

**Pattern**:
1. Generate multiple candidate approaches (breadth)
2. Evaluate each approach (scoring or heuristic)
3. Expand most promising branches (depth)
4. Backtrack from dead ends
5. Select best path

**Best practices**:
- Use for problems with clear evaluation criteria (can you score partial solutions?)
- Combine with domain-specific heuristics for pruning
- Set a depth limit to control cost

**Anti-pattern**: ToT for linear tasks — the branching overhead is waste when there's one clear path.

### 6. ReAct (Reasoning + Acting)

**When**: Agentic tasks requiring tool use. Information gathering. Multi-step workflows.

**Pattern**:
```
Thought: [What I need to do and why]
Action: [tool_name(parameters)]
Observation: [tool result]
Thought: [What the result means, what to do next]
Action: [next tool call or final answer]
```

**Best practices**:
- Keep tool descriptions concise but complete — the model uses them for planning
- Include error handling in tool schemas — what happens on failure
- Limit available tools per task — fewer tools = better selection accuracy
- Set maximum iteration limits to prevent infinite loops
- Log all thought-action-observation triples for debugging

**Anti-pattern**: Giving agents 50+ tools — selection accuracy drops. Keep toolsets focused per task.

### 7. Prompt Chaining

**When**: Complex task with clear sub-steps. Need intermediate validation. Pipeline processing.

**Pattern**:
```
Step 1: [Extract/Transform] → validate output → 
Step 2: [Analyze/Enrich] → validate output → 
Step 3: [Synthesize/Format] → final output
```

**Best practices**:
- Each step has a single, clear objective
- Validate intermediate outputs before passing to next step
- Use cheaper/faster models for simple steps, powerful models for complex steps
- Pass minimal context between steps — only what the next step needs
- Design for retry: each step should be idempotent

**Anti-pattern**: Chaining when a single well-structured prompt would suffice — adds latency and failure points.

### 8. Reflection / Self-Critique

**When**: Quality improvement. Error correction. Tasks where initial output is often "almost right."

**Pattern**:
```
Step 1 — Generate:
[Produce initial response to the task]

Step 2 — Critique:
Review your response against these criteria:
- [Criterion 1]
- [Criterion 2]
- [Criterion 3]
List specific issues found.

Step 3 — Revise:
Fix all identified issues. Produce the final version.
```

**Best practices**:
- Provide explicit critique criteria — don't just say "review your answer"
- Can be single-pass (generate→critique→revise in one prompt) or multi-pass (separate API calls)
- Works well for code generation, writing, analysis
- Diminishing returns after 2-3 reflection rounds

**Anti-pattern**: Reflection without criteria — the model says "looks good" and changes nothing.

### 9. Step-Back Prompting

**When**: Model gets lost in details. Needs to abstract before answering. Complex domain questions.

**Pattern**:
```
Before answering the specific question, first answer this higher-level question:
[Abstracted/generalized version of the question]

Then use that understanding to answer the original question:
[Original specific question]
```

**Best practices**:
- Force the model to identify the underlying principle before applying it
- Useful for physics, law, medicine — domains where principles govern specifics
- Combine with CoT for best results

**Anti-pattern**: Step-back on concrete, well-defined tasks — the abstraction step adds latency without improving answers that don't require principle-level reasoning.

### 10. Skeleton-of-Thought (SoT)

**When**: Long-form generation where speed matters. Parallel content creation.

**Pattern**:
```
Step 1: Generate an outline with N key points (skeleton)
Step 2: Expand each point independently (can be parallelized)
Step 3: Combine into final output
```

**Best practices**:
- Points in the skeleton should be independent — enables true parallelism
- Each expansion call gets only its point + minimal global context
- Good for: documentation, reports, blog posts, comprehensive analyses

**Anti-pattern**: SoT for short responses or tightly coupled content — parallelism breaks when points depend on each other.

### 11. Constrained Generation

**When**: Output must conform to a strict format. Parsing reliability is critical.

**Methods**:
- **JSON Schema**: Force output to match a schema (OpenAI structured outputs, Anthropic tool use)
- **Grammar-based**: GBNF grammars (llama.cpp), regex constraints (Outlines, Guidance)
- **Enum/Choice**: Restrict to predefined options
- **Template filling**: Provide template with blanks to fill

**Best practices**:
- Always prefer schema-based constraints over instructions alone
- Use `additionalProperties: false` in JSON Schema — prevents hallucinated fields
- Include `description` fields in schema properties — guides the model
- Test with edge cases: empty input, very long input, adversarial input

**Anti-pattern**: Over-constraining creative or exploratory outputs — rigid schemas kill the model's ability to surface unexpected insights.

### 12. RAG Prompt Design

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

### 13. Meta-Prompting / DSPy

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
