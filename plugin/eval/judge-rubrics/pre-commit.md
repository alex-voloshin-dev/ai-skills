# Pre-Commit Rubric

## Overview

Evaluates `/pre-commit` output — local quality gates run before a commit lands. Six dimensions × five levels. Frame: route to existing tooling first, only run inline gates when the repo lacks them; never report a pass when something failed.

## Dimensions

### Dimension 1: Framework Routing (Step 0)
Detects existing pre-commit framework and delegates to it.

- **Level 1:** Reinvents gates inline despite `.pre-commit-config.yaml` / `.husky/` / `lefthook.yml` / `package.json` `lint-staged` present
- **Level 2:** Notices framework but runs both inline + framework (double work, conflicting results)
- **Level 3:** Detects framework and runs it; ignores configured stage flags
- **Level 4:** Detects framework + runs the right stage (`pre-commit` vs `commit-msg`) + reports each hook result
- **Level 5:** All of L4 + checks hook freshness (`pre-commit autoupdate`, `husky install` idempotent)

### Dimension 2: Stack Detection
Identifies the linter / formatter / type-checker / test runner per stack when no framework is configured.

- **Level 1:** Runs Python tooling on a JS repo (or vice versa)
- **Level 2:** Picks one tool correctly but skips type-checker / tests
- **Level 3:** Linter + formatter + type-checker chosen correctly
- **Level 4:** Full quartet (linter / formatter / type-checker / test runner) chosen + commands match installed versions
- **Level 5:** All of L4 + monorepo-aware (only runs gates for changed packages via nx/turbo/changed-files)

### Dimension 3: Auto-Fix Attempt
Attempts safe auto-fixes before reporting.

- **Level 1:** Reports lint/format failures without attempting any fix
- **Level 2:** Runs `--fix` but does not re-stage formatted files
- **Level 3:** Runs auto-fix + re-stages + re-runs the gate
- **Level 4:** Auto-fix scoped to safe rewriters (eslint --fix, ruff check --fix, prettier --write, spotless:apply, gofmt) + diff shown
- **Level 5:** All of L4 + skips destructive auto-fixes (e.g., eslint `no-unused-vars` removing code) and surfaces them as manual review

### Dimension 4: Secret-Scan Inclusion
Runs a secret scanner when one is available.

- **Level 1:** Secret scan skipped despite `gitleaks` / `trufflehog` in repo
- **Level 2:** Runs secret scan but on the whole repo (slow, irrelevant) instead of staged files
- **Level 3:** Runs gitleaks/trufflehog on staged diff
- **Level 4:** Staged-diff scan + uses repo's `.gitleaks.toml` allowlist
- **Level 5:** All of L4 + blocks commit when finding is non-allowlisted; offers `--no-verify` only with explicit user APPROVE

### Dimension 5: Stop Conditions Explicit
Each gate produces a clear pass/fail; never reports "all good" when something failed.

- **Level 1:** Reports "ready to commit" while a gate failed
- **Level 2:** Mixed signals (some gates skipped without note)
- **Level 3:** Per-gate pass/fail listed; final verdict matches
- **Level 4:** Per-gate pass/fail + counts (warnings vs errors) + first-failure context
- **Level 5:** All of L4 + remediation hint per failure (which command to re-run after fix)

### Dimension 6: Conventional Commit Message
Final commit suggestion matches Conventional Commits format.

- **Level 1:** "fix stuff" / "wip" / blank message proposed
- **Level 2:** Free-form message; not CC
- **Level 3:** CC format (`type: subject`); subject ≤ 72 chars
- **Level 4:** CC format + scope when applicable + body explaining why
- **Level 5:** All of L4 + footer for `BREAKING CHANGE:` / issue refs / `Co-authored-by:` when relevant

## Scoring Logic

- **Aggregate:** average of D1–D6
- **Pass threshold:** 3.5
- **Judge model:** Sonnet

## Anti-Patterns (Auto-Fail)

- Reports pass when typecheck / lint / test failed
- Runs both Husky hooks AND inline duplicates of those gates
- Proposes commit message ignoring Conventional Commits despite repo using CC
- Skips secret scan when `gitleaks` is wired
- `--no-verify` used without explicit user APPROVE

## Calibration Reference

- **Known-good:** `plugin/eval/calibration/pre-commit/good/*`
- **Known-bad:** `plugin/eval/calibration/pre-commit/bad/*`
