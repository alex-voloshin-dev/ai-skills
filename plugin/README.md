# ai-assets — Claude Code Plugin

A reusable team-of-agents plugin for the full software development lifecycle. Drives feature design, implementation, bugfixing, environment analysis, and refactoring through coordinated subagents, with built-in iteration loops (RALF), layered memory, and systematic eval.

**Project-agnostic by design.** Operations live in this plugin; project-specific context (brand, conventions, terminology) lives in the target repo's `CLAUDE.md` / `AGENTS.md` / `marketing/MARKETING.md` and is read at runtime.

## Status — v0.1.4 (released 2026-04-29)

First stable release after 17 alpha iterations (alpha.13 → alpha.29) + 2 hotfix patches (0.1.1, 0.1.4) and 4 full review rounds (Round 13/14/15/16). All Phase 2 batches per `../plugin-design/04-MIGRATION-CHECKLIST.md` are complete: B1-B13 + Rounds 11/12 cross-phase review passes. Both v0.1.4 release gates closed: local validator passes (21 checks, 0 fail, 0 warn), live smoke tests confirmed `/develop` orchestrates DEV→REVIEW→QA pipeline with plugin-namespaced subagents on **3 stacks** — Java + Spring Boot, Python + FastAPI, Next.js + TypeScript — in both Path A (Subagents) and Path B (Agent Teams) modes on Windows host with `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`.

| Component | Implemented | v0.1 target | Pending |
|---|---|---|---|
| Hooks | **16** (4 carried + 12 new) across 13 lifecycle events | 16 | — |
| Agents | **26** (22 normalized + 4 new) | 26 | — |
| Rules | **12** (8 carried + 4 new) | 12 | — |
| Skills | **52** (20 KEEP + 13 REFACTOR + 17 NEW + 2 MERGE) | 52 | — (target met) |
| JSON schemas | **2** (G7 spawn + return) | 2 | — |
| Memory templates | **7** + `pii-patterns.txt` | 7 | — |
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

## What's inside today (v0.1.4)

- **52 skills** — 20 KEEP + 13 REFACTOR + 17 NEW + 2 MERGE; covers the full SDLC plus marketing + content
- **26 specialized agents** — cloud architect, security engineer, all major language engineers, content/marketing roles, 4 orchestrators
- **16 hooks** across 13 lifecycle events — security guardrails, untrusted-content wrapping, session memory flush, RALF loop control, `.committed/` allowlist enforcement
- **12 rules** — security, memory discipline, RALF budget, untrusted-content wrapping, etc.
- **17 eval rubrics + 102 calibration samples + Tier 1 linter + Tier 2 judge-calibration smoke** — for systematic regression detection (Tier 2 added in v0.1.4, requires `ANTHROPIC_API_KEY`)
- **2 output styles** — `concise-pr` for PR descriptions, `design-pack` for `/feature-design` artefacts
- **12-knob declarative config** + 0 external dependencies (fully standalone in v0.1)

## Learn more

- [docs/getting-started.md](docs/getting-started.md) — 30-min tutorial (install + first feature design)
- [docs/workflows/](docs/workflows/) — one user doc per slash command (10 files)
- [docs/concepts/memory.md](docs/concepts/memory.md) — 6-layer memory model summary
- [docs/concepts/eval.md](docs/concepts/eval.md) — eval framework summary
- [docs/concepts/ralf.md](docs/concepts/ralf.md) — RALF iteration loop summary
- [CHANGELOG.md](CHANGELOG.md) — version history per batch
- `../plugin-design/00-PHASE-1-PLAN.md` — full plan with locked decisions D1-D13
- `../plugin-design/04-MIGRATION-CHECKLIST.md` — atomic-batch implementation checklist

## License

MIT
