# Prompt Template Contracts

## Output Schemas

Use explicit schemas for machine-consumed outputs.

Rules:

- require critical fields
- use enums where possible
- set `additionalProperties: false`
- define a structured error object
- add field descriptions to guide the model

## Tool Schema Design

Tool schemas should say:

- what the tool does
- when to use it
- when not to use it
- what parameters are required
- what failures look like

Prefer narrow, well-described tools over large vague toolsets.

## Prompt Registry and Versioning

Treat prompts like versioned runtime configuration.

Track:

- prompt id and version
- model family or snapshot
- tool set
- output schema
- owner
- change summary
- risk level
- eval results
- rollout state

Use semantic diff review for prompt changes so reviewers can see behavioral changes, not only text diffs.

## Provider-Specific Patterns

- Anthropic: XML tags and structured sections work well
- OpenAI: structured outputs and function schemas are strong defaults
- Gemini: long-context synthesis is useful but still needs strict curation
- Open models: formatting sensitivity is higher, so test the exact prompt shape
