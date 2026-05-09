# Architecture

## System Type

This is a non-code asset repository. It contains AI coding assistant configuration in two delivery formats: a Claude Code plugin (`plugin/`) and the legacy two-vendor packages for OpenAI Codex and Codeium Windsurf (`.codex/`, `.windsurf/`, shared `.agents/`). There is no application code, no database, no API, and no CI/CD pipeline.

## Design Philosophy

After v0.2.0 the repository ships two distinct delivery formats rather than mirroring one source of truth into three top-level packages. The Claude Code plugin (`plugin/`) is its own first-class artifact with native plugin primitives (manifest, hooks.json, schemas, eval rubrics, marketplace.json). The Codex and Windsurf packages stay in mirror-parity with each other through `.agents/skills/` (shared skill bodies) and per-runtime translations of the same roles + rules.

The legacy `.claude/` package was removed in v0.2.0; everything it carried lives in `plugin/` in plugin-native form.

## Package Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    ai-assets repo                       │
│                                                         │
│  ┌────────────────────────────────────────────────────┐ │
│  │ plugin/  (Claude Code plugin v0.2.0+)              │ │
│  │  agents/  skills/  rules/  hooks/  schemas/        │ │
│  │  eval/  docs/  dev/validate.py                     │ │
│  │  .claude-plugin/plugin.json   (manifest)            │ │
│  └────────────────────────────────────────────────────┘ │
│                                                         │
│  ┌────────────┐    ┌────────────────┐                   │
│  │ .codex/     │←→  │ .windsurf/     │  parity mirror   │
│  │ roles      │    │ rules/roles    │                   │
│  │ rules      │    │ rules           │                   │
│  │ ops*       │    │ hooks (scripts) │                   │
│  │ templates  │    │ workflows       │                   │
│  │ config     │    │ hooks.json      │                   │
│  └────────────┘    └────────────────┘                   │
│       ↑                   ↑                              │
│  ┌────┴───────────────────┴────┐                        │
│  │ .agents/skills/             │  shared skill bodies    │
│  └────────────────────────────┘                        │
│                                                         │
│  * Codex has no native hooks; .codex/operations/         │
│    hook-intents.md documents intent for manual          │
│    enforcement                                          │
└─────────────────────────────────────────────────────────┘
```

## Primitive Mapping

| Capability | Claude Code (plugin) | Codex | Windsurf |
|---|---|---|---|
| Role definition | `plugin/agents/*.md` | `.codex/roles/*.md` | `.windsurf/rules/roles/**/*.role.md` |
| Reusable knowledge | `plugin/skills/*/SKILL.md` | `.agents/skills/*/SKILL.md` | `.windsurf/skills/*/SKILL.md` |
| User-invocable procedure | Skill with `context: fork` + 4 main-thread orchestrators (32 in plugin) | Skill with invocation instructions | `.windsurf/workflows/**/*.md` |
| Guardrail rule | `plugin/rules/*.md` (12) | `.codex/rules/*.md` | `.windsurf/rules/*.md` |
| Runtime enforcement | `plugin/hooks/scripts/*.py` (18 across 13 events) + `hooks.json` | Documented intent in `.codex/operations/hook-intents.md` | `.windsurf/hooks/scripts/*.py` + `hooks.json` |
| Hook wiring | `plugin/hooks/hooks.json` | N/A | `.windsurf/hooks.json` |
| Scaffolding | n/a (templates folded into skill resources or plugin docs/) | `.codex/templates/*.template.md` | Embedded in skill resource directories |
| Eval framework | `plugin/eval/` — 45 rubrics + 270 calibration samples + Tier 1 linter + Tier 2 judge-calibration smoke + g1g2 attack-surface (Tier 3 planned, not yet shipped) | n/a | n/a |

## Skill Architecture

Each skill is a directory containing:

```
<skill-name>/
├── SKILL.md              # main skill file (YAML frontmatter + body)
└── <resource>.md         # optional companion resources
```

Frontmatter fields:
- `name` — skill identifier
- `description` — one-line summary (used for routing)
- `context: fork` — marks user-invocable workflow (called via `/<skill-name>`)
- `argument-hint` — usage hint for invocation
- `disable-model-invocation` — `true` for non-AI skills like `pre-commit`

Plugin skills fall into three categories:
1. **Engineering workflows** — bugfix, feature-design, develop, deploy, testing, security
2. **Content workflows** — blog-post, docs-pack, marketing-strategist
3. **Background knowledge / orchestration** — context-engineering, subagent-spawn, ralph

## Hook Architecture

In the plugin (`plugin/hooks/scripts/`, 18 hooks + `_lib.py` shared module):

Security & audit (PreToolUse / PostToolUse):
- `block-dangerous-commands.py`, `block-secrets-in-code.py`, `block-sensitive-files.py`
- `pre-tool-use-committed-write.py` — `.committed/` allowlist enforcement
- `log-actions.py`, `tool-output-wrap.py`, `tool-output-normalize.py`
- `tool-failure-log.py`

Lifecycle:
- `session-start-context.py`, `session-end-finalize.py`, `instructions-loaded-augment.py`
- `pre-compact-memory-flush.py`, `task-event-log.py`

Subagent control (SubagentStart / SubagentStop):
- `subagent-start-budget.py`, `subagent-depth-guard.py` (v0.1.7), `subagent-stop-learnings.py`

RALF (Stop / PostToolUse):
- `ralph-stop.py`, `ralph-iter-meter.py` (v0.1.6)

All scripts share `_lib.py` for hook-input normalization, PII filtering, untrusted-content wrapping, token meter, RALF state, and active-spawn tracking. Scripts read JSON from stdin and exit with code 0 (allow) or 2 (block with reason on stdout).

In the Windsurf package (`.windsurf/hooks/scripts/`): four security/audit scripts (block-dangerous-commands, block-secrets-in-code, block-sensitive-files, log-actions) are mirrored from the plugin equivalents. Codex declares the same intent declaratively in `.codex/operations/hook-intents.md`.

## Installation Flow

```
┌────────────────────────────────────────────────────────┐
│ Claude Code:                                            │
│   claude --plugin-dir /path/to/ai-assets/plugin         │
│   (no copy, no patch — Claude Code reads plugin/        │
│    from the original path)                              │
│                                                        │
│ Codex + Windsurf:                                       │
│   ./install.sh   or   .\install.ps1                     │
│   sync .agents/, .codex/, .windsurf/ → ~/               │
└────────────────────────────────────────────────────────┘
```

The Codex+Windsurf installers:
1. Sync `.agents/`, `.codex/`, `.windsurf/` to `~/`
2. Remove stale files in target directories so the global packages stay aligned with the repo contents

(The legacy step "rewrite hook command paths in ~/.claude/settings.json" no longer applies — the plugin manages its own hook wiring via `${CLAUDE_PLUGIN_ROOT}` substitution at load time.)

## Parity Enforcement

See [PARITY.md](PARITY.md) for the full parity model.

After v0.2.0 parity is enforced between Codex and Windsurf only. Claude Code lives in `plugin/` and follows its own internal organization with its own `dev/validate.py` (23 structural checks).

`review/parity-matrix.md` tracks the cross-package alignment for Codex ↔ Windsurf:
- Current parity status per capability area (roles, skills, rules, workflows, templates)
- Change log entries for parity-impacting additions
- Review rules that must be followed for any change

Any change that adds, removes, or modifies a capability in Codex must be reflected in Windsurf in the same changeset.

## Key Constraints

- No application code — this repo produces no deployable artifacts
- All Markdown assets must stay under 12,000 characters
- All content must be in English
- No project-specific references in shared assets
- Plugin hook scripts use `${CLAUDE_PLUGIN_ROOT}` substitution; Windsurf hook scripts work both as project-local and global (via installer-rewritten absolute paths)
- Windsurf stores templates inside skill resource directories rather than a top-level `templates/` primitive
