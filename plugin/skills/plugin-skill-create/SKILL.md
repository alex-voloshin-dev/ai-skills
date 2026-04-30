---
name: plugin-skill-create
description: Scaffold a new skill INSIDE the ai-assets plugin (under plugin/skills/) with H5 frontmatter, eval test-case stub, and memory-write points pre-wired. Narrower than Anthropic's general skill-creator — this scaffolds plugin-convention-aligned skills only. Use when extending the plugin with a new workflow or companion.
context: fork
argument-hint: "<skill-name> [--invocable] [--type knowledge|workflow|companion]"
---

# /plugin-skill-create — Plugin-Convention Skill Scaffold

Generate `plugin/skills/<name>/SKILL.md` plus eval/case stub plus memory-hook scaffolding. Conforms to ai-assets plugin conventions: H5 frontmatter trigger pattern, schema-validated frontmatter, `<untrusted_content>` G1 wrapping where applicable, G7 spawn payload format if the skill spawns subagents.

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
description: <one-sentence description; placeholder>. Use when the user <trigger phrase>.
context: fork           # if --invocable
argument-hint: "<arg>"  # if --invocable
disable-model-invocation: true  # if --type knowledge AND not --invocable
---
```

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

6. Print summary: created files + next steps (fill placeholders, run `/eval --skill <name> --tier 1`).

## Hard rules

- **Lowercase + hyphens only** for skill names per Anthropic best-practices doc
- **Body ≤ 12K chars** per project rule (matches Anthropic recommendation of ≤500 lines for optimal performance)
- **Description must include `Use when`** trigger pattern (H5)
- **Description in third person** per Anthropic best-practices doc — first-person breaks discovery
- **Never overwrite** existing skill — refuse if `plugin/skills/<name>/` already exists
- **Plugin-only scope** — never scaffolds skills outside `plugin/skills/`. For project-local skills use upstream `skill-creator`

## Failure modes

- **Name collision:** refuse, suggest different name
- **Name fails validation:** refuse with examples of valid names (e.g., `release-notes`, NOT `Release Notes` or `releasenotes`)
- **Permission denied on write:** report path; suggest checking plugin/ writeability

## Memory writes

| Layer | When | Shape |
|---|---|---|
| L4 | After scaffold | `.ai-assets-memory/plugin-skills/<name>/scaffolded.md` — timestamp + flags used |

## Integration

- **Writes to**: `plugin/skills/<name>/`, `plugin/eval/cases/<name>/`, `plugin/eval/judge-rubrics/<name>.md`
- **References**: Anthropic skill-creator best-practices doc (https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices)
- **Templates**: H5 frontmatter pattern, G7 schemas (if `--agent-spawn`), `ralph-budget.md` defaults (if `--ralph`)
- **Companion**: upstream `skill-creator` for general (non-plugin) skill scaffolding
