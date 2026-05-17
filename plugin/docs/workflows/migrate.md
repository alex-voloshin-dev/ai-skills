# /migrate — Versioned migration with tested rollback

Schema, library, version, framework migration with documented + tested rollback procedure.

## When to use

- Database schema migration (Postgres major version, schema additions/changes)
- Framework version upgrade (Django 3 → 4, Spring Boot 2 → 3)
- Library replacement requiring code changes (raw SQL → ORM, lodash → ramda)
- Breaking-API client SDK upgrade

## Not for

- Refactors without external contract change → [`/refactor`](refactor.md)
- Small bug-fix releases → [`/develop`](develop.md)
- Infrastructure changes without code → `/infra-change` (carried)

## How to invoke

```bash
/migrate "Postgres 13 → 14"
/migrate "Django 3.2 → 4.0"
/migrate "React class → functional components" --staged
```

| Flag | Default | Effect |
|---|---|---|
| `<migration>` (positional) | required | Source → target description |
| `--staged` | off | Use blue-green or canary pattern (requires ops sign-off) |

## What you get

- Migration code (schema scripts, version pins, compat shims)
- `<repo>/.ai-skills-memory/migrate/<run-id>/MIGRATION-PLAN.md` — pre-flight + forward + rollback + risk
- `<repo>/.ai-skills-memory/migrate/<run-id>/VALIDATION.md` — test results + data integrity checks
- `<repo>/.ai-skills-memory/.committed/migrations/<name>/` — strategy + validation report (versioned in git after sign-off)
- PR with migration + rollback procedures

## The hard rule

**You must approve the rollback procedure separately from the migration plan.** The workflow refuses to advance until both are explicitly OK'd. This is by design — most migration failures are rollback failures, not forward-procedure failures.

## How it works

1. **PLAN** — Lead researches compat matrix, drafts forward + rollback procedures, risk matrix. **You approve rollback explicitly.**
2. **EXECUTE** — `devops-engineer` (DB schema), `developer` per stack (app changes). Sequential per file.
3. **VALIDATE** — Full test suite + data integrity checks (row counts + checksums + FK constraints + business invariants).
4. **RALF** — if validation fails: oracle = `python:./validate-migration.py`, kill-on = `oracle-pass OR no-progress:2` (5 iter / 300K / 90 min cap).
5. **Sign-off + memory write** — Lead approves; committed reports for team review.

## Common questions

**What if the rollback can't be tested on staging?**
Hard requirement. The workflow refuses to proceed without a tested rollback. If your environment makes this impossible, escalate — running an untested rollback in production is a known way to lose data.

**What's `--staged`?**
Blue-green or canary deployment pattern (gradual traffic shift instead of cutover). Requires canary deployment infrastructure; the workflow detects and refuses if absent.

**What about Postgres pg_upgrade specifically?**
Has its own rollback semantics — `--link` mode is reversible until ANALYZE runs. Document this in your MIGRATION-PLAN.md so the rollback section covers the pre-ANALYZE window separately from post-ANALYZE.

**Where do migration plans live in git?**
`.ai-skills-memory/.committed/migrations/<name>/plan.md` and `validation-report.md`. Allowlist-validated by `pre-tool-use-committed-write.py`.

## Examples

### Postgres major version upgrade
```bash
/migrate "Postgres 13.10 → 14.11"
```
Plan covers: extensions compat, client lib compat, --link mode, ANALYZE step, rollback via snapshot, data integrity per top-50 tables.

### Framework upgrade
```bash
/migrate "Django 3.2 → 4.0"
```
Plan covers: dep updates, deprecation warnings, breaking changes per release notes, compat shims, parallel-run mode.

### Library replacement (staged)
```bash
/migrate "raw psycopg2 → SQLAlchemy 2.0 async" --staged
```
Plan covers: introduce SQLAlchemy alongside existing code, dual-mode for N weeks, gradual cutover per service, validation per cutover wave.

## Related

- [`/refactor`](refactor.md) — for in-app structural changes without external contract change
- [`/develop`](develop.md) — for new functionality
- [`/env-analyze`](env-analyze.md) — pre-flight environment check
- [`/run-tests`](feature-design.md) — full test suite execution
- [Memory](../concepts/memory.md) — committed migration reports
- [RALF](../concepts/ralf.md) — validation loop
