# Global Package Rules

These rules apply to the Codex runtime package in this repository.

## Runtime Boundaries

- `.agents/skills/` plus `.codex/` together make up the Codex runtime package in this repository
- `.claude/` is the semantic source of truth, not the Codex runtime format
- Claude-oriented assets must be translated into Codex-native primitives before they become Codex runtime material

## Validation

- keep Codex runtime guidance free of Claude-only runtime instructions
- review structural changes for broken references and project-specific commands
- update manifests and parity docs when adding new asset categories

## Change Hygiene

- prefer Codex-native representations over literal Claude feature emulation
- preserve intent even when the runtime primitive changes
- keep support guidance explicit and reviewable
