---
trigger: always_on
description: Git conventions for commits, branches, and pull requests. Apply when working with repository git workflows.
---

# Git Conventions

Standards for commit messages, branching, and pull requests. Follow these conventions in all git operations.

## Commit Messages

Use **Conventional Commits** format:

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

### Types

| Type | When to Use |
|---|---|
| `feat` | New feature or capability |
| `fix` | Bug fix |
| `refactor` | Code change that neither fixes a bug nor adds a feature |
| `perf` | Performance improvement |
| `test` | Adding or updating tests |
| `docs` | Documentation changes only |
| `chore` | Build process, dependencies, CI config |
| `ci` | CI/CD pipeline changes |
| `style` | Formatting, whitespace (no logic change) |
| `revert` | Reverting a previous commit |

### Rules

- **Subject line**: Imperative mood, lowercase, no period, max 72 characters
- **Scope**: Module, component, or area affected (optional but recommended)
- **Body**: Explain WHAT and WHY, not HOW. Wrap at 72 characters
- **Footer**: Reference issues (`Closes #123`), note breaking changes (`BREAKING CHANGE: ...`)
- **Breaking changes**: Add `!` after type/scope: `feat(api)!: remove deprecated endpoint`

### Examples

```
feat(auth): add OAuth2 login with Google provider
fix(api): handle null response from payment gateway
refactor(db): migrate user queries to repository pattern
docs(readme): add local development setup instructions
chore(deps): upgrade Spring Boot to 3.4.1
test(orders): add integration tests for order cancellation
perf(search): add index on product.category_id column
ci(github): add parallel test execution to PR workflow
```

## Branching Strategy

### Branch Naming

```
<type>/<ticket-id>-<short-description>
```

| Prefix | Purpose |
|---|---|
| `feature/` | New features |
| `fix/` | Bug fixes |
| `hotfix/` | Urgent production fixes |
| `refactor/` | Code restructuring |
| `chore/` | Maintenance tasks |
| `docs/` | Documentation |
| `release/` | Release preparation |

Examples:
- `feature/AUTH-42-oauth-google-login`
- `fix/API-108-null-payment-response`
- `hotfix/PROD-15-memory-leak-worker`

### Branch Rules

- **Never commit directly to `main`** — always use feature branches and PRs
- **Keep branches short-lived** — merge within days, not weeks
- **Rebase on `main` before creating PR** — keep history clean
- **Delete branch after merge**

## Pull Request Standards

- **Title**: Same format as commit message (`type(scope): description`)
- **Description**: Include summary, changes list, testing approach, checklist
- **Size**: Aim for < 400 lines changed. Split larger changes into stacked PRs
- **One concern per PR** — do not mix features, refactors, and dependency updates
- **Link related issues** in the PR description
- **Request reviewers** who own the affected code areas

## Commit Hygiene

- **Atomic commits** — each commit represents one logical change
- **No WIP commits on `main`** — squash or rebase before merge
- **No merge commits in feature branches** — use rebase to stay up to date
- **Never force-push shared branches** — only force-push personal feature branches
- **Never commit secrets, credentials, or large binary files**
- **Sign commits** if required by project policy

## Integration

- **Workflows**: `/pre-commit` (validates before commit), `/create-pr` (generates PR description), `/code-review` (review standards)
- **Hooks**: `block-secrets-in-code` (PreToolUse (Write|Edit)), `block-dangerous-commands` (PreToolUse (Bash))