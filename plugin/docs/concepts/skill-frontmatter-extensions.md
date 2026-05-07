# Skill Frontmatter: Claude Code Extensions

How four Claude Code-specific frontmatter fields shape skill UX in this plugin, and why other agentskills.io clients silently ignore them.

The 52 SKILL.md files in this plugin use YAML frontmatter that is mostly compatible with the [agentskills.io](https://agentskills.io) specification — but four fields are Claude Code extensions, not part of the spec. This doc exists so cross-client users (Cursor, OpenCode, Gemini CLI, Goose) understand which fields are load-bearing inside Claude Code and which are silently dropped elsewhere.

## The four fields

| Field | Type | Claude Code behavior | Used in | Example |
|---|---|---|---|---|
| `argument-hint` | string | Renders a placeholder in Claude Code's slash-command UI for `/<skill> <args>`. Hints what the user should type after the command. | 35 skills | `argument-hint: "[PRD path or feature description]"` |
| `context: fork` | literal | Claude Code runs the skill body in a forked `general-purpose` subagent context instead of the main thread. Used to make a skill behave as a self-contained user-invocable workflow. | 28 skills | `context: fork` |
| `user-invocable: true` | boolean | Alternate signal that exposes the skill in `/help` listings without forking context. The skill stays in the main thread. | 10 skills | `user-invocable: true` |
| `disable-model-invocation: true` | boolean | Prevents Claude Code's model from auto-loading the skill via description matching. The user must invoke the skill explicitly by name. Used for safety-critical operations. | 6 skills | `disable-model-invocation: true` |

### Important exception for `context: fork`

Per alpha.25, the three orchestration skills — `develop`, `team-bugfix`, and `feature-design` — MUST NOT use `context: fork`. Subagents in Claude Code cannot spawn other subagents, so an orchestrator running in a forked context loses access to the `Agent` tool and cannot drive the DEV → REVIEW → QA pipeline. These three skills run in the main thread; the architectural note is repeated inline at the top of each SKILL.md. The `plugin/dev/validate.py` validator enforces this with the `orchestration_no_fork` check.

## Why these fields are not in the spec

The [agentskills.io specification](https://agentskills.io/specification) standardizes a small, portable surface — `name`, `description`, `license`, `compatibility`, `metadata`, and `allowed-tools` (experimental). Anything beyond that is implementation-specific. Claude Code's UI affordances — slash-command hints, fork-vs-main thread routing, model-invocation gating — don't generalize to other clients, so the spec deliberately leaves them out. The plugin uses the four extensions because they are load-bearing for the Claude Code experience, not because every client should support them.

## Cross-client portability

Cursor, OpenCode, Gemini CLI, and Goose silently ignore unknown frontmatter keys. The skills still load and trigger correctly in those clients — `description` is the universal activation signal — but the Claude Code-specific UX (argument hints in `/help`, forked execution, explicit-only invocation) is lost.

If you want a skill to communicate the same intent across clients, mirror the value into the spec-compliant `metadata` map. Other clients will preserve and surface `metadata` via their own conventions, while Claude Code continues to read the top-level fields:

```yaml
---
name: my-skill
description: ...
context: fork
argument-hint: "[PRD path]"
metadata:
  ai-assets-context: fork
  ai-assets-argument-hint: "[PRD path]"
---
```

The `ai-assets-` prefix avoids collision with other plugins that may also extend `metadata`.

## Where to find examples

- `argument-hint` — `plugin/skills/refactor/SKILL.md`, `plugin/skills/security-audit/SKILL.md`
- `context: fork` — `plugin/skills/refactor/SKILL.md`, `plugin/skills/spike/SKILL.md`
- `user-invocable: true` — `plugin/skills/humanizer/SKILL.md`, `plugin/skills/geo-writer/SKILL.md`
- `disable-model-invocation: true` — `plugin/skills/deploy-production/SKILL.md`, `plugin/skills/release/SKILL.md`

## Related

- [Memory](memory.md) — how skills persist learnings across sessions
- [RALF](ralf.md) — the iteration loop several user-invocable skills wrap
- [Eval](eval.md) — how skill outputs are scored
