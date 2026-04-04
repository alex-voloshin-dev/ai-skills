# Prompt Template Patterns

Use this file as the overview for prompt structure patterns. Detailed templates and contracts now live in smaller companion files.

## Prompt Anatomy

Most production prompts should separate:

1. role or identity
2. hard rules
3. task instructions
4. context or data
5. output contract
6. fallback or error path

## Pattern Map

| Need | File |
|---|---|
| Delimiters and prompt sectioning | `prompt-template-foundations.md` |
| System prompt structure | `prompt-template-foundations.md` |
| Few-shot and CoT formatting | `prompt-template-foundations.md` |
| Output schemas and tool schemas | `prompt-template-contracts.md` |
| Prompt registry and versioning | `prompt-template-contracts.md` |
| Provider-specific prompt adjustments | `prompt-template-contracts.md` |

## Default Rules

- separate instructions from untrusted data
- prefer XML tags or other hard delimiters over loose prose
- keep output contracts explicit
- define what failure looks like
- treat prompt changes like versioned config, not ad hoc copy edits
