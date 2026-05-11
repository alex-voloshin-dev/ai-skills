# ai-assets — Claude Code Plugin

A reusable team-of-agents plugin for the full software development lifecycle. Drives feature design, implementation, bugfixing, environment analysis, and refactoring through coordinated subagents, with built-in iteration loops (RALF), layered memory, and systematic eval.

**Project-agnostic by design.** Operations live in this plugin; project-specific context (brand, conventions, terminology) lives in the target repo's `CLAUDE.md` / `AGENTS.md` / `marketing/MARKETING.md` and is read at runtime.

## Status — v0.3.7

Current release. The plugin is the canonical Claude Code delivery format for this repository (the legacy `.claude/` mirror was retired in v0.2.0). Codex and Windsurf packages remain alongside for those runtimes; parity is enforced between Codex and Windsurf only.

For existing `~/.claude/` install users from before v0.2.0, switch to:

```bash
claude --plugin-dir /path/to/ai-assets/plugin
```

After cleaning up the old install: `rm -rf ~/.claude/agents ~/.claude/skills ~/.claude/rules ~/.claude/hooks ~/.claude/settings.json` (preserve any of your own personal `~/.claude/` content first).

The local validator (`python3 plugin/dev/validate.py`) passes 23 checks against the live tree.

| Component | Count | Notes |
|---|---|---|
| Hooks | 18 | Across 13 lifecycle events; includes ralph-iter-meter (v0.1.6) and subagent-depth-guard (v0.1.7) |
| Agents | 26 | 22 normalized roles + 4 orchestrators |
| Rules | 12 | Security, memory discipline, RALF budget, untrusted-content wrapping, etc. |
| Skills | 53 | 32 user-invocable (28 with `context: fork` + 4 main-thread orchestrators); rest are background knowledge loaded as context |
| JSON schemas | 2 | G7 spawn payload + return contract |
| Memory templates | 6 | In `memory/templates/` (`pii-patterns.txt` lives at `hooks/scripts/pii-patterns.txt` so `_lib.py` can load it) |
| Eval rubrics | 45 | 17 base + 4 meta-tools + 24 per-skill workflow rubrics |
| Calibration samples | 270 | 6 per rubric (3 good + 3 bad) × 45 |
| Output styles | 2 | `concise-pr`, `design-pack` |
| User docs | 15 | 1 getting-started + 10 workflows + 4 concepts |
| Workflows (`/<command>`) | 10 | Primary user-invocable workflows |
| Companion skills | 9 | Named user-invocable companions |
| userConfig knobs | 13 | Declarative configuration |

Distribution: local install via `claude --plugin-dir <path>` (Anthropic-canonical for development). Marketplace install via `/plugin marketplace add <repo-url>` once published.

## Install

### Local development (recommended)

