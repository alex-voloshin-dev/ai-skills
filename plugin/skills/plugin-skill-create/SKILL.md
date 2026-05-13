---
name: plugin-skill-create
description: Internal procedure for `/plugin-author create`. Scaffolds a new skill INSIDE the ai-assets plugin (under `plugin/skills/`) with H5 frontmatter, eval test-case stub, and memory-write points pre-wired. Conforms to the agentskills.io specification (https://agentskills.io/specification) and ai-assets plugin conventions. No longer slash-invocable — call `/plugin-author create <name>` instead. Read by the `prompt-engineer` agent at task start when DEV-ing or reviewing a plugin skill.
disable-model-invocation: true
---

# /plugin-skill-create — Plugin-Convention Skill Scaffold

Generate `plugin/skills/<name>/SKILL.md` plus eval/case stub plus memory-hook scaffolding. Conforms to:

1. **agentskills.io specification** — https://agentskills.io/specification (frontmatter, naming, directory layout, progressive disclosure)
2. **agentskills.io best practices** — https://agentskills.io/skill-creation/best-practices (description style, body length, calibration)
3. **agentskills.io description optimization** — https://agentskills.io/skill-creation/optimizing-descriptions (trigger phrasing, what+when, keywords)
4. **ai-assets plugin conventions** — H5 frontmatter trigger pattern, schema-validated frontmatter, `<untrusted_content>` G1 wrapping where applicable, G7 spawn payload format if the skill spawns subagents

## When to use

- Adding a new workflow skill to the plugin (e.g., a project-specific workflow)
- Adding a knowledge skill to the plugin
- Adding a companion utility skill

Not for: general-purpose Anthropic skill creation — use the upstream `skill-creator` for that. This scaffold ONLY targets plugin-convention skills under `plugin/skills/`.

## Invocation

```
/plugin-skill-create new-workflow --invocable --agent-spawn
/plugin-skill-create analyzer --type knowledge
/plugin-skill-create release-notes --type companion --invocable
```

## Arguments

| Flag | Default | Effect |
|---|---|---|
| `<name>` (positional) | required | Lowercase + hyphens; ≤64 chars; must NOT clash with existing `plugin/skills/<name>/` |
| `--type` | `workflow` | `workflow` (full SDLC stage), `knowledge` (read-only reference), `companion` (helper) |
| `--invocable` | true (workflow + companion); false (knowledge) | Adds `context: fork` for slash invocation |
| `--agent-spawn` | off | Pre-wires G7 spawn payload section + return contract validation |
| `--ralph` | off | Pre-wires RALF Loop section per `ralph-budget.md` defaults |
| `--memory L4|L5` | off | Pre-wires memory write points per `memory-discipline.md` rule 1 |

## Behavior

1. Validate `<name>`:
   - Lowercase + hyphens only (per Anthropic skill name convention from docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices)
   - ≤64 chars
   - Does NOT collide with existing `plugin/skills/<name>/`
   - If collision: error and suggest `--overwrite` flag (but this skill never overwrites by default — minimum-change discipline)
2. Generate `plugin/skills/<name>/SKILL.md` with H5 frontmatter:

```yaml
---
name: <name>
description: TODO — replace this placeholder. One sentence describing what the skill does. Use when <TODO: trigger phrase>.
context: fork           # if --invocable
argument-hint: "<arg>"  # if --invocable
disable-model-invocation: true  # if --type knowledge AND not --invocable
---
```

The `TODO —` token is a hard guard: `plugin-skill-audit` fails (CRITICAL severity) on any skill description that still contains `TODO`. This forces the scaffolded description to be edited before merge. Removing the literal `TODO` from your description is the gate that flips the audit from failing to passing.

3. Generate body skeleton:
   - `# /<name>` heading
   - Purpose section (placeholder)
   - When to use / Not for sections
   - Invocation examples (placeholder)
   - Arguments table (placeholder)
   - Behavior steps
   - Hard rules
   - Failure modes
   - Memory writes table (if `--memory`)
   - RALF Loop section (if `--ralph`)
   - G7 Spawn Payload + Return Contract section (if `--agent-spawn`)
   - Integration section: rules, hooks, schemas, companions

4. Generate `plugin/eval/cases/<name>/eval-case-001.json` stub (Tier 3):

```json
{
  "case_id": "<name>-001",
  "skill": "<name>",
  "input": {"prompt": "<test prompt>"},
  "expected": {"contains": ["<expected substring>"]},
  "judge_rubric": "plugin/eval/judge-rubrics/<name>.md",
  "judge_model": "haiku",
  "max_tokens_input": 30000,
  "max_tokens_output": 2000
}
```

5. Generate `plugin/eval/judge-rubrics/<name>.md` skeleton with the standard 5-dimension template.

6. Print summary: created files + next steps:
   - Fill placeholder content
   - Run `/plugin-skill-audit <name> --strict` to confirm spec compliance
   - Run `/eval --skill <name> --tier 1`

## Hard rules

Every scaffolded skill MUST satisfy the agentskills.io specification + ai-assets conventions below. The audit counterpart `/plugin-skill-audit` enforces the same rules — anything this skill emits MUST pass `/plugin-skill-audit <name> --strict`.

### agentskills.io specification (https://agentskills.io/specification)

- **`name`**: 1–64 chars; lowercase a–z, digits, hyphens only; MUST NOT start or end with hyphen; MUST NOT contain consecutive hyphens (`--`); MUST equal the parent directory name
- **`description`**: 1–1024 chars (hard limit); non-empty; describes BOTH what the skill does AND when to use it; includes trigger keywords; uses imperative phrasing
- **Directory**: `SKILL.md` is required; optional `scripts/`, `references/`, `assets/` for progressive disclosure
- **Body**: ≤ 5000 tokens AND ≤ 500 lines recommended; keep file references one level deep from `SKILL.md`

### agentskills.io best practices (https://agentskills.io/skill-creation/best-practices)

- **Add what the agent lacks, omit what it knows** — no "what is a PDF" filler
- **Pick a default, not a menu** — when multiple tools work, name one default and mention alternatives briefly
- **Procedures over declarations** — teach how to approach a class of problems, not what to produce for one instance
- **Match specificity to fragility** — flexible for tolerant tasks; prescriptive for fragile sequences
- **Progressive disclosure** — long reference material moves to `references/`, with explicit "load when X" triggers in `SKILL.md`
- **Gotchas section** when the skill has non-obvious environment-specific facts
- **Validation loops** for multi-step workflows (do work → run validator → fix → repeat)

### agentskills.io description rules (https://agentskills.io/skill-creation/optimizing-descriptions)

- **Imperative phrasing** — "Use this skill when…" not "This skill does…"
- **User-intent focus** — describe what the user is trying to achieve, not internal mechanics
- **Be pushy** — list contexts explicitly, including ones where the user does not name the domain directly
- **Concise** — a few sentences to a short paragraph; well under the 1024-char hard limit

### ai-assets plugin conventions

- **Body ≤ 12K chars** per project rule (matches the upstream ≤500-line recommendation)
- **Description in third person** — first-person breaks discovery
- **`Use when` trigger pattern** present in every description (H5 convention)
- **Never overwrite** existing skill — refuse if `plugin/skills/<name>/` already exists
- **Plugin-only scope** — never scaffolds skills outside `plugin/skills/`. For project-local skills use upstream `skill-creator`
- **English-only** per repo CLAUDE.md
- **No absolute user-machine paths** in templates or examples

## Failure modes

- **Name collision:** refuse, suggest different name
- **Name fails validation:** refuse with examples of valid names (e.g., `release-notes`, NOT `Release Notes` or `releasenotes`)
- **Permission denied on write:** report path; suggest checking plugin/ writeability

## Memory writes

| Layer | When | Shape |
|---|---|---|
| L4 | After scaffold | `.ai-assets-memory/plugin-skills/<name>/scaffolded.md` — timestamp + flags used |

## Integration

- **Status**: internal procedure document for `/plugin-author create`. Not slash-invocable (frontmatter `disable-model-invocation: true`). The umbrella reads this file directly when scaffolding a new asset; `ai-assets:prompt-engineer` pre-reads it before any plugin-asset DEV pass.
- **Reachable via**: `/plugin-author create <name> [--type workflow|knowledge|companion] [--agent-spawn] [--ralph]`
- **Writes to**: `plugin/skills/<name>/`, `plugin/eval/cases/<name>/`, `plugin/eval/judge-rubrics/<name>.md`
- **References**:
  - agentskills.io specification — https://agentskills.io/specification
  - agentskills.io best practices — https://agentskills.io/skill-creation/best-practices
  - agentskills.io description optimization — https://agentskills.io/skill-creation/optimizing-descriptions
  - Anthropic Agent Skills best-practices — https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices
- **Templates**: H5 frontmatter pattern, G7 schemas (if `--agent-spawn`), `ralph-budget.md` defaults (if `--ralph`)
- **Companion procedure**: `plugin/skills/plugin-skill-audit/SKILL.md` — audit + safe-fix discipline applied by `/plugin-author audit`.
