---
name: docs-pack
description: Generate user-facing documentation pack (README, API reference, runbook, tutorial) for a module or feature. Distinct from the `docs` knowledge skill — `docs-pack` produces git-versioned user docs while `docs` is general documentation guidance. Use for onboarding users, API documentation, or operational procedures.
context: fork
argument-hint: "<path> [--template api-reference|user-guide|runbook|architecture] [--audience developer|operator|user]"
---

# /docs-pack — User-Facing Documentation Pack

Generate a coherent set of user-facing docs for a module or feature. Output goes to `<repo>/docs/<module>/` (versioned in git, NOT in `.ai-assets-memory/`) — same convention exception as `/feature-design` per Round 4 N6.

## When to use

- Onboarding users to a feature: `/docs-pack ./features/auth --type user-guide --audience user`
- API documentation: `/docs-pack src/api --template api-reference --audience developer`
- Operational runbook: `/docs-pack ./services/payment --template runbook --audience operator`
- Architecture overview: `/docs-pack . --template architecture --audience developer`

## Not for

- Internal technical docs (ADRs, design decisions) → use internal wiki / `docs` skill
- Code comments, docstrings → IDE / language-native tools
- Marketing copy or blog posts → `/content-creation` (B12 MERGE)

## Invocation

```
/docs-pack src/api --template api-reference
/docs-pack ./features/auth --type user-guide
/docs-pack . --template architecture --audience developer
```

## Arguments

| Flag | Default | Effect |
|---|---|---|
| `<path>` (positional) | required | Directory or file to document |
| `--template` | auto-detect | `api-reference`, `user-guide`, `runbook`, `architecture` |
| `--audience` | `developer` | `developer`, `operator`, `user` |

## Output (Round 4 N6 convention exception)

Files written to **`<repo>/docs/<module>/`** — versioned in git as project documentation:

- `README.md` — overview + quick-start
- `API-REFERENCE.md` (if applicable) — endpoint/function docs
- `RUNBOOK.md` (if operational) — procedures, troubleshooting
- `EXAMPLES.md` — code examples, use cases
- (Optional) Mermaid diagrams for flows / architecture

Memory writes (workflow run logs) go to L4 `.ai-assets-memory/docs/<module>/` separately.

## Agent roster

| Agent | Model | Effort | Tools | Role |
|---|---|---|---|---|
| `content-writer` | inherit | medium | Read, Grep, Glob, Write | Writes documentation from code + examples |
| `subject-matter-expert` (per-stack) | inherit | medium | Read, Bash, Grep | Technical review, accuracy check |
| `seo-engineer` (if public-facing) | inherit | low | Read, Write | GEO/SEO optimization pass per `geo-content` rule + `geo-writer` skill |

## Pipeline

```
┌─ content-writer:
│  - Read source code, docstrings, tests
│  - Extract examples
│  - Generate documentation per template
│  → Draft docs in <repo>/docs/<module>/
│
├─ subject-matter-expert (per-stack):
│  - Review accuracy, completeness, runnability of examples
│  - Suggest improvements
│  → feedback.md (in .ai-assets-memory/docs/<module>/)
│
├─ content-writer revisions:
│  └─ Address feedback, finalize
│
├─ (If --audience = user OR public-facing) seo-engineer:
│  └─ Apply @geo-writer (structure pass) + @humanizer (voice pass) per geo-content + humanize-content rules
│
└─ Memory write: L4 generation summary
   Report: docs location + update reminder
```

No RALF — docs generated in one pass with optional reviewer pass.

## G7 spawn payloads

content-writer, SME, and seo-engineer spawns use structured G7 payloads per `plugin/schemas/spawn-payload.schema.json`. Returns validated against `plugin/schemas/return-contract.schema.json`.

## Eval rubric

Pointer: `plugin/eval/judge-rubrics/docs-pack.md` (B10).

Dimensions:
1. **Completeness** — all key concepts documented per template
2. **Clarity** — examples are runnable, explanations clear
3. **Accuracy** — matches actual code behavior (verified by SME)
4. **Organization** — logical flow, easy to navigate
5. **Style consistency** — follows `docs` skill style guide + `geo-content` rule (if public-facing)

Pass: avg ≥ 4.0, no dimension < 3.

## Memory writes

| Layer | When | Shape |
|---|---|---|
| L4 | After complete | `.ai-assets-memory/docs/<module>/generation-summary.md` — what was documented, when, audience, files emitted |

## Failure modes

- **Source code poorly documented (no docstrings, no tests):** content-writer infers from code + flags as `[INFERRED — needs review]` in the doc
- **API changed since docs written (re-run scenario):** SME catches; content-writer updates affected sections
- **Examples don't run:** content-writer tests examples; fixes or removes broken ones; flags as `[EXAMPLE TESTED]` for those that pass
- **Public-facing flag set but no `marketing/MARKETING.md`:** seo-engineer warns about missing brand context; uses generic GEO defaults

## Observability events

- `workflow_start` — docs-pack + path + template
- `agent_spawned` × 2–3 (content-writer, sme, optional seo-engineer)
- `workflow_end` — `COMPLETE` with file count

## Integration

- **Orchestrator**: `feature-design-lead`
- **Schemas**: `plugin/schemas/spawn-payload.schema.json`, `plugin/schemas/return-contract.schema.json`
- **Companions**: `/subagent-spawn`, `/context-load`
- **Knowledge skills**: `docs` (general writing patterns), `geo-writer` (GEO structure pass), `humanizer` (voice pass), `content-creation` (B12 MERGE — if marketing/blog overlap)
- **Rules**: `subagent-isolation`, `untrusted-content-wrapping` (G1 wrap on source code reads), `geo-content` (if public-facing — mandatory per rule), `humanize-content` (mandatory for public-facing per rule), `memory-discipline`
- **Hooks**: `tool-output-normalize.py` (G2 on extracted code samples)
