# Cross-Vendor Parity

This repository ships AI coding assistant configuration in two delivery formats. Parity is enforced **only** between Codex and Windsurf — Claude Code lives in `plugin/` and follows its own internal organization (no longer mirrored into a sibling top-level package).

For the Codex ↔ Windsurf change log, see [review/parity-matrix.md](review/parity-matrix.md). For Claude Code, see [plugin/CHANGELOG.md](plugin/CHANGELOG.md).

## How parity works (Codex ↔ Windsurf)

Parity means equivalent capability coverage, not file-for-file duplication. Codex and Windsurf each expose different runtime primitives, so the same capability takes a different shape in each package.

### Primitive mapping

| Capability | Codex | Windsurf |
|---|---|---|
| **Roles** | `.codex/roles/*.md` | `.windsurf/rules/roles/**/*.role.md` |
| **Skills** | `.agents/skills/*/SKILL.md` (shared with Windsurf) | `.windsurf/skills/*/SKILL.md` |
| **User workflows** | user-invocable skills | `.windsurf/workflows/**/*.md` |
| **Rules** | `.codex/rules/*.md` | `.windsurf/rules/*.md` |
| **Hooks** | `.codex/operations/hook-intents.md` (documented intent) | `.windsurf/hooks/scripts/*.py` + `hooks.json` |
| **Templates** | `.codex/templates/*.template.md` | Embedded in skill resources |
| **Config** | `.codex/config.toml` | `.windsurf/hooks.json` |

### Source of truth flow

```
.agents/skills/  ── shared skill corpus (read by both Codex and Windsurf)
       ↑
       │
.codex/  ←─→  .windsurf/   parity mirror
roles          rules/roles
rules          rules
ops*           hooks (scripts + hooks.json)
templates      workflows + skill-embedded templates
```

When a capability is added to or changed in either Codex or Windsurf, the other must be updated in the same changeset. The parity matrix (`review/parity-matrix.md`) tracks every change.

## Claude Code lives in plugin/

The Claude Code plugin (`plugin/`) is a first-class artifact with its own internal organization, manifest, hooks.json, schemas, and validator. It is **not** a parity target — it does not need to mirror the Codex/Windsurf packages, and changes to plugin assets do not need to land in `.codex/` or `.windsurf/`.

This was the v0.2.0 transition: before v0.2.0, the repo enforced three-way parity across `.claude/ + .codex/ + .windsurf/`. The `.claude/` package was retired because the plugin format superseded it with native plugin primitives (manifest, eval framework, schemas, namespaced skills, hook lifecycle events) that the legacy folder layout couldn't carry.

For Claude Code asset coverage, see [plugin/README.md](plugin/README.md) — 26 agents, 73 skills (36 user-invocable: 32 `context: fork` + 4 main-thread orchestrators), 18 hooks across 13 lifecycle events, 12 rules, 45 eval rubrics + 270 calibration samples, 2 schemas, 13 userConfig knobs.

## Current parity status (Codex ↔ Windsurf)

### Roles: 22 / 22

Full parity. Every role exists in both packages.

| Category | Roles |
|---|---|
| Architects (4) | cloud-architect, devops-architect, solution-architect, system-architect |
| Engineers (12) | data-engineer, db-engineer, devops-engineer, frontend-engineer, java-engineer, ml-engineer, mobile-engineer, python-engineer, qa-engineer, seo-engineer, software-engineer, sre-engineer |
| Designers (2) | content-designer, ui-ux-designer |
| Other (4) | content-writer, marketing-strategist, product-manager, prompt-engineer |

### Skills: 39 / 39

Full parity via shared `.agents/skills/`. Both Codex and Windsurf read the same skill bodies.

### Rules: 8 / 8

Semantic parity. Each side keeps its own README and organizes rules to fit its runtime, but guardrail coverage matches.

### Hooks: 4 scripts (Windsurf only) + intent docs (Codex)

