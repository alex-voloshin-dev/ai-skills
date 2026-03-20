# Architecture

## System Type

This is a non-code asset repository. It contains configuration files for three AI coding assistant runtimes. There is no application code, no database, no API, and no CI/CD pipeline.

## Design Philosophy

One source of truth for AI assistant behavior across Claude Code, OpenAI Codex, and Codeium Windsurf. Each runtime has different primitives, so the repository translates a single set of capabilities into three runtime-native representations rather than forcing identical file structures.

## Package Architecture

```
┌─────────────────────────────────────────────────┐
│                  ai-assets repo                  │
│                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐  │
│  │ .claude/  │  │ .codex/  │  │ .windsurf/   │  │
│  │          │  │          │  │              │  │
│  │ agents   │←→│ roles    │←→│ rules/roles  │  │
│  │ skills   │←→│          │←→│ skills       │  │
│  │ rules    │←→│ rules    │←→│ rules        │  │
│  │ hooks    │  │ ops*     │  │ hooks        │  │
│  │ templates│  │ templates│  │ (in skills)  │  │
│  │ settings │  │ config   │  │ hooks.json   │  │
│  └──────────┘  └──────────┘  └──────────────┘  │
│       ↑                                          │
│  ┌────┴─────┐                                    │
│  │ .agents/ │  shared skill bodies               │
│  │ skills/  │  (Codex + Windsurf read these)     │
│  └──────────┘                                    │
│                                                  │
│  * Codex has no native hooks; operations          │
│    document hook intent for manual enforcement    │
└─────────────────────────────────────────────────┘
```

## Primitive Mapping

| Capability | Claude Code | Codex | Windsurf |
|---|---|---|---|
| Role definition | `.claude/agents/*.md` (frontmatter: name, description, tools, model) | `.codex/roles/*.md` | `.windsurf/rules/roles/**/*.role.md` |
| Reusable knowledge | `.claude/skills/*/SKILL.md` | `.agents/skills/*/SKILL.md` | `.windsurf/skills/*/SKILL.md` |
| User-invocable procedure | Skill with `context: fork` | Skill with invocation instructions | `.windsurf/workflows/**/*.md` |
| Guardrail rule | `.claude/rules/*.md` | `.codex/rules/*.md` | `.windsurf/rules/*.md` |
| Runtime enforcement | Python hook scripts (exit 2 = block) | Documented intent in `.codex/operations/hook-intents.md` | Python hook scripts (same as Claude) |
| Hook wiring | `settings.json` + `hooks/configs/*.json` | N/A | `hooks.json` + `hooks/configs/*.json` |
| Scaffolding | `.claude/templates/*.template.md` | `.codex/templates/*.template.md` | Embedded in skill resource directories |

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
- `user-invocable` — `true`/`false`, or use `context: fork`
- `argument-hint` — usage hint for invocation
- `disable-model-invocation` — `true` for non-AI skills like `pre-commit`

Skills fall into three categories:
1. **Engineering workflows** — bugfix, feature-dev, deploy, testing, security
2. **Content workflows** — blog-post, docs, marketing, content-creation, humanizer
3. **Background knowledge** — cloud-platforms, context-engineering, prompt-engineering

## Hook Architecture

Four Python scripts handle runtime enforcement:

```
hooks/scripts/
├── block-dangerous-commands.py   # PreToolUse(Bash)
├── block-secrets-in-code.py      # PreToolUse(Write|Edit)
├── block-sensitive-files.py      # PreToolUse(Read)
└── log-actions.py                # PostToolUse(*)
```

All scripts share a `_normalize_hook_input()` function that bridges old and new hook payload formats. Scripts read JSON from stdin and exit with code 0 (allow) or 2 (block with reason on stdout).

Hook configs in `hooks/configs/` wire scripts to events. `settings.json` maps these at the Claude runtime level.

## Installation Flow

```
ai-assets repo
     │
     ├── install.sh (bash)    ─┐
     │                          ├─→ rsync/robocopy to ~/
     └── install.ps1 (pwsh)   ─┘    then rewrite hook paths
                                      in settings.json to use
                                      absolute ~/... paths
```

The installers:
1. Sync `.claude/`, `.agents/`, `.codex/`, `.windsurf/` to `~/`
2. Remove stale files in target directories
3. Rewrite hook `command` fields from relative to absolute paths (`python3 "~/.claude/hooks/scripts/..."`)

## Parity Enforcement

`review/parity-matrix.md` is the authoritative record of cross-package alignment. It tracks:
- Current parity status per capability area (roles, skills, rules, workflows, templates)
- Change log entries for parity-impacting additions
- Review rules that must be followed for any change

Any change that adds, removes, or modifies a capability in one package must be reflected in all three packages in the same changeset.

## Key Constraints

- No application code — this repo produces no deployable artifacts
- All Markdown assets must stay under 12,000 characters
- All content must be in English
- No project-specific references in shared assets
- Hook scripts must work both as project-local (`.claude/hooks/scripts/`) and global (`~/.claude/hooks/scripts/`)
- Windsurf stores templates inside skill resource directories rather than a top-level `templates/` primitive
