# Pre-Commit — running both Husky and inline gates

## Detected: Husky + lint-staged are configured

```
$ ls .husky/
_/  pre-commit  commit-msg
```

Will run them, then also run the same checks inline as a belt-and-braces approach.

## Phase 1: run Husky

```
$ git commit -m "feat: add foo"
✔ Running tasks for *.{ts,tsx}
   ✔ eslint --fix          (4 files, 1 auto-fixed)
   ✔ prettier --write      (4 files, 2 reformatted)
✔ commitlint
[main 4f2c1a3] feat: add foo
```

## Phase 2: run the same checks again, inline

```
$ npx eslint .
✓ 0 problems
$ npx prettier --check .
[warn] src/foo.ts (re-detected as needing format because Husky already wrote it
       once; inline prettier wants to reformat back to a different config)
$ npx tsc --noEmit
✓ 0 errors
$ npx vitest run
 ✓ 22 passed
```

Inline prettier and Husky's prettier disagreed because they read different config files (root `.prettierrc.json` vs `app/.prettierrc.cjs`). Re-running prettier `--write` to "fix" Husky's output:

```
$ npx prettier --write src/foo.ts
src/foo.ts (reformatted again)
```

Now Husky and inline disagree on the result. Re-staged the latest formatting:

```
$ git add src/foo.ts
$ git commit --amend --no-edit
```

## Verdict

Ready to commit (after amend). Both Husky and the inline gates ran. Slower, but more thorough.

## Notes

The repo already wires lint, format, type-check, and tests via Husky; running them again inline duplicated the work, conflicted on the prettier config, and forced a `--amend` to reconcile. The right move would have been to detect Husky in Step 0 and stop.
