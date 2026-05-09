# ai-assets — Claude Code Plugin

A reusable team-of-agents plugin for the full software development lifecycle. Drives feature design, implementation, bugfixing, environment analysis, and refactoring through coordinated subagents, with built-in iteration loops (RALF), layered memory, and systematic eval.

**Project-agnostic by design.** Operations live in this plugin; project-specific context (brand, conventions, terminology) lives in the target repo's `CLAUDE.md` / `AGENTS.md` / `marketing/MARKETING.md` and is read at runtime.

## Status — v0.2.0 (released 2026-04-30, breaking)

Phase 5 milestone — sunset of legacy `.claude/` package. The repository previously shipped Claude Code assets in two parallel layouts: the legacy three-package mirror (`.claude/` + `.codex/` + `.windsurf/` + shared `.agents/`) and the new plugin format (`plugin/`). v0.2.0 retires the legacy `.claude/` package — the plugin is now the single canonical Claude Code delivery format. Codex and Windsurf packages remain (parity now enforced between those two only).

**Breaking change for existing `~/.claude/` install users.** `install.sh` and `install.ps1` no longer sync `.claude/`. Switch to:

```bash
claude --plugin-dir /path/to/ai-assets/plugin
```

After cleaning up the old install: `rm -rf ~/.claude/agents ~/.claude/skills ~/.claude/rules ~/.claude/hooks ~/.claude/settings.json` (preserve any of your own personal `~/.claude/` content first).

17 alpha iterations (alpha.13 → alpha.29) + 7 hotfix/feature patches (0.1.1 → 0.1.7) + 1 breaking release (0.2.0) and 4 full review rounds (Round 13/14/15/16). All Phase 2 batches per `../plugin-design/04-MIGRATION-CHECKLIST.md` are complete: B1-B13 + Rounds 11/12 cross-phase review passes. Validator passes **23 checks** with hook count 18, userConfig knobs 13, live smoke tests confirmed `/develop` orchestrates DEV→REVIEW→QA pipeline with plugin-namespaced subagents on **3 stacks** — Java + Spring Boot, Python + FastAPI, Next.js + TypeScript.

| Component | Implemented | v0.1 target | Pending |
|---|---|---|---|
| Hooks | **18** (4 carried + 12 new + 1 v0.1.6 ralph-iter-meter + 1 v0.1.7 subagent-depth-guard) across 13 lifecycle events | 16 | — |
| Agents | **26** (22 normalized + 4 new) | 26 | — |
| Rules | **12** (8 carried + 4 new) | 12 | — |
| Skills | **52** (20 KEEP + 13 REFACTOR + 17 NEW + 2 MERGE) | 52 | — (target met) |
| JSON schemas | **2** (G7 spawn + return) | 2 | — |
| Memory templates | **7** in `memory/templates/` (+ `pii-patterns.txt` co-located in `hooks/scripts/` for hook loading) | 7 | — |
| Eval rubrics | **17** + Tier 1 linter (`runner.py`) | 17 | — (target met) |
| Calibration samples | **102** (3 good + 3 bad per rubric × 17) | 102 (alpha.16 HIGH-A) | full Phase 3 target met |
| Output styles | **2** (`concise-pr`, `design-pack`) | 2 | — (target met) |
| User docs | **14** (1 getting-started + 10 workflows + 3 concepts) | 14 | — (target met) |
| Workflows (`/<command>`) | **10** primary user-invocable | 10 | — (target met) |
| Companion skills | **9** named user-invocable | 9 | — (target met) |
| Extended fork-skills | **9** additional `/<command>`-invocable | n/a | 3 orchestration skills (develop, team-bugfix, feature-design) run in main thread per alpha.25; total user-invocable = **31** (28 with `context: fork` + 3 main-thread orchestrators) |

All structural deliverables shipped. The plugin installs, all 10 user-invocable workflows + 9 companion skills + 12 extended fork-skills (31 total user-invocable) are present, all 16 hooks wire into 13 lifecycle events, all 17 rubrics + 102 calibration samples are in place, all 14 user docs are in place. Local install via `claude --plugin-dir <path>` (Anthropic-canonical for development); marketplace install via `/plugin marketplace add <repo-url>` once published.

## Install

### Local development (recommended for v0.1)