Hook scripts (`block-dangerous-commands.py`, `block-secrets-in-code.py`, `block-sensitive-files.py`, `log-actions.py`) ship in Windsurf. Codex documents hook intent in `.codex/operations/hook-intents.md` because Codex has no native hook execution.

### Workflows: 27

All 27 Windsurf workflows have corresponding user-invocable skills in Codex.

## Intentional gaps

Some capabilities exist in only one runtime because the underlying primitive has no equivalent elsewhere.

### Codex-specific assets

| Asset | Purpose |
|---|---|
| `.codex/rules/role-overlays/` | Codex applies role behavior through visible overlay rules rather than hidden agent invocation. Codex-native pattern with no Windsurf equivalent needed. |
| `.codex/operations/skill-role-mapping.md` | Documents the Codex `skill -> codex-roles -> role overlay` routing pattern. |

### Windsurf-specific assets

| Asset | Purpose |
|---|---|
| `.windsurf/workflows/` | Windsurf separates user-facing procedures into workflow files. Codex bundles these into user-invocable skills. Both achieve the same result. |

### Plugin-only capabilities (Claude Code)

The plugin carries capabilities that are intentionally not mirrored to Codex/Windsurf because they depend on Claude Code-native primitives:

| Capability | Why plugin-only |
|---|---|
| RALF iteration loop (`/ralph` + `ralph-stop.py` + `ralph-iter-meter.py`) | Depends on Stop/PostToolUse lifecycle events |
| Subagent depth-guard + budget hooks | Depends on SubagentStart/SubagentStop events + Task tool spawn primitive |
| Untrusted-content wrapping (G1) | Depends on PostToolUse event piping |
| 45 eval rubrics + 270 calibration samples + Tier 1/Tier 2/g1g2 runners | Plugin-internal eval framework (rubrics + Haiku judge calibration) |
| `team-protocols`, `team-bugfix`, `develop`, `feature-design`, `bugfix` orchestration | Depend on Claude Code's Agent tool + optional Agent Teams flag |
| 73 skills × 36 user-invocable (32 `context: fork` + 4 main-thread orchestrators) | Plugin-namespaced via `ai-skills:` prefix per Anthropic spec |

Codex and Windsurf carry the simpler 4 carry-over hooks (security/audit only) plus the shared skill+role corpus.

## Adding new capabilities

### For Codex / Windsurf

1. **Decide primary location** — usually `.agents/skills/` for skills (read by both); `.codex/roles/` or `.codex/rules/` for Codex-specific role/rule; `.windsurf/rules/roles/` or `.windsurf/rules/` for Windsurf parallel
2. **Mirror to the other** — every Codex change must land a matching Windsurf change in the same commit (and vice versa)
3. **Update workflow file** in `.windsurf/workflows/` if the skill is user-invocable
4. **Update the parity matrix** in `review/parity-matrix.md` with a changelog entry
5. **Verify parity** by checking that the capability is accessible in both runtimes

### For Claude Code (plugin)

1. **Edit in `plugin/`** — agents in `plugin/agents/`, skills in `plugin/skills/<name>/SKILL.md`, rules in `plugin/rules/`, hooks in `plugin/hooks/scripts/`
2. **Update `plugin/dev/validate.py` `EXPECTED_COUNTS`** if the structural inventory changed
3. **Update `plugin/CHANGELOG.md` and bump `plugin/.claude-plugin/plugin.json` version** for any user-visible change
4. **Run `python3 plugin/dev/validate.py`** — must pass 23 checks
5. Do **not** mirror plugin changes to `.codex/` or `.windsurf/` — they are separate delivery formats

### Parity review checklist (Codex ↔ Windsurf only)

- [ ] Capability exists in both packages (or is documented as an intentional gap)
- [ ] Runtime-native representations used (no forced file mirroring)
- [ ] Shared skills in `.agents/skills/` use neutral wording (read by both runtimes)
- [ ] Windsurf workflow added if the skill is user-invocable
- [ ] No project-specific references in any package
- [ ] Parity matrix changelog updated

## Design direction: single-source generation (roadmap, not yet implemented)

