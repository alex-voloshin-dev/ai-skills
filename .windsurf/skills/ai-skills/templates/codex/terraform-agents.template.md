# `AGENTS.md` Template: Terraform

```md
# [Infrastructure Area] Guidelines

## Stack

- Terraform [version]
- Cloud: [Azure / AWS / GCP]
- State backend: [backend type]

## Hard Rules

- no manual drift acceptance without documenting it
- prefer explicit variables and outputs
- keep modules narrowly scoped
- plan before apply

## Structure

- `modules/` — reusable infrastructure units
- `[env path]/` — environment entrypoints
- `[policy path]/` — policy or validation assets

## Commands

- Format: `[terraform fmt -recursive]`
- Validate: `[terraform validate]`
- Plan: `[terraform plan]`

## Safety

- document imports, taints, and state moves
- call out destructive changes before execution
- note secrets handling and backend access rules
```
