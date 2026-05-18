---
name: prompt-engineering
description: Use this skill when designing prompts, building AI features, or auditing LLM security — a prompt engineering knowledge base covering technique taxonomy, template patterns, the OWASP LLM Top 10 security checklist, eval frameworks, structured output contracts, and cost optimization.
disable-model-invocation: true
---

# Prompt Engineering

Comprehensive prompt engineering knowledge base. Provides actionable patterns, checklists, and guides for designing, securing, evaluating, and optimizing LLM prompts and agent systems.

## When to Use

- Designing or reviewing prompt templates (system, developer, user prompts)
- Building tool calling schemas and structured output contracts
- Evaluating prompt quality — accuracy, safety, cost, latency
- Auditing LLM security against OWASP LLM Top 10
- Designing multi-agent orchestration and handoff protocols
- Optimizing prompt cost and latency
- Creating or reviewing Claude Code AI assets (rules, workflows, skills — all are prompts)
- Authoring or auditing a plugin skill — frontmatter spec, body length, progressive disclosure, scripts, eval (see `skill-authoring-spec.md`) or a mis-triggering / fuzzy description (see `optimizing-descriptions.md`)
- Setting up prompt versioning and observability

## When NOT to Use

- Implementing backend/frontend code (use `Agent(software-engineer)` + stack-specific role)
- Infrastructure and deployment (use `Agent(devops-engineer)`)
- Writing code tests (use `Agent(qa-engineer)` + `test-strategy` skill)
- Content writing (use `Agent(content-writer)`)
- Context pipeline design, memory engineering, agent harness, RAG architecture, multi-agent orchestration, production AI checklists → use `context-engineering` skill

## Key Concepts

### Prompt as System

A prompt is not a string — it is a **system** composed of:
1. **Instruction hierarchy**: System prompt > Developer prompt > User prompt > Retrieved content
2. **Context assembly**: What enters the context window, in what order, with what priority
3. **Output contract**: Schema, format, constraints, error handling, fallback behavior
4. **Tool interface**: Available tools, their schemas, permissions, composition patterns
5. **Guard rails**: Safety filters, refusal policies, output validators
6. **Versioning**: Immutable versions, deployment tags, audit trail

### Core Principles

1. **Eval-first**: Define how to measure before changing anything
2. **Simplest technique**: Zero-shot → few-shot → CoT → chaining. Escalate only when simpler fails
3. **Explicit over implicit**: Spell out constraints, output format, edge cases. Never assume the model "knows"
4. **Separation of concerns**: Instructions vs data vs examples — always delimited
5. **Grounding**: Prefer citations and verifiable data over unanchored claims
6. **Least privilege**: Minimal tool permissions per agent. HITL for high-impact actions
7. **Cost awareness**: Every token costs money and time. Compress, cache, route

## Resource Files

| File | Contents |
|---|---|
| `technique-guide.md` | Full technique taxonomy with decision tree, examples, and anti-patterns |
| `prompt-template-patterns.md` | Delimiter conventions, system prompt structure, few-shot formatting, CoT triggers, output schema patterns |
| `security-checklist.md` | OWASP LLM Top 10 mapped to prompt-level mitigations with checklist |
| `eval-and-testing-guide.md` | Eval frameworks, grader types, dataset curation, A/B testing, regression gates |
| `prompt-versioning-and-providers.md` | Version-control patterns for prompts, prompt registry layout, provider differences (Anthropic / OpenAI / Google / open-source), portability tradeoffs |
| `prompt-deployment-and-monitoring.md` | Production rollout patterns — staged release, canary, rollback, observability, cost/latency monitoring, drift detection, on-call runbook hooks |
| `advanced-techniques-and-models.md` | Advanced techniques (self-consistency, tree-of-thought, ReAct, reflection) and model-specific patterns (Claude reasoning vs OpenAI, Gemini long context, Haiku/Sonnet/Opus selection) |
| `skill-authoring-spec.md` | Cached agentskills.io digest — skill specification (frontmatter/naming/dirs/progressive disclosure), best practices, scripts, and skill-output eval. Read when authoring or auditing a plugin skill |
| `optimizing-descriptions.md` | Cached agentskills.io digest — writing skill `description` triggering surface: imperative phrasing, trigger eval queries, train/val split, optimization loop. Read when a skill is mis-triggering or its description needs tuning |

## Integration

- **Follows rules**: `Agent(prompt-engineer)` (prompt system architecture, security, eval-first quality)
- **Used by workflows**: `/plugin-doctor` (prompt-engineering checks during plugin self-diagnostic), `/develop` and `/feature-dev` (AI features), `/feature-design` (Wave-2 review for AI/LLM systems), `/code-review` (prompt quality review), `/plugin-skill-create` (skill scaffolding follows prompt-engineering patterns)
- **Companion skills**: `context-engineering` skill (context pipeline design, memory engineering, agent harness, RAG architecture, multi-agent orchestration, production checklists), `code-review` skill (review checklists)
- **Collaborates with roles**: `Agent(software-engineer)` (prompt integration), `Agent(qa-engineer)` (prompt regression tests), `Agent(product-manager)` (success metrics)
