# Cross-Vendor Parity

This repository maintains capability parity across three AI coding assistant runtimes:
**Claude Code**, **OpenAI Codex**, and **Codeium Windsurf**. This document explains how
parity works, what the current state is, and where intentional gaps exist.

For the full change log, see [review/parity-matrix.md](review/parity-matrix.md).

## How parity works

Parity means equivalent capability coverage, not file-for-file duplication. Each runtime
has different primitives, so the same capability takes a different shape in each package.

### Primitive mapping

| Capability | Claude Code | Codex | Windsurf |
|---|---|---|---|
| **Roles** | `.claude/agents/*.md` | `.codex/roles/*.md` | `.windsurf/rules/roles/**/*.role.md` |
| **Skills** | `.claude/skills/*/SKILL.md` | `.agents/skills/*/SKILL.md` | `.windsurf/skills/*/SKILL.md` |
| **User workflows** | user-invocable skills (`context: fork`) | user-invocable skills | `.windsurf/workflows/**/*.md` |
| **Rules** | `.claude/rules/*.md` | `.codex/rules/*.md` | `.windsurf/rules/*.md` |
| **Hooks** | `.claude/hooks/scripts/*.py` + `settings.json` | `.codex/operations/hook-intents.md` (documented intent) | `.windsurf/hooks/scripts/*.py` + `hooks.json` |
| **Templates** | `.claude/templates/*.template.md` | `.codex/templates/*.template.md` | Embedded in skill resources |
| **Config** | `.claude/settings.json` | `.codex/config.toml` | `.windsurf/hooks.json` |

### The source of truth flow

```
Claude (.claude/) ── source of truth
    │
    ├── Codex (.codex/) ── roles derived from Claude agents,
    │   │                   rules aligned to Claude rules,
    │   │                   operations document Claude hook intent
    │   └── .agents/skills/ ── shared skill corpus (Codex-native wording)
    │
    └── Windsurf (.windsurf/) ── roles derived from Claude agents,
        │                        rules aligned to Claude rules,
        │                        hooks mirror Claude hooks
        └── .windsurf/skills/ ── skills from .agents/skills/ with Windsurf frontmatter
            .windsurf/workflows/ ── user-facing procedures from Claude skills
```

Claude is the primary authoring surface. When a capability is added or changed in Claude,
the corresponding Codex and Windsurf assets must be updated in the same changeset.

## Current parity status

### Roles: 22 / 22 / 22

Full parity. Every role exists across all three packages.

| Category | Roles |
|---|---|
| Architects (4) | cloud-architect, devops-architect, solution-architect, system-architect |
| Engineers (12) | data-engineer, db-engineer, devops-engineer, frontend-engineer, java-engineer, ml-engineer, mobile-engineer, python-engineer, qa-engineer, seo-engineer, software-engineer, sre-engineer |
| Designers (2) | content-designer, ui-ux-designer |
| Other (4) | content-writer, marketing-strategist, product-manager, prompt-engineer |

### Skills: 40 / 38 / 38

38 skills in full parity. 2 skills are intentionally Claude-only (see Intentional Gaps below).

### Rules: 7 / 8 / 7

Semantic parity. Codex carries one additional `README.md` and organizes rules differently,
but the guardrail coverage matches across all runtimes.

### Hooks: 4 scripts

Hook scripts (`block-dangerous-commands.py`, `block-secrets-in-code.py`,
`block-sensitive-files.py`, `log-actions.py`) are identical in Claude and Windsurf.
Codex documents hook intent in `.codex/operations/hook-intents.md` because Codex
has no native hook execution.

### Workflows: 26

All 26 Windsurf workflows have corresponding user-invocable skills in Claude.

## Intentional gaps

Some capabilities exist in only one runtime because the underlying runtime primitive
has no equivalent elsewhere. These are tracked here rather than treated as parity violations.

### Claude-only skills

| Skill | Reason |
|---|---|
| `multi-agent-orchestration` | Relies on Claude Code's native `Agent` tool for spawning named subagents with parallel execution. Codex and Windsurf have no equivalent runtime primitive. |
| `multi-agent-bugfix-audit` | Multi-agent coordinated bugfix workflow using Claude Code's parallel Agent spawning with developer/reviewer/QA pipeline. No equivalent in other runtimes. |

### Codex-specific assets

| Asset | Purpose |
|---|---|
| `.codex/rules/role-overlays/` | Codex applies role behavior through visible overlay rules rather than hidden agent invocation. This is a Codex-native pattern with no Claude/Windsurf equivalent needed. |
| `.codex/operations/skill-role-mapping.md` | Documents the Codex `skill -> codex-roles -> role overlay` routing pattern. |

### Windsurf-specific assets

| Asset | Purpose |
|---|---|
| `.windsurf/workflows/` | Windsurf separates user-facing procedures into workflow files. Claude bundles these into user-invocable skills. Both achieve the same result. |

## Adding new capabilities

When adding a new role, skill, or guardrail, follow this process:

1. **Author in Claude** (`.claude/`) first -- this is the source of truth
2. **Create Codex equivalent** in `.codex/roles/` or `.codex/rules/` and update `.agents/skills/` for shared skills
3. **Create Windsurf equivalent** in `.windsurf/rules/roles/`, `.windsurf/skills/`, and add a workflow file if the skill is user-invocable
4. **Update the parity matrix** in `review/parity-matrix.md` with a changelog entry
5. **Verify parity** by checking that the capability is accessible in all three runtimes

### Parity review checklist

- [ ] Capability exists in all three packages (or is documented as an intentional gap)
- [ ] Runtime-native representations used (no forced file mirroring)
- [ ] Shared skills in `.agents/skills/` use Codex-native wording
- [ ] Windsurf workflow added if the Claude skill is user-invocable
- [ ] No project-specific references in any package
- [ ] Parity matrix changelog updated

## Validation

Run a parity check by comparing asset inventories:

```bash
# Count skills per package
ls -d .claude/skills/*/  | wc -l
ls -d .agents/skills/*/  | wc -l
ls -d .windsurf/skills/*/ | wc -l

# Count roles per package
ls .claude/agents/*.md    | wc -l
ls .codex/roles/*.md      | grep -v README | wc -l
find .windsurf/rules/roles -name '*.role.md' | wc -l

# Diff shared skill files
diff .claude/skills/<name>/SKILL.md .agents/skills/<name>/SKILL.md
diff .claude/skills/<name>/SKILL.md .windsurf/skills/<name>/SKILL.md
```

Full automated validation is tracked in [review/parity-matrix.md](review/parity-matrix.md).
