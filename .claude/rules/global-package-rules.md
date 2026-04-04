---
description: Runtime boundaries and change hygiene for the Claude Code package in this repository.
---

# Global Package Rules

These rules apply to the Claude Code runtime package in this repository.

## Runtime Boundaries

- this directory is the Claude Code runtime package in the source repository and installs to `~/.claude/`
- `agents/`, `skills/`, `rules/`, `hooks/`, and `settings.json` together make up the installed Claude runtime package
- Codex or Windsurf-oriented assets must be normalized before they become Claude runtime material

## Validation

- keep Claude runtime guidance free of Codex-only or Windsurf-only runtime instructions
- review structural changes for broken references and project-specific commands
- update manifests and parity docs when adding new asset categories

## Change Hygiene

- prefer Claude-native representations over literal Codex or Windsurf feature emulation
- preserve intent even when the runtime primitive changes
- keep support guidance explicit and reviewable