> **Status: design intent.** The repo today still ships hand-maintained Codex + Windsurf packages as described above. This section records the target architecture and its hard limits, so the eventual migration stays honest about what it can and cannot deliver.

**Goal.** Make `plugin/` plus the marketplace manifest the only source of truth in the tracked tree. Author every asset once for Claude Code (the primary) and generate the Codex / Windsurf / GitHub Copilot packages at release time, instead of maintaining them by hand. Target end-user experience: minimal configuration (plug-and-play) per vendor.

**Why generation, not a universal file or runtime detection.** Two simpler ideas were considered and rejected:

- *One universal file per asset, each vendor ignoring the others' parts.* Works for body content (a model follows the relevant conditional branch) but not for discovery: each runtime hard-codes where it looks, so a file in `plugin/skills/` is never found by Windsurf or Copilot. It also multiplies context cost on every invocation and risks cross-contamination on weaker models.
- *Runtime detection of the host agent.* The mechanism that would detect and branch is itself vendor-specific — only Claude Code runs hooks/scripts. Codex and Copilot have no script runtime, so detection cannot run there.

A build step is therefore unavoidable: one generator reads `plugin/` and emits each vendor's tree into that vendor's expected path.

### Four-vendor primitive mapping (target)

| Capability | Claude Code (source) | Codex | Windsurf | GitHub Copilot |
|---|---|---|---|---|
| Project instructions | `CLAUDE.md` | `AGENTS.md` | `.windsurf/rules/` | `.github/copilot-instructions.md` |
| Invocable workflows | `skills/*` (`context: fork`) | `prompts/` | `.windsurf/workflows/` | `.github/prompts/*.prompt.md` |
| Background knowledge | knowledge skills | `AGENTS.md` body | `.windsurf/skills/` | `.github/instructions/*.instructions.md` |
| Roles / personas | `agents/*` | role overlays | `.windsurf/rules/roles/` | `.github/chatmodes/*.chatmode.md` |
| Guardrails | `rules/*` + hooks | `.codex/rules/*` | `.windsurf/rules/*` + hooks | instructions (advisory) |

`AGENTS.md` is the one converging cross-vendor standard (read by Codex, newer Windsurf, Copilot, and Claude Code via config). Workflows, roles, and hooks do not converge — they keep vendor-specific paths.

### Hard limits the migration cannot remove

- **No shared asset path** — assets must be packaged per runtime, not read from one tree.
- **Runtime machinery is Claude-Code-only** — `Agent` spawn, G7 schemas, RALF loops, and the eval framework have no equivalent; dependent skills degrade to advisory prose.
- **Hooks don't port fully** — full in Claude Code, security-only in Windsurf, none enforced in Codex/Copilot.
- **Orchestration falls back to single-agent** — multi-agent workflows (`/develop`, `/feature-design`, `/bugfix`) run as single-agent sequential prompts off Claude Code.

### PnP is asymmetric

Only Claude Code has a true plugin/marketplace install. The realistic floor for the others is one install command; Copilot assets are per-repository by nature.

| Vendor | Install | PnP level |
|---|---|---|
| Claude Code | marketplace / plugin | true plug-and-play |
| Codex | one installer script | one command |
| Windsurf | one installer script | one command |
| Copilot | `.github/*` committed per repo | per-repository |

## Validation

Run a parity check by comparing asset inventories:

```bash
# Count skills per package
ls -d .agents/skills/*/   | wc -l
ls -d .windsurf/skills/*/ | wc -l

# Count roles per package
ls .codex/roles/*.md       | grep -v README | wc -l
find .windsurf/rules/roles -name '*.role.md' | wc -l

# Diff shared skill files
diff .agents/skills/<name>/SKILL.md .windsurf/skills/<name>/SKILL.md
```

For Claude Code plugin validation:

```bash
python3 plugin/dev/validate.py
```

Full automated validation history is tracked in [review/parity-matrix.md](review/parity-matrix.md) for Codex/Windsurf and in [plugin/CHANGELOG.md](plugin/CHANGELOG.md) for the plugin.
