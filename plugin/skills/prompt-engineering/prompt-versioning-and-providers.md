# Prompt Versioning and Provider Patterns

Companion to `prompt-template-patterns.md`. Covers prompt registry schema, canary deployment, semantic diff for prompt reviews, and provider-specific template adaptations.

## Prompt Registry & Versioning

Treat prompts as **versioned production artifacts** — like any other config that affects system behavior.

### Registry Schema (per prompt version)

Store these fields for every prompt version in your prompt management system:

```json
{
  "prompt_id": "support-agent-v1",
  "version": 12,
  "hash": "sha256:a1b2c3...",
  "model_family": "claude-sonnet",
  "model_snapshot": "claude-sonnet-4-20250514",
  "template": "...prompt text...",
  "tools": ["search_kb", "create_ticket"],
  "output_schema": {"$ref": "schemas/support-response.json"},
  "owner": "ai-platform-team",
  "change_summary": "Added citation requirement for policy questions",
  "risk_level": "medium",
  "golden_set_id": "eval-set-support-v3",
  "eval_scores": {
    "task_success": 0.94,
    "faithfulness": 0.91,
    "parse_success": 0.99
  },
  "created_at": "2025-11-15T10:00:00Z",
  "deployed_at": null,
  "deployment_tag": "staging",
  "rollback_reason": null
}
```

### Canary Deployment Pattern

Roll out prompt changes gradually — never 0→100%:

1. **5% canary** — deploy to small traffic slice, monitor for 1-4 hours
2. **25% rollout** — expand if metrics hold, monitor for 4-24 hours
3. **100% GA** — full deployment after all gates pass

**Gate metrics** (must not degrade vs baseline):
- Hallucination / ungrounded-claim rate
- Schema / tool-call error rate
- Latency p95 and token cost deltas
- Task success rate (from eval golden set)

**Automatic rollback triggers**: Any gate metric degrades > threshold → revert to previous version automatically. Log `rollback_reason` in the registry.

### Semantic Diff (for prompt change reviews)

Textual diffs miss behavioral changes. Add an **LLM-based semantic diff** step for every prompt change:

Ask the diff model:
1. "Which **instructions** changed?" (added, removed, modified)
2. "Which **constraints** were added or removed?"
3. "What new **failure modes** might this change introduce?"

Store the semantic diff alongside the Git diff. Include in PR reviews for prompt changes. Flag changes that remove constraints or add new tool permissions as **high-risk**.

## Provider-Specific Patterns

### Anthropic (Claude)

- Prefers XML tags for structure (`<thinking>`, `<answer>`, `<context>`)
- System prompt is a dedicated parameter — use it for role + rules
- Supports prefilling: start the assistant's response to steer format
- Long system prompts are handled well — detailed instructions work

### OpenAI (GPT-4o)

- Native `response_format: { type: "json_schema", ... }` for structured outputs
- Function calling / tool use with JSON Schema validation
- System → Developer → User message hierarchy
- `temperature: 0` for deterministic outputs

### Google (Gemini)

- Supports system instructions as dedicated parameter
- Native multimodal — images, video, audio in prompts
- Very large context windows — effective for many-document synthesis
- Tool use via function declarations

### Open Source (Llama, Mistral, Qwen)

- More sensitive to prompt format — test exact wording and delimiters
- May need more few-shot examples than frontier models
- Grammar-based constrained generation available (GBNF in llama.cpp, Outlines, Guidance)
- Chat templates vary per model — use the model's native template format
- Lower cost per token — good for high-volume, simpler tasks
