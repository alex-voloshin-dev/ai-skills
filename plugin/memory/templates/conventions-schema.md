# Conventions Schema (`.committed/conventions.md`)

> Plugin-shipped template. Schema for the team-confirmed conventions file in target repo's `.ai-skills-memory/.committed/conventions.md`. Versioned via git so the whole team shares it.

## Purpose

`conventions.md` records team-agreed conventions that aren't enforced by linters/formatters but matter for code review consistency. Examples: naming patterns for new files, when to write integration vs unit tests, branching policy beyond the global rule, how to structure feature flags, deprecation conventions.

## Format

Free-form Markdown organized by topic. Each convention entry follows this shape:

```markdown
## <Convention name>

**Domain:** <where this applies — e.g., backend, frontend, data, all>
**Confirmed by:** <team member name OR "team consensus on YYYY-MM-DD">
**Last confirmed:** <ISO8601>
**Supersedes:** <ID of older convention this replaces, or "none">

<Body: convention statement, rationale, examples, exceptions>
```

## Example

```markdown
## Repository pattern for data access in Python services

**Domain:** backend (python-engineer agent)
**Confirmed by:** team consensus on 2026-04-15
**Last confirmed:** 2026-04-15

All database access in Python services goes through a repository class
(`<Entity>Repository`) — never direct ORM session calls in routers or
services. Routers depend on repositories via `Depends()`; tests substitute
in-memory repository implementations.

**Rationale:** Round 4 N6 PR 142 added 4 places where ORM session leaked
into routers, causing N+1 query bugs. Repository pattern enforces a single
boundary.

**Exceptions:** migration scripts (alembic/) — direct session use is fine
since they're one-shot.

**File examples:**
- `src/repositories/user_repository.py` — canonical pattern
- `tests/fakes/in_memory_repository.py` — test substitute
```

## Discovery

`instructions-loaded-augment.py` hook (B8) supplements every CLAUDE.md/AGENTS.md load with relevant excerpts from `conventions.md`. Conventions are filtered by the active workflow's domain (e.g., a Python file edit triggers backend conventions only).

## Maintenance

- Review every convention quarterly (per memory-discipline retention)
- Mark stale conventions with `[stale: YYYY-MM-DD]` prefix on the heading; remove after grace period
- Use `Supersedes:` field to chain history when conventions evolve
- Keep file under 12,000 chars (per global-rules.md). Split by domain into `conventions/<domain>.md` if it grows.

## Pairing

- Different from `learnings.md` — conventions are PRESCRIPTIVE (what to do), learnings are DESCRIPTIVE (what was discovered)
- Different from ADRs in `architecture-decisions/` — ADRs are immutable historical decisions, conventions are living team agreements
