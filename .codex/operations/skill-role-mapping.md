# Skill Role Mapping

This document defines the Codex-side contract for attaching role behavior to reusable skills.

## Purpose

Claude skills may reference runtime agent application directly. Codex in this repository does not have an equivalent hidden agent runtime.

Use visible role overlays instead:

`skill frontmatter -> codex-roles -> role overlay activation -> Codex behavior`

## Frontmatter Contract

`SKILL.md` may include:

```yaml
codex-roles:
  - software-engineer
```

Rules:

- `codex-roles` is optional
- values must match filenames in `.codex/roles/` without the `.md` suffix
- values must also match files in `.codex/rules/role-overlays/`
- order matters only when a consuming project wants to announce a primary role first
- keep the list short and execution-relevant

## Layer Responsibilities

### `.agents/skills/*/SKILL.md`

- declares when the workflow should be used
- may declare `codex-roles` for the workflow
- should not claim that a hidden agent process is started

### `.codex/roles/*.md`

- defines the reference view of the role
- captures mission, ownership, deliverables, preferred skills, and boundaries
- is not the runtime instruction layer

### `.codex/rules/role-overlays/*.md`

- defines executable Codex behavior for an active role
- should be concise, imperative, and testable
- must focus on priorities, evidence, decision rules, and handoff conditions

### `AGENTS.md`

- activates overlays when a skill with `codex-roles` is invoked
- makes the routing rule visible to the model and reviewers
- may add project-specific routing refinements

## Recommended `AGENTS.md` Rule

Use language like:

```md
When an invoked skill declares `codex-roles` in frontmatter, treat the matching
files under `.codex/rules/role-overlays/` as mandatory active instructions for
the task. Apply those overlays before executing the workflow and announce the
active role set in the next progress update.
```

## Authoring Guidance

- prefer one default role for most skills
- add multiple roles only when the workflow genuinely composes them
- if a skill switches roles by stack or evidence, encode the branching in the skill body and keep `codex-roles` limited to plausible overlays for that workflow
- move runtime-critical behavior into overlays instead of duplicating role prose inside every skill
- if no overlay would materially change execution, do not add `codex-roles`

## Validation Checklist

- every `codex-roles` value resolves to `.codex/roles/<id>.md`
- every `codex-roles` value resolves to `.codex/rules/role-overlays/<id>.md`
- overlay instructions do not conflict with root package rules
- skill wording does not imply hidden agent spawning
- parity docs reflect any new Codex-native routing pattern
