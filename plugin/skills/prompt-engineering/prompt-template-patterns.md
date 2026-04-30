# Prompt Template Patterns

Reusable patterns for structuring prompts. Covers delimiter conventions, system prompt architecture, few-shot formatting, output schema design, and provider-specific adaptations.

## Delimiter Conventions

Delimiters separate instructions from data from examples. Critical for both clarity and injection defense.

### Recommended Delimiters by Purpose

| Purpose | Delimiter | Example |
|---|---|---|
| **Sections** (role, context, instructions) | XML tags | `<system>`, `<context>`, `<instructions>` |
| **Data blocks** (user input, documents) | XML tags or triple backticks | `<user_input>...</user_input>`, ` ```...``` ` |
| **Examples** (few-shot) | Numbered with headers | `Example 1:`, `Input:`, `Output:` |
| **Output format** | Code block with schema | ` ```json { ... } ``` ` |
| **Internal reasoning** | XML tags | `<thinking>...</thinking>` |
| **Separators** (between sections) | `---` or blank lines | Visual separation for readability |

### XML Tags — Best Practice

XML tags are the most reliable delimiter for LLMs. They:
- Are unambiguous — clear open/close boundaries
- Nest naturally — `<context><document>...</document></context>`
- Are injection-resistant — attacker must match exact tag names
- Are model-agnostic — all major providers handle XML tags well

```xml
<system>
You are a code reviewer. Follow these rules strictly.
</system>

<instructions>
Review the code below for security vulnerabilities.
Output findings as JSON matching the schema.
</instructions>

<code>
{{user_provided_code}}
</code>

<output_schema>
{"findings": [{"severity": "high|medium|low", "line": int, "issue": "string", "fix": "string"}]}
</output_schema>
```

### Anti-Patterns

- **No delimiters** — instructions and data mixed in plain prose. Injection-prone, hard to parse
- **Inconsistent delimiters** — mixing `###`, `"""`, XML tags randomly. Confuses the model
- **Markdown headers as delimiters** — `## Instructions` looks structural but is weaker than XML for isolation
- **User content inside instruction block** — never concatenate untrusted input with system instructions

## System Prompt Architecture

### Standard Structure

Every system prompt follows this layered architecture:

```
1. ROLE IDENTITY        — Who you are, what you own
2. HARD RULES           — Non-negotiable constraints (always apply)
3. CONTEXT              — Domain knowledge, project specifics
4. INSTRUCTIONS         — What to do for this task type
5. CONSTRAINTS          — What NOT to do, edge cases, boundaries
6. OUTPUT FORMAT        — Schema, structure, examples
7. ERROR HANDLING       — What to do when uncertain or unable
```

### Minimal System Prompt Template

```xml
<role>
You are a [ROLE]. You [KEY_RESPONSIBILITY].
</role>

<rules>
1. [HARD_RULE_1]
2. [HARD_RULE_2]
3. Never [FORBIDDEN_ACTION]
</rules>

<instructions>
For every request:
1. [STEP_1]
2. [STEP_2]
3. [STEP_3]
</instructions>

<output_format>
Respond as JSON:
{
  "field_1": "[TYPE] — [DESCRIPTION]",
  "field_2": "[TYPE] — [DESCRIPTION]"
}
</output_format>

<error_handling>
If you cannot complete the task:
- State what is missing or unclear
- Never fabricate data
- Never guess credentials or URLs
</error_handling>
```

### Layered System Prompt (Multi-Concern)

For complex agents with multiple concerns:

```xml
<identity>
You are a Senior Software Engineer specializing in [STACK].
</identity>

<hard_rules>
1. No git write operations
2. No secrets in code
3. Tests are mandatory for every change
</hard_rules>

<reasoning_protocol>
Before writing code:
1. Understand the goal and constraints
2. Locate affected files and dependencies
3. Design the simplest solution
4. Implement layer by layer
5. Verify with tests
</reasoning_protocol>

<domain_context>
Project: [NAME]
Tech stack: [STACK]
Architecture: [PATTERN]
Key conventions: [CONVENTIONS]
</domain_context>

<response_format>
Structure every response as:
- **Context**: What you found (1-2 sentences)
- **Approach**: Architecture decision and rationale
- **Implementation**: Code with file paths
- **Verification**: Commands to run
</response_format>

<autonomy>
DO without asking: [ACTIONS]
ASK before: [ACTIONS]
NEVER: [ACTIONS]
</autonomy>
```

## Few-Shot Example Formatting

### Standard Format

```
[Task instruction]

<examples>

<example>
<input>[Representative input]</input>
<output>[Desired output]</output>
</example>

<example>
<input>[Edge case input]</input>
<output>[Correct handling of edge case]</output>
</example>

<example>
<input>[Adversarial input]</input>
<output>[Correct rejection/handling]</output>
</example>

</examples>

Now process the following:
<input>{{actual_input}}</input>
```

