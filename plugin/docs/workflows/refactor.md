# /refactor — Behavior-preserving structural change

Plan and execute a refactor with mandatory test-equivalence gate via RALF.

## When to use

- Breaking up large functions / classes
- Migrating to new patterns (class → functional, raw SQL → ORM)
- Extracting to a shared library
- Improving testability (DI, pure functions)

## Not for

- Adding features → [`/develop`](develop.md)
- Fixing bugs → [`/bugfix`](bugfix.md)
- Schema/library/version migrations → [`/migrate`](migrate.md)

## How to invoke

```bash
/refactor --files "src/api/*.ts" --goal "extract auth middleware to shared lib"
/refactor --scope "convert class-based to functional components"
/refactor --files "src/data/*.py" --goal "introduce Repository pattern" --preserve-tests
```

| Flag | Default | Effect |
|---|---|---|
| `--files <glob>` | ask user | Glob or file list |
| `--goal '<text>'` | required | Plain-English goal |
| `--preserve-tests` | true | Keep existing tests passing throughout |

## What you get

- Refactored code with public API preserved
- Test suite passing (tests updated only if signatures genuinely change)
- `<repo>/.ai-assets-memory/refactor/<run-id>/REFACTOR-LOG.md` — before/after + rationale
- PR with diff + refactor log

## How it works

1. **PLAN** — Lead reads target files, scopes refactor, breaks into per-file steps. You approve.
2. **EXECUTE** — Developer refactors per file (sequential per `subagent-isolation.md`). Tests run after each file.
3. **RALF** — if tests fail, oracle = `cli:./run-tests.sh`, kill-on = `same-error-repeats:2` (4 iter / 200K / 45 min cap).
4. **Verify** — Lead checks no behavior change via API diff.
5. **Memory write + PR** — REFACTOR-LOG.md emitted; `/create-pr` consumes it.

## The `same-error-repeats:2` discipline

This kill-on signal is intentional: two iterations failing with the same error usually means **the refactor introduced a real behavior change**, not a refactor bug. The workflow stops and asks you whether the goal needs adjustment or whether you actually want a behavior change (in which case it's a `/develop`, not a `/refactor`).

## Common questions

**Can I refactor and add a feature at the same time?**
No. Anti-pattern auto-fail. Open separate PRs for refactor and feature change.

**What if some tests need to update because the refactor exposes their brittleness?**
Acceptable IF the production code's tested behavior is unchanged. Document in REFACTOR-LOG.md what changed in the tests and why.

**What about API diff?**
Step 4 runs `git diff` on the public-API surface. Empty diff = clean refactor. Non-empty = either intentional (document in REFACTOR-LOG.md) or a violation (block).

## Examples

### Extract shared library
```bash
/refactor --files "src/{api,worker,scheduler}/auth.py" --goal "extract auth to shared lib"
```

### Convert class to functional components
```bash
/refactor --files "src/components/**/*.tsx" --goal "class → functional components"
```

### Improve testability
```bash
/refactor --files "src/services/order.py" --goal "extract repository pattern; remove direct DB calls"
```

## Related

- [`/develop`](develop.md) — for feature changes
- [`/bugfix`](bugfix.md) — for fixes
- [`/migrate`](migrate.md) — for schema/library/version migrations
- [`/run-tests`](feature-design.md) — sub-workflow for test execution
- [RALF](../concepts/ralf.md) — test-equivalence loop
- [Memory](../concepts/memory.md) — REFACTOR-LOG.md persists to L4
