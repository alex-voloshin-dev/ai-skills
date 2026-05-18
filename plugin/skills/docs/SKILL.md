---
name: docs
description: Use this skill when the user asks to edit internal markdown documentation and source code must stay untouched — the internal documentation workflow to edit technical docs, ADRs, PRDs, design notes, release notes, and UI microcopy without touching source code, applying the Content Writer role. For public-facing blog posts, landing pages, and marketing content use `/content-creation` (it owns the GEO/SEO/humanizer pipeline). For full multi-document user-facing packs (README + API ref + runbook + tutorial) use `/docs-pack`.
argument-hint: [documentation target or section]
---

<!-- ARCHITECTURAL NOTE: no `context: fork`. This skill spawns the Content Writer subagent (and optionally an SEO Engineer subagent) via the `Agent` tool. Subagents cannot spawn other subagents (per Anthropic docs), so this skill MUST run in the main thread to retain spawn capability. -->

# Documentation

Safe documentation-only workflow. Edit markdown files without touching application source code, configs, or infrastructure. Applies `Agent(content-writer)` for all writing tasks.

**⚠️ CONSTRAINT: This workflow NEVER modifies source code (*.java, *.ts, *.tsx, *.py, *.go), configs (*.yaml, *.yml, *.json), infrastructure (*.tf, Dockerfile, Helm), or dependency files (pom.xml, package.json, requirements.txt).**

## 1. Define Scope

Ask the user (or extract from parent workflow):

- **What documentation?** (technical docs, API reference, README, PRD, design doc, ADR, release notes, UI copy)
- **Action**: Create new / update existing / restructure
- **Target files**: Which `.md` files will be affected

If the request is for **public-facing blog / landing / marketing content**, stop and route to `/content-creation`. This skill is internal-only.

## 2. Apply Roles

| Content Type | Primary Role | Additional Role |
|---|---|---|
| Technical documentation | `Agent(content-writer)` | — |
| API reference | `Agent(content-writer)` | Stack-specific role for accuracy |
| PRD / acceptance criteria | `Agent(product-manager)` | — |
| Architecture / ADR | `Agent(solution-architect)` | — |
| Release notes | `Agent(content-writer)` | — |
| UI microcopy | `Agent(content-writer)` | `Agent(frontend-engineer)` for context |

## 3. Gather Context

Before writing:

1. **Read project's `CLAUDE.md`** — terminology, conventions, tech stack
2. **Read existing docs** — understand structure, tone, terminology already in use
3. **Identify Diátaxis mode** — Tutorial, How-to, Reference, or Explanation
4. **Check related code** (read-only) — verify technical accuracy of claims

## 4. Write Content

Follow `Agent(content-writer)` standards:

- **Diátaxis framework** for documentation structure
- **English only** unless explicitly requested otherwise
- **Progressive disclosure** — overview first, details on demand
- **Tested examples** — all code snippets must be accurate
- **Consistent terminology** — match existing project conventions

## 5. Verify

- [ ] All internal links are valid (no broken references)
- [ ] Code examples are accurate and match current implementation
- [ ] Terminology is consistent with project conventions
- [ ] Formatting follows existing documentation patterns
- [ ] No secrets, PII, or internal-only information leaked
- [ ] No source code, config, or infrastructure files were modified

## 6. Summary

```
## Documentation Summary
- **Type**: [technical docs / blog / API reference / release notes / etc.]
- **Content mode**: [Tutorial / How-to / Reference / Explanation]
- **Files changed**:
  - [file1.md]: [created/updated — what changed]
  - [file2.md]: [created/updated — what changed]
- **Role(s) applied**: [Agent(content-writer), Agent(seo-engineer) if public]
- **SEO review**: [pass / N/A for internal docs]
- **Verification**: [links valid, formatting correct, no code files modified]
- **Next steps**: [if any]
```

## Integration

- **Roles**: `Agent(content-writer)` (primary), `Agent(product-manager)` (PRDs), `Agent(solution-architect)` (ADRs)
- **Follow-up**: `/pre-commit`, `/create-pr`
- **Related**: `/feature-dev` (inline docs during development), `/release` (release notes), `/docs-pack` (multi-document user-facing packs), `/content-creation` (public-facing blog / landing / marketing — owns GEO + SEO + humanizer pipeline)