### Selection Criteria for Examples

1. **Cover the distribution** — typical, edge case, adversarial
2. **Diverse** — different lengths, formats, domains
3. **Correct** — every example must have a verified-correct output
4. **Minimal** — 3-5 examples. More is rarely better
5. **Ordered** — most representative first, edge cases after

### Anti-Patterns

- **All examples are easy** — model learns the easy pattern, fails on hard cases
- **Examples contradict instructions** — model follows examples over instructions
- **Too many examples** — wastes context, marginal quality gains after 5
- **Inconsistent format** — different structure across examples confuses the model

## Output Schema Patterns

### JSON Schema Contract

Always use explicit JSON Schema for machine-consumed outputs:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "required": ["result", "confidence"],
  "additionalProperties": false,
  "properties": {
    "result": {
      "type": "object",
      "description": "The primary output data",
      "additionalProperties": false,
      "properties": {
        "answer": { "type": "string", "description": "The answer to the question" },
        "sources": {
          "type": "array",
          "items": { "type": "string" },
          "description": "Source citations used"
        }
      },
      "required": ["answer"]
    },
    "confidence": {
      "type": "string",
      "enum": ["high", "medium", "low"],
      "description": "Confidence level in the result"
    },
    "error": {
      "type": "object",
      "description": "Present only if the task could not be completed",
      "additionalProperties": false,
      "properties": {
        "code": { "type": "string", "enum": ["insufficient_context", "ambiguous_input", "out_of_scope"] },
        "message": { "type": "string" }
      },
      "required": ["code", "message"]
    }
  }
}
```

### Key Principles

1. **`additionalProperties: false`** — prevents hallucinated fields
2. **`required` fields** — make expectations explicit
3. **`enum` for categories** — constrains to valid values
4. **`description` on every field** — guides the model
5. **Error object** — always include a structured error path
6. **Confidence field** — enables downstream filtering

### Anti-Patterns

- **No schema** — relying on instructions alone for output format. Parse failures spike
- **Missing `additionalProperties: false`** — model invents extra fields
- **No error path** — forces downstream to handle unstructured failures
- **Overly nested schemas** — deep nesting confuses the model. Flatten where possible

## Chain-of-Thought Formatting

### Separated Reasoning

Keep reasoning separate from final output — enables programmatic extraction:

```xml
<thinking>
[Step-by-step reasoning here — not shown to user]
</thinking>

<answer>
[Final structured answer here — this is what gets used]
</answer>
```

### Structured CoT with Checkpoints

```xml
<analysis>
Step 1 — Identify: [what we're looking at]
Step 2 — Evaluate: [assessment against criteria]
Step 3 — Decide: [conclusion with reasoning]
</analysis>

<result>
[Action or answer based on analysis]
</result>
```

### Anti-Patterns

- **Reasoning mixed with output** — no delimiter between thinking and answer. Cannot programmatically extract the result
- **Unstructured CoT** — "think step by step" without specifying what steps. Model rambles
- **CoT for simple tasks** — classification, extraction don't benefit from reasoning steps

## Tool Schema Design

### MCP-Compatible Tool Schema

```json
{
  "name": "search_database",
  "description": "Search the product database by query. Returns top N results sorted by relevance. Use when the user asks about product availability, pricing, or specifications.",
  "inputSchema": {
    "type": "object",
    "required": ["query"],
    "properties": {
      "query": {
        "type": "string",
        "description": "Natural language search query"
      },
      "limit": {
        "type": "integer",
        "default": 5,
        "minimum": 1,
        "maximum": 20,
        "description": "Max results to return"
      },
      "category": {
        "type": "string",
        "enum": ["electronics", "clothing", "home", "all"],
        "default": "all",
        "description": "Product category filter"
      }
    }
  }
}
```

### Tool Description Best Practices

1. **Name**: verb_noun format (`search_database`, `create_file`, `send_email`)
2. **Description**: What it does + when to use it + what it returns
3. **Parameters**: Self-documenting with descriptions, defaults, constraints
4. **Enums**: Use instead of free-text for categorical parameters
5. **Required vs optional**: Mark clearly — reduces ambiguity
6. **Error documentation**: Describe failure modes in tool description

### Anti-Patterns

- **Vague descriptions** — "Does stuff with the database" — model can't decide when to use it
- **No `when to use`** — model must guess the right tool. Selection accuracy drops
- **Free-text for categories** — use enums. Free-text leads to invalid values
- **Missing error docs** — model doesn't know what to do when the tool fails


See [prompt-versioning-and-providers.md](prompt-versioning-and-providers.md) for prompt registry schema, canary deployment, semantic diff, and provider-specific patterns.