Per [official Anthropic docs](https://docs.claude.com/en/docs/claude-code/plugins), the canonical way to use a plugin from a local path is the `--plugin-dir` flag:

```bash
# Start Claude Code with the plugin loaded for this session
claude --plugin-dir /path/to/ai-assets/plugin

# After editing plugin files, reload without restarting:
/reload-plugins
```

All 31 user-invocable skills appear in `/help` under the `ai-assets:` namespace, e.g. `/ai-assets:feature-design`, `/ai-assets:develop`, `/ai-assets:plugin-doctor`. Plugin namespacing is automatic per Anthropic spec — prevents conflicts when multiple plugins ship same-named skills.

### Future: marketplace distribution (after GitHub publish)

Once the plugin is pushed to GitHub, install via the official marketplace flow:

```text
/plugin marketplace add alex-voloshin/ai-assets
/plugin install ai-assets@ai-assets
```

The repo's `.claude-plugin/marketplace.json` already declares the registry. **Local marketplace install** (`/plugin marketplace add <local-path>`) is supported by Claude Code in principle but currently brittle for same-host development on v2.1.x — use `--plugin-dir` instead.

## Workflows (10 user-invocable)

| Slash command | What it does |
|---|---|
| `/feature-design` | Multi-agent design pack from a 1-3 sentence idea (PRD + ARD + UX + impl plan) |
| `/develop` | Full SDLC implementation from a design pack (DEVELOP → REVIEW → QA pipeline) |
| `/bugfix` | Triage → diagnose → fix → ship, with reproduction-test RALF loop |
| `/env-analyze` | Standalone diagnostic for Docker / K8s / CI environments |
| `/refactor` | Plan + execute refactor across N files with safety nets |
| `/migrate` | Schema/library/version migration with rollback plan |
| `/spike` | Time-boxed exploration with go/no-go writeup |
| `/security-audit` | OWASP Web Top 10 + GenAI Top 10 audit + remediation plan |
| `/docs-pack` | Generate user-facing docs (README, API ref, runbook) |
| `/ai-assets-init` | Bootstrap a target repo to be ai-assets-aware |

## Companion skills (9)

`/ralph` (power-user RALF entry) · `/eval` (skill/agent evaluator) · `/plugin-doctor` (self-diagnostic) · `/memory-init` · `/memory-recall` · `/learnings-write` · `/context-load` · `/subagent-spawn` · `/plugin-skill-create`

## What's inside today (v0.2.0)

- **52 skills** — 20 KEEP + 13 REFACTOR + 17 NEW + 2 MERGE; covers the full SDLC plus marketing + content
- **26 specialized agents** — cloud architect, security engineer, all major language engineers, content/marketing roles, 4 orchestrators
- **18 hooks** across 13 lifecycle events — security guardrails, untrusted-content wrapping, session memory flush, RALF loop control + per-iteration token meter (v0.1.6), subagent depth guard (v0.1.7), `.committed/` allowlist enforcement
- **12 rules** — security, memory discipline, RALF budget, untrusted-content wrapping, etc.
- **17 eval rubrics + 102 calibration samples + Tier 1 linter + Tier 2 judge-calibration smoke** — for systematic regression detection (Tier 2 added in v0.1.4, requires `ANTHROPIC_API_KEY`)
- **G1/G2 attack-surface validation (v0.1.5)** — 6 indirect-prompt-injection fixtures + structural runner that confirms `<untrusted_content>` envelope wrapping correctly contains attacker-planted instructions across 5 attack vectors (poisoned CLAUDE.md, malicious env logs, poisoned learnings, bash role-switch, poisoned PRD); 1 fixture documents the sub-200-token wrap-skip design tradeoff. Optional behavioral mode round-trips wrapped payloads through Haiku to verify no compliance escape.
- **Per-iteration RALF token measurement (v0.1.6)** — `ralph-iter-meter.py` PostToolUse hook estimates tokens per tool call (chars/4) and accumulates while a RALF run is active. `ralph-stop.py` consumes the per-iter accumulator on each Stop intercept, persists `iter-NNN/tokens.json`, and fires a runaway warning when a single iteration exceeds 3× fair share (`token_budget / max_iterations`). Closes the v0.1 gap where session-aggregate token caps only fired inside Tier 3 eval runs.
- **Defensive subagent depth-guard (v0.1.7)** — `subagent-depth-guard.py` SubagentStart hook walks the `parent_trace_id` chain in G7 spawn payloads, computes spawn depth, and blocks at `depth > userConfig.subagent_max_depth` (default 3). Logs every `start`/`stop`/`rejected` event to `.ai-assets-memory/sessions/<sid>/spawn-chain.jsonl`. Anthropic's runtime enforces depth=1 max; this is the defensive backstop in case orchestration accidentally bypasses or future versions add Task to additional agents.
- **2 output styles** — `concise-pr` for PR descriptions, `design-pack` for `/feature-design` artefacts
- **13-knob declarative config** + 0 external dependencies (fully standalone in v0.1)

## Learn more

- [docs/getting-started.md](docs/getting-started.md) — 30-min tutorial (install + first feature design)
- [docs/workflows/](docs/workflows/) — one user doc per slash command (10 files)
- [docs/concepts/memory.md](docs/concepts/memory.md) — 6-layer memory model summary
- [docs/concepts/eval.md](docs/concepts/eval.md) — eval framework summary
- [docs/concepts/ralf.md](docs/concepts/ralf.md) — RALF iteration loop summary
- [docs/concepts/skill-frontmatter-extensions.md](docs/concepts/skill-frontmatter-extensions.md) — the 4 Claude Code-specific frontmatter fields and how they relate to the agentskills.io spec
- [CHANGELOG.md](CHANGELOG.md) — version history per batch
- `../plugin-design/00-PHASE-1-PLAN.md` — full plan with locked decisions D1-D13
- `../plugin-design/04-MIGRATION-CHECKLIST.md` — atomic-batch implementation checklist

## License

MIT