Per [official Anthropic docs](https://docs.claude.com/en/docs/claude-code/plugins), the canonical way to use a plugin from a local path is the `--plugin-dir` flag:

```bash
# Start Claude Code with the plugin loaded for this session
claude --plugin-dir /path/to/ai-assets/plugin

# After editing plugin files, reload without restarting:
/reload-plugins
```

All 32 user-invocable skills appear in `/help` under the `ai-assets:` namespace, e.g. `/ai-assets:feature-design`, `/ai-assets:develop`, `/ai-assets:plugin-doctor`. Plugin namespacing is automatic per Anthropic spec — prevents conflicts when multiple plugins ship same-named skills.

### Future: marketplace distribution (after GitHub publish)

Once the plugin is pushed to GitHub, install via the official marketplace flow:

```text
/plugin marketplace add alex-voloshin-dev/ai-assets
/plugin install ai-assets@ai-assets
```

The repo's `.claude-plugin/marketplace.json` already declares the registry. Local marketplace install (`/plugin marketplace add <local-path>`) is supported by Claude Code in principle but currently brittle for same-host development on v2.1.x — use `--plugin-dir` instead.

## Workflows (10 user-invocable)

| Slash command | What it does |
|---|---|
| `/feature-design` | Multi-agent design pack from a 1-3 sentence idea (PRD + ARD + UX + impl plan) |
| `/develop` | Full SDLC implementation from a design pack (DEVELOP → REVIEW → QA pipeline) |
| `/bugfix` | Triage, diagnose, fix, ship — with reproduction-test RALF loop |
| `/env-analyze` | Standalone diagnostic for Docker / K8s / CI environments |
| `/refactor` | Plan and execute refactor across N files with safety nets |
| `/migrate` | Schema/library/version migration with rollback plan |
| `/spike` | Time-boxed exploration with go/no-go writeup |
| `/security-audit` | OWASP Web Top 10 + GenAI Top 10 audit + remediation plan |
| `/docs-pack` | Generate user-facing docs (README, API ref, runbook) |
| `/ai-assets-init` | Bootstrap a target repo to be ai-assets-aware |

## Companion skills (9)

`/ralph` (power-user RALF entry) · `/eval` (skill/agent evaluator) · `/plugin-doctor` (self-diagnostic) · `/memory-init` · `/memory-recall` · `/learnings-write` · `/context-load` · `/subagent-spawn` · `/plugin-skill-create`

## What's inside today (v0.3.7)

- **73 skills** covering the full SDLC plus marketing and content. 36 are user-invocable: 32 with `context: fork` plus 4 main-thread orchestrators (`develop`, `feature-design`, `bugfix`, `team-bugfix`) that retain Agent-spawn capability. The remaining 37 are knowledge skills (`disable-model-invocation: true`) loaded as context by workflows or agents — Single-Responsibility split per the May 2026 `/plugin-skill-audit` refactor (split fat workflows, extract per-stack tooling tables, thin engineer agents via the `prompt-engineer` pattern).
- **26 specialized agents** — cloud architect, security engineer, all major language engineers, content/marketing roles, 4 orchestrators.
- **18 hooks** across 13 lifecycle events — security guardrails, untrusted-content wrapping, session memory flush, RALF loop control, per-iteration token meter (v0.1.6), subagent depth guard (v0.1.7), `.committed/` allowlist enforcement.
- **12 rules** — security, memory discipline, RALF budget, untrusted-content wrapping, etc.
- **45 eval rubrics + 270 calibration samples + Tier 1 linter + Tier 2 judge-calibration smoke** for systematic regression detection. Tier 2 added in v0.1.4 and requires `ANTHROPIC_API_KEY`. Tier 3 is planned but not yet shipped (runner returns error code 3 if invoked).
- **G1/G2 attack-surface validation (v0.1.5)** — 6 indirect-prompt-injection fixtures plus a structural runner that confirms the `<untrusted_content>` envelope wraps attacker-planted instructions across 5 attack vectors (poisoned `CLAUDE.md`, malicious env logs, poisoned learnings, bash role-switch, poisoned PRD). 1 fixture documents the sub-200-token wrap-skip design tradeoff. Optional behavioral mode round-trips wrapped payloads through Haiku to verify no compliance escape.
- **Per-iteration RALF token measurement (v0.1.6)** — `ralph-iter-meter.py` PostToolUse hook estimates tokens per tool call (chars/4) and accumulates while a RALF run is active. `ralph-stop.py` consumes the per-iter accumulator on each Stop intercept, persists `iter-NNN/tokens.json`, and fires a runaway warning when a single iteration exceeds 3× fair share (`token_budget / max_iterations`). Closes the v0.1 gap where session-aggregate token caps only fired inside Tier 3 eval runs.
- **Defensive subagent depth-guard (v0.1.7)** — `subagent-depth-guard.py` SubagentStart hook walks the `parent_trace_id` chain in G7 spawn payloads, computes spawn depth, and blocks at `depth > userConfig.subagent_max_depth` (default 3). Logs every `start`/`stop`/`rejected` event to `.ai-assets-memory/sessions/<sid>/spawn-chain.jsonl`. Anthropic's runtime enforces depth=1 max; this is the defensive backstop in case orchestration accidentally bypasses or future versions add Task to additional agents.
- **2 output styles** — `concise-pr` for PR descriptions, `design-pack` for `/feature-design` artefacts.
- **13-knob declarative config** + 0 external dependencies (fully standalone).

## Learn more

- [docs/getting-started.md](docs/getting-started.md) — 30-min tutorial (install + first feature design)
- [docs/workflows/](docs/workflows/) — one user doc per slash command (10 files)
- [docs/concepts/memory.md](docs/concepts/memory.md) — 6-layer memory model summary
- [docs/concepts/eval.md](docs/concepts/eval.md) — eval framework summary
- [docs/concepts/ralf.md](docs/concepts/ralf.md) — RALF iteration loop summary
- [docs/concepts/skill-frontmatter-extensions.md](docs/concepts/skill-frontmatter-extensions.md) — the 4 Claude Code-specific frontmatter fields and how they relate to the agentskills.io spec
- [CHANGELOG.md](CHANGELOG.md) — version history per batch

## License

MIT
