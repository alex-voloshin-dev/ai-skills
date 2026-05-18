---
name: pre-commit
description: Use this skill when running a quality gate over staged changes before a git commit to catch lint/format/type/test failures — a pre-commit quality gate that lints, formats, type-checks, tests, and validates before committing. Detects existing pre-commit framework / Husky / Lefthook / lint-staged and routes to it; otherwise runs an inline stack-detected gate. Not the [pre-commit framework](https://pre-commit.com) itself — see Step 0 for framework detection.
disable-model-invocation: true
---

# Pre-Commit

Automated quality gate before committing code. Runs linting, formatting, tests, and validation checks. Fixes auto-fixable issues and reports blockers.

## 0. Detect Existing Hook Framework — route first, build inline second

Before running any inline gate, check whether the repo already has a pre-commit hook framework configured. If so, route to it; the team's framework choice supersedes anything in this skill.

| Marker file present | Framework | Run command |
|---|---|---|
| `.pre-commit-config.yaml` (root) | [pre-commit framework](https://pre-commit.com) | `pre-commit run --files <staged-files>` (or `--all-files` if staged scope ambiguous) |
| `.husky/` directory | [Husky](https://typicode.github.io/husky/) | `.husky/pre-commit` (or `git commit` triggers it; just continue) |
| `lefthook.yml` / `lefthook.toml` (root) | [Lefthook](https://github.com/evilmartians/lefthook) | `lefthook run pre-commit` |
| `package.json["lint-staged"]` | [lint-staged](https://github.com/okonet/lint-staged) (Node) | `npx lint-staged` |
| `.git/hooks/pre-commit` (custom) | Bespoke shell hook | inspect contents; run only if obviously safe |

If a framework is detected:
1. Run its command on staged files.
2. Capture its output (pass/fail + which checks ran).
3. If it passes — skip Steps 1–7 below; go straight to Step 8 (Summary).
4. If it fails — fix per its output, re-stage, re-run; do not duplicate the same checks inline.

If multiple markers are present, prefer the most specific (Husky + lint-staged is the common Node combo — let Husky drive).

If no framework is detected, continue to Step 1 below.

## 1. Detect Project Stack

Read `CLAUDE.md` and project config files to determine:

- **Language(s)**: TypeScript, Java, Python, Go, etc.
- **Package manager**: npm/pnpm/yarn, maven/gradle, pip/poetry, go mod
- **Linter**: ESLint, Checkstyle, ruff/flake8, golangci-lint
- **Formatter**: Prettier, google-java-format, black/ruff, gofmt
- **Test runner**: Vitest/Jest, JUnit/Maven, pytest, go test

## 2. Check Staged Changes

```
// turbo
git status --short
```

Identify which files are staged. If no files are staged:

```
⚠️ No staged changes found. Stage your changes first:
  git add <files>
```

Stop and inform the user.

## 3. Run Linter

Run the project's linter on staged files:

| Stack | Command |
|---|---|
| TypeScript/JS | `npx eslint --fix <files>` |
| Python | `ruff check --fix <files>` or `flake8 <files>` |
| Java | `mvn checkstyle:check` or `gradle checkstyleMain` |
| Go | `golangci-lint run <files>` |

**Completion**: If exit code 0 after auto-fix → proceed. If errors remain → report and STOP:

```
## Lint Issues (must fix)
- [file:line] [rule] description
```

## 4. Run Formatter

Run the project's formatter:

| Stack | Command |
|---|---|
| TypeScript/JS | `npx prettier --write <files>` |
| Python | `ruff format <files>` or `black <files>` |
| Java | `mvn spotless:apply` or `google-java-format <files>` |
| Go | `gofmt -w <files>` |

Re-stage any auto-formatted files:
```
git add <formatted-files>
```

**Completion**: Files formatted and re-staged → proceed.

## 5. Run Type Checker (if applicable)

| Stack | Command |
|---|---|
| TypeScript | `npx tsc --noEmit` |
| Python | `mypy <files>` or `pyright <files>` |

**Completion**: If exit code 0 → proceed. If type errors → report and STOP.

## 6. Run Tests

Run the project's test suite (unit tests at minimum):

| Stack | Command |
|---|---|
| TypeScript/JS | `npx vitest run` or `npx jest` |
| Python | `pytest -x -q` |
| Java | `mvn test -q` or `gradle test` |
| Go | `go test ./...` |

If tests fail:
1. Analyze the failure
2. Attempt auto-fix if the fix is obvious and safe
3. Re-run tests to verify
4. If still failing — report and STOP

**Completion**: All tests pass → proceed. Any failure after auto-fix attempt → STOP.

## 7. Validate Build (if applicable)

| Stack | Command |
|---|---|
| TypeScript/JS | `npm run build` or `npx tsc --noEmit` |
| Java | `mvn compile -q` |
| Go | `go build ./...` |

## 8. Summary

```
## Pre-Commit Results

| Check      | Status | Details |
|------------|--------|---------|
| Lint       | ✅/❌  | [issues found/fixed] |
| Format     | ✅/❌  | [files formatted] |
| Type check | ✅/❌/⏭️ | [errors or N/A] |
| Tests      | ✅/❌  | [passed/failed count] |
| Build      | ✅/❌/⏭️ | [success or N/A] |

Ready to commit: [YES / NO — fix issues above first]
```

If all checks pass, suggest the commit command:
```
git commit -m "<type>(<scope>): <description>"
```

Follow Conventional Commits format.

## Integration

- **Called by**: `/feature-dev`, `/bugfix` (before commit)
- **Calls**: `/run-tests`
- **Followed by**: `/create-pr`
