---
trigger: always_on
description: Runtime boundaries and change hygiene for the Windsurf package in this repository.
---

# Global Package Rules

These rules apply to the Windsurf runtime package in this repository.

## Runtime Boundaries

- `.windsurf/` is the Windsurf runtime package in this repository
- `rules/`, `skills/`, `workflows/`, `hooks.json`, and `hooks/` together make up the Windsurf runtime package
- Claude-oriented assets must be normalized before they become Windsurf runtime material

## Validation

- keep Windsurf runtime guidance free of Claude-only runtime instructions
- review structural changes for broken references and project-specific commands
- update manifests and parity docs when adding new asset categories

## Change Hygiene

- prefer Windsurf-native representations over literal Claude feature emulation
- preserve intent even when the runtime primitive changes
- keep support guidance explicit and reviewable
