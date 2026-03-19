# Service `AGENTS.md` Template

Use this template for a service or directory with its own local rules.

```md
# <Service Name> Guidelines

## Scope

This directory owns <service responsibilities>.

## Stack

- Runtime: <runtime>
- Framework: <framework>
- Test framework: <tests>

## Local Rules

- Keep changes inside this service unless cross-service work is required
- Reuse existing patterns before introducing new abstractions
- Add or update tests for behavior changes

## Important Files

- `<path>` — <purpose>
- `<path>` — <purpose>

## Verification

- `<build command>`
- `<test command>`
- `<lint command>`
```
