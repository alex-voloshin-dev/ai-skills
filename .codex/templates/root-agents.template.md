# Root `AGENTS.md` Template

Use this template for repository-wide Codex guidance.

````md
# <Project Name> Project Guidelines

## What This Project Does

- <one-line product summary>
- <main user value>

## Architecture

| Service | Stack | Notes |
|---|---|---|
| <service> | <stack> | <purpose> |

## Mandatory Rules

- Prefer root-cause fixes over workarounds
- No secrets in git
- Keep logs clean
- Follow the project's testing requirements before finishing

## Project Structure

```text
<repo tree excerpt>
```

## Codex Guidance

- Use root `AGENTS.md` for global policy
- Use local `AGENTS.md` files for directory-specific rules
- Use `.agents/skills` for reusable task workflows
- Keep documentation in English
````
