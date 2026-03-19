# Settings Mapping

This file maps Claude settings intent into Codex-friendly practices.

## Pre-Tool Intent

- risky shell actions require explicit scrutiny
- code writes should avoid secrets and sensitive material
- reads should stay scoped to the task

## Post-Tool Intent

- keep the user informed with concise progress updates
- review tool output before using it as prompt context
- preserve an explicit validation step for structural asset changes

## Repository Practice

- keep safety rules visible in `AGENTS.md`
- validate structural changes with an explicit review pass
- use visible translation instead of hidden mutation when importing Claude concepts
