# Pre-Commit — routed to existing Husky setup

## Step 0: framework detection

Found `.husky/` directory and `lint-staged` config in `package.json`. Routed to existing tooling rather than reinventing gates inline.

```
$ ls .husky/
_/  pre-commit  commit-msg
$ cat .husky/pre-commit
npx lint-staged
$ jq '."lint-staged"' package.json
{
  "*.{ts,tsx}": ["eslint --fix", "prettier --write"],
  "*.{json,md,yml}": ["prettier --write"]
}
```

## Stage executed: `pre-commit`

```
$ git commit -m "feat(billing): add proration helper"
✔ Preparing lint-staged...
✔ Running tasks for *.{ts,tsx}
   ✔ eslint --fix          (4 files, 0 errors)
   ✔ prettier --write      (4 files, 2 reformatted)
✔ Applying modifications...
```

Auto-fix outcome: `prettier --write` reformatted `app/billing/proration.ts` and `app/billing/proration.test.ts`. Husky re-staged the formatted versions automatically (lint-staged contract).

## Stage executed: `commit-msg`

`commitlint` ran via the `commit-msg` hook against the proposed message:

```
✔ subject-case: ok
✔ type-enum: feat
✔ scope-enum: billing
```

## Per-gate result

| Gate                 | Source                  | Status |
| -------------------- | ----------------------- | ------ |
| eslint --fix         | husky / lint-staged     | pass   |
| prettier --write     | husky / lint-staged     | pass   |
| commitlint           | husky / commit-msg      | pass   |

No additional inline gates were run — Husky already covers lint, format, and commit-message for this stack. Running them again would duplicate work and risk conflicting auto-fixes.

## Final commit message

```
feat(billing): add proration helper for mid-cycle plan upgrade

Computes prorated charge by remaining seconds in the billing period.
Credits unused old-tier value as a separate invoice line item.

Refs: #4180
```

## Verdict

Ready to commit. Husky owns the gate; this skill stayed out of its way.
