# Codex Asset Validation Checklist

## Core Checks

- [ ] Asset uses Codex-native concepts
- [ ] English only
- [ ] No secrets or credentials
- [ ] References resolve
- [ ] No machine-specific paths unless intentionally local docs
- [ ] File sits in the correct package directory

## `AGENTS.md` Checks

- [ ] Global policy stays in root `AGENTS.md`
- [ ] Scoped `AGENTS.md` files stay directory-specific
- [ ] Hard rules are near the top
- [ ] No redundant restatement of parent guidance

## `SKILL.md` Checks

- [ ] `name` present
- [ ] `description` is specific and activation-safe
- [ ] Workflow is actionable
- [ ] Bulky references moved to companion files
- [ ] No Claude-specific syntax, legacy file names, or Claude hook contracts

## Template and Checklist Checks

- [ ] Template is reusable
- [ ] Checklist is concise and scannable
- [ ] Examples do not conflict with project policy

## Script Checks

- [ ] Script purpose is explicit
- [ ] Dry-run or safe inspection path exists when appropriate
- [ ] Script does not perform hidden destructive behavior

## PowerShell Pattern

For non-trivial validation commands, prefer a `.ps1` file over large inline PowerShell blocks.
