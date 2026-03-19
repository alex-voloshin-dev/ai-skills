# Global Package Rules

These rules apply to the Codex runtime package in this repository.

## Runtime Boundaries

- `.claude/` is the sibling Claude runtime package
- `.agents/skills/` and `.codex/` together make up the Codex runtime package
- Claude-oriented assets must be normalized before they become Codex runtime material

## Validation

- keep Codex runtime guidance free of Claude-only runtime instructions
- review structural changes for broken references and project-specific commands
- update manifests and parity docs when adding new asset categories

## Change Hygiene

- prefer Codex-native representations over literal Claude feature emulation
- preserve intent even when the runtime primitive changes
- keep support guidance explicit and reviewable