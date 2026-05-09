# Pre-Commit — gates passed

## Stack

TypeScript / Vitest. Repo uses Conventional Commits (commitlint config present at `.commitlintrc.cjs`, types: feat, fix, chore, docs, refactor, perf, test, build, ci).

## Gates

### eslint

```
$ npx eslint .
✓ 0 problems
```

### prettier

```
$ npx prettier --check .
✓ All matched files use Prettier code style!
```

### tsc

```
$ npx tsc --noEmit
✓ 0 errors
```

### vitest

```
$ npx vitest run
✓ 22 passed
```

## Per-gate result

| Gate     | Status |
| -------- | ------ |
| eslint   | pass   |
| prettier | pass   |
| tsc      | pass   |
| vitest   | pass   |

## Final commit message

```
updated some files in auth and added a helper for proration
```

## Verdict

Ready to commit.

## Notes

Repo has commitlint configured to enforce Conventional Commits. The proposed message is free-form, has no `type(scope):` prefix, and would fail commitlint at the `commit-msg` stage. The skill should have proposed something like `feat(billing): add proration helper` or `fix(auth): rotate session on role change`. The commit will be rejected as written.
