# /docs-pack — Generate user-facing documentation

Coherent set of user docs for a module or feature, written to `<repo>/docs/<module>/` for git versioning.

## When to use

- Onboarding users to a feature: `/docs-pack ./features/auth --type user-guide --audience user`
- API documentation: `/docs-pack src/api --template api-reference --audience developer`
- Operational runbook: `/docs-pack ./services/payment --template runbook --audience operator`
- Architecture overview: `/docs-pack . --template architecture --audience developer`

## Not for

- Internal technical docs (ADRs, design decisions) → use internal wiki / `docs` skill
- Code comments, docstrings → IDE / language-native tools
- Marketing copy or blog posts → [`/content-creation`](feature-design.md)

## How to invoke

```bash
/docs-pack <path> [--template api-reference|user-guide|runbook|architecture] [--audience developer|operator|user]
```

| Flag | Default | Effect |
|---|---|---|
| `<path>` (positional) | required | Directory or file to document |
| `--template` | auto-detect | `api-reference`, `user-guide`, `runbook`, `architecture` |
| `--audience` | `developer` | `developer`, `operator`, `user` |

## What you get

Markdown files in `<repo>/docs/<module>/`:
- `README.md` — overview + quick-start
- `API-REFERENCE.md` (if applicable) — endpoint/function docs
- `RUNBOOK.md` (if operational) — procedures, troubleshooting
- `EXAMPLES.md` — code examples, use cases
- (Optional) Mermaid diagrams for flows / architecture

Output convention: docs go to `<repo>/docs/<module>/` per Round 4 N6 (versioned in git as project documentation), NOT to `.ai-assets-memory/`.

## How it works

1. **content-writer** reads source code, docstrings, tests; extracts examples; generates documentation per template
2. **subject-matter-expert** (per stack) reviews accuracy + completeness; suggests improvements
3. **content-writer revisions** address feedback
4. **(If `--audience user` or public-facing) seo-engineer** applies `@geo-writer` (structure pass) + `@humanizer` (voice pass)
5. **Memory write** — generation summary to L4

No RALF — docs generated in one pass with optional reviewer pass.

## Common questions

**What if the source code is poorly documented?**
content-writer infers from code + tests + flags as `[INFERRED — needs review]` in the doc. You confirm or correct.

**Examples don't run after generation?**
content-writer tests examples; fixes or removes broken ones; flags `[EXAMPLE TESTED]` for those that pass.

**Docs got out of sync after a code change?**
Re-run `/docs-pack <same-path>`. The content-writer detects existing docs and updates only what changed (preserves your manual edits).

**Should I commit the docs?**
Yes — they live in `<repo>/docs/<module>/` for that reason. The plugin produces drafts; your team reviews + commits.

## Examples

### API documentation for backend service
```bash
/docs-pack src/api --template api-reference --audience developer
```
Produces README + API-REFERENCE + EXAMPLES. content-writer extracts endpoints from FastAPI/Spring decorators.

### User-facing guide for a feature
```bash
/docs-pack ./features/oauth-login --type user-guide --audience user
```
Produces README + EXAMPLES (with screenshots placeholder). seo-engineer applies GEO + humanizer for public-facing copy.

### Operational runbook for a service
```bash
/docs-pack ./services/payment --template runbook --audience operator
```
Produces RUNBOOK with on-call procedures, common alerts + diagnostics, escalation paths.

### Architecture overview
```bash
/docs-pack . --template architecture --audience developer
```
Produces ARCHITECTURE.md with component diagram (Mermaid), data flow, deployment topology.

## Related

- `/docs` (carried) — general docs guidance + style
- [`/feature-design`](feature-design.md) — produces `<repo>/docs/features/` design packs (different convention exception)
- `/seo-review` (carried) — public-facing SEO/GEO audit after generation
- [`/content-creation`](feature-design.md) — for blog posts, marketing copy, landing pages
- [Memory](../concepts/memory.md) — generation summaries to L4
