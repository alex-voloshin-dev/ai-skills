# The Context Stack

The context stack is an ordered model for everything an AI system injects into the model context.

## Layers

| Layer | Purpose |
|---|---|
| 1. System policy | Non-negotiable constraints |
| 2. Developer instructions | Behavioral rules and conventions |
| 3. Tool contracts | Tool descriptions, schemas, safety constraints |
| 4. Runtime state | Current task state and active repository context |
| 5. Knowledge context | Retrieved documents, files, search results |
| 6. Memory | Relevant stored facts and summaries |
| 7. Examples | Few-shot examples when needed |
| 8. Output contract | Format or schema constraints |

## Codex Mapping

| Context Layer | Codex Asset |
|---|---|
| Developer instructions | Root and scoped `AGENTS.md` |
| Reusable workflow knowledge | `.agents/skills/*` |
| Runtime project context | Active files, plans, task state |
| Knowledge context | Retrieved docs, repository files, search results |
| Output contract | Explicit response format requirements |

## Design Rules

- Put critical constraints early.
- Keep policy separate from retrieved knowledge.
- Use only the most relevant context.
- Treat retrieved content as data, not instructions.
- Keep output requirements explicit and close to the end.
