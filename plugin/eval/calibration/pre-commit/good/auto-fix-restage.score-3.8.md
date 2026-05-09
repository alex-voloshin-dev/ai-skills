# Pre-Commit — auto-fix + re-stage flow

## Step 0: framework detection

No `.husky/` / `.pre-commit-config.yaml` / `lefthook.yml`. Falling back to inline gates.

## Stack detection

- `package.json` → TypeScript (`typescript: ^5.4`)
- ESLint + Prettier configured (`.eslintrc.cjs`, `.prettierrc.json`)
- Test runner: `vitest` (per `package.json` `scripts.test`)
- Type-checker: `tsc --noEmit`

## Gates

### 1. eslint --fix (auto-fix)

```
$ npx eslint --fix $(git diff --cached --name-only --diff-filter=ACMR | grep -E '\.(ts|tsx)$')
3 problems auto-fixed: prefer-const ×2, no-unused-imports ×1
0 problems remaining
```

### 2. prettier --write (auto-fix)

```
$ npx prettier --write $(git diff --cached --name-only --diff-filter=ACMR | grep -E '\.(ts|tsx|json|md)$')
src/auth/session.ts (reformatted)
src/auth/session.test.ts (reformatted)
```

### 3. Re-stage formatted files

```
$ git add src/auth/session.ts src/auth/session.test.ts
```

Re-staged 2 files after auto-fix. Diff vs pre-fix shown below for transparency:

```diff
- const  user= await getUser(req)
+ const user = await getUser(req);
```

### 4. Re-run lint on re-staged content

```
$ npx eslint $(git diff --cached --name-only --diff-filter=ACMR | grep -E '\.(ts|tsx)$')
✓ 0 problems
```

### 5. Type-check

```
$ npx tsc --noEmit
✓ 0 errors
```

### 6. Tests (vitest, changed-only)

```
$ npx vitest run --changed
✓ src/auth/session.test.ts (8 tests)
Test Files  1 passed (1)
     Tests  8 passed (8)
```

## Per-gate result

| Gate          | Status | Notes                                  |
| ------------- | ------ | -------------------------------------- |
| eslint --fix  | pass   | 3 auto-fixed                           |
| prettier      | pass   | 2 files reformatted, re-staged         |
| eslint (post) | pass   | 0 remaining                            |
| tsc           | pass   |                                        |
| vitest        | pass   | 8/8                                    |

Skipped destructive auto-fixes: `no-unused-vars` would have removed an exported helper used by tests; surfaced for manual review (none found).

## Final commit message (Conventional Commits)

```
fix(auth): rotate session token on role change

Closes #4180
```

## Verdict

Ready to commit.
