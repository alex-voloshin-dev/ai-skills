# Prompt Technique Guide

Use this file as the entry point for prompt-technique selection. It stays short on purpose; the detailed explanations now live in narrower companion files.

## Decision Tree

```text
Task -> Is it simple and deterministic?
  -> yes: start with zero-shot + output constraints
     -> still unstable: add few-shot
  -> no: does it need explicit reasoning?
     -> yes: use CoT or self-consistency
  -> does it need exploration or tools?
     -> yes: use ReAct, chaining, or ToT
  -> does it need external knowledge?
     -> yes: use RAG with grounded output rules
  -> does it need repeated optimization?
     -> yes: use eval-first iteration and meta-prompting
```

## Technique Selector

| Need | Start With | Escalate To | Detailed Guide |
|---|---|---|---|
| Extraction, classification, formatting | Zero-shot | Few-shot | `technique-guide-core.md` |
| Multi-step reasoning | Chain-of-Thought | Self-consistency | `technique-guide-core.md` |
| Tool use or agent loops | ReAct | Prompt chaining | `technique-guide-agentic.md` |
| Search or branching plans | Tree of Thoughts | Reflection loop | `technique-guide-agentic.md` |
| External knowledge | RAG | Meta-prompting or routing improvements | `technique-guide-agentic.md` |
| Long-form generation speed | Skeleton-of-Thought | Chaining | `technique-guide-agentic.md` |
| Strict output correctness | Constrained generation | Schema + validation pipeline | `technique-guide-core.md` |

## Rules of Use

1. Start with the simplest viable technique.
2. Add one complexity layer at a time.
3. Measure quality before and after every change.
4. Keep instructions, data, and examples explicitly separated.
5. Move orchestration logic into code when prompt logic becomes hard to audit.

## Companion Files

- `technique-guide-core.md`
  Covers zero-shot, few-shot, CoT, self-consistency, and constrained generation.
- `technique-guide-agentic.md`
  Covers ToT, ReAct, chaining, reflection, step-back prompting, SoT, RAG, meta-prompting, and provider guidance.
