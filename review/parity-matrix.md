# Parity Matrix

This document tracks semantic parity between the Claude Code, Codex, and Windsurf runtime packages stored in this repository.

## Scope

Parity means the runtimes provide equivalent capability coverage, even when the runtime primitives differ.

- Claude Code uses `.claude/agents`, `.claude/rules`, `.claude/skills`, hooks, and `settings.json`.
- Codex uses `.agents/skills` plus `.codex/roles`, `.codex/rules`, `.codex/operations`, templates, and checklists.
- Windsurf uses `.windsurf/rules`, `.windsurf/skills`, `.windsurf/workflows`, `hooks.json`, and supporting skill resources.
- A direct file-for-file match is not required.
- Capability coverage and intent must match.

## Current Baseline

### Roles

- Status: full semantic match
- Coverage target: every role in `.claude/agents/` has a corresponding role in `.codex/roles/` and `.windsurf/rules/roles/`

### Skills

- Status: full semantic match
- Coverage target: every skill in `.agents/skills/` has a corresponding skill in `.windsurf/skills/`
- Notes: Windsurf skill bodies stay concise and use `.claude/skills/` as workflow/reference input when the Claude version is more detailed

### Rules and Guardrails

- Status: semantic match
- Claude uses rules, hooks, and settings
- Codex uses rules, operations, and checklists
- Windsurf uses rules plus workspace hooks
- Mapping is capability-based rather than file-name-based

### Workflows

- Status: semantic match
- Claude stores many user-facing procedures as skills
- Windsurf exposes user-facing procedures as `.windsurf/workflows/` while keeping reusable knowledge in `.windsurf/skills/`

### Templates

- Status: semantic match
- Claude templates focus on Claude-oriented runtime assets
- Codex templates focus on `AGENTS.md`, skill authoring, and Codex-native scaffolding
- Windsurf stores template and checklist material as supporting resources inside relevant skills instead of a separate top-level primitive

## Review Rules

- new roles must be added to all runtime packages in the same change set
- new skills must be added to all runtime packages in the same change set, using runtime-native representations where needed
- new user-facing task procedures should update Windsurf workflows when the Claude package adds or materially changes the corresponding procedure
- when a Claude hook introduces a new guardrail, Codex must receive an explicit visible equivalent
- when a Claude or Codex asset adds a reusable resource that Windsurf cannot model as a top-level primitive, preserve it as a supporting resource in the relevant Windsurf skill
- project-specific references must be removed before assets are accepted into this repository
