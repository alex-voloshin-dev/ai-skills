# Settings Mapping

This file maps the current Claude `settings.json` intent into visible Codex practices.

## Source Behavior

Claude currently enforces:

- `PreToolUse (Write|Edit)` -> block secrets in code
- `PreToolUse (Bash)` -> block dangerous commands
- `PreToolUse (Read)` -> block sensitive file reads
- `PostToolUse (*)` -> log tool activity once per tool event

## Codex Translation

Codex has no hidden hook runtime in this package, so preserve the same intent through visible rules:

- risky shell actions require explicit scrutiny and approval
- code writes should avoid secrets and sensitive material
- reads should stay scoped to the task
- structural asset changes require an explicit validation pass
- user-visible progress updates replace hidden activity logging

## Repository Practice

- keep safety rules visible in `AGENTS.md`
- keep secret-handling guidance visible in skills and review checklists
- keep sensitive-read guidance visible in package rules and task instructions
- validate structural changes with an explicit review pass
- use visible translation instead of hidden mutation when importing Claude concepts
