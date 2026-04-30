# Plugin Design Glossary — Single Source of Truth

> **Purpose (T1 from Round 5):** every entity in the plugin design has its canonical name, disposition, and authoritative source document recorded here. All other docs REFERENCE this glossary instead of restating. When a value here changes, every reference must be updated (see `_phase-gate-criteria.md` for verification process).
>
> **Maintenance rule:** every PR that adds, renames, removes, or rescopes an entity MUST update this glossary in the same commit. `plugin-design-doctor.py` enforces consistency between this glossary and other docs.
>
> **Last updated:** 2026-04-26 (after Round 5)

---

## 1. Counts (authoritative)

| Asset class | Count | Authoritative breakdown |
|---|---|---|
| Skills | **52** | 20 KEEP + 13 REFACTOR + 2 MERGE-output + 17 NEW |
| Agents | **26** | 22 normalized + 4 new (security-engineer, feature-design-lead, eval-judge, memory-curator) |
| Rules | **12** | 8 carried + 4 new |
| Hooks | **16** | 4 carried + 12 new across 13 lifecycle events (12th new is `pre-tool-use-committed-write.py` added Round 8 CRIT-1) |
| Eval rubrics | **17** | 10 per-workflow + 7 cross-cutting |
| JSON schemas | **2** | spawn-payload, return-contract |
| Output styles | **2** | concise-pr, design-pack |
| Monitors | **1** | env-watch |
| User-facing docs | **14** | 1 getting-started + 10 workflow + 3 concept |
| Memory templates (L1) | **7** | (excluding pii-patterns.txt which lives in hooks/scripts/) |
| Calibration samples | **34 v0.1 ship; 102 in Phase 3** | 2 per rubric (v0.1, deterministic) → 6 per rubric (Phase 3 expansion) |
| `userConfig` knobs | **11** | session_token soft/hard (2), ralph per-workflow defaults × 3, ralph session-aggregate × 3 (added Round 6 HIGH-3), opt-in toggles × 3 |
| Plugin dependencies | **0** | fully standalone in v0.1 |

---

## 2. Skills (52 total)

### KEEP (20) — copy unchanged with frontmatter audit

| # | Skill | Type | Slash command | User-invocable | Source |
|---|---|---|---|---|---|
| 1 | analyze | knowledge | /analyze | yes | `.claude/skills/analyze/` |
| 2 | analyze-local | workflow auxiliary | /analyze-local | yes | `.claude/skills/analyze-local/` |
| 3 | analyze-prod | workflow auxiliary | /analyze-prod | yes | `.claude/skills/analyze-prod/` |
| 4 | architecture | knowledge | — | no | `.claude/skills/architecture/` |
| 5 | cloud-platforms | knowledge | — | no | `.claude/skills/cloud-platforms/` |
| 6 | code-review | workflow auxiliary | — | no | `.claude/skills/code-review/` |
| 7 | context-engineering | knowledge | — | no | `.claude/skills/context-engineering/` |
| 8 | deployment-procedures | knowledge | — | no | `.claude/skills/deployment-procedures/` |
| 9 | docs | knowledge | — | no | `.claude/skills/docs/` (general docs help; distinct from /docs-pack workflow) |
| 10 | geo-writer | knowledge | — | no | `.claude/skills/geo-writer/` |
| 11 | humanizer | knowledge | — | no | `.claude/skills/humanizer/` |
| 12 | pre-commit | utility | — | no (`disable-model-invocation: true`) | `.claude/skills/pre-commit/` |
| 13 | prompt-engineering | knowledge | — | no | `.claude/skills/prompt-engineering/` |
| 14 | qa | workflow auxiliary | — | no | `.claude/skills/qa/` |
| 15 | security-scan | workflow auxiliary | — | no | `.claude/skills/security-scan/` (used by /security-audit) |
| 16 | seo-review | knowledge | — | no | `.claude/skills/seo-review/` |
| 17 | social-media-manager | knowledge (extended scope) | — | no | `.claude/skills/social-media-manager/` |
| 18 | test-strategy | knowledge | — | no | `.claude/skills/test-strategy/` |
| 19 | ui-ux-design | knowledge | — | no | `.claude/skills/ui-ux-design/` |
| 20 | worktree-isolation | utility | — | no | `.claude/skills/worktree-isolation/` |

### REFACTOR (13) — rewrite for plugin patterns; one is RENAMED

| # | Source name | Plugin name | Slash command | User-invocable |
|---|---|---|---|---|
| 21 | feature-dev | feature-dev | — | no (auxiliary; /develop is the workflow) |
| 22 | bugfix | bugfix | /bugfix | yes |
| 23 | team-dev | **develop** (RENAME) | /develop | yes |
| 24 | team-bugfix | team-bugfix | — | no (auxiliary of /bugfix) |
| 25 | team-protocols | team-protocols | — | no (knowledge) |
| 26 | plan | plan | /plan | yes |
| 27 | release | release | /release | yes |
| 28 | create-pr | create-pr | /create-pr | yes |
| 29 | infra-change | infra-change | /infra-change | yes |
| 30 | deploy-staging | deploy-staging | /deploy-staging | yes |
| 31 | deploy-production | deploy-production | /deploy-production | yes |
| 32 | run-tests | run-tests | /run-tests | yes |
| 33 | test-local | test-local | /test-local | yes |

### MERGE input → output (4 → 2)

| Inputs (from `.claude/skills/`) | Output (in `plugin/skills/`) | Slash command | User-invocable |
|---|---|---|---|
| marketing + marketing-operations | marketing | /marketing | yes |
| blog-post + content-creation | content-creation | /content-creation | yes |

### ARCHIVE (5) — do NOT migrate; remain in legacy `.claude/`

| Skill | Replacement in plugin | Phase 5 sunset migration |
|---|---|---|
| ai-assets | /plugin-doctor | `archive/MIGRATION.md` entry |
| asset-validation | /plugin-doctor | same |
| ml-pipeline | (none in v0.1; revisit v0.3+) | document as "no replacement; revisit if generalisable" |
| product | product-manager agent (use directly) | document |
| project-init | /ai-assets-init | document |

### NEW (17) — author for plugin

#### Workflow skills (8 NEW)

| # | Skill | Slash command | Source spec |
|---|---|---|---|
| 38 | feature-design | /feature-design | `01-WORKFLOW-SPECS.md` Part A |
| 39 | env-analyze | /env-analyze | (renamed from earlier draft `env-analyzer`) |
| 40 | refactor | /refactor | Part A |
| 41 | migrate | /migrate | Part A |
| 42 | spike | /spike | Part A |
| 43 | security-audit | /security-audit | Part A |
| 44 | docs-pack | /docs-pack | Part A |
| 45 | ai-assets-init | /ai-assets-init | Part A |

#### Companion skills (9 NEW)

| # | Skill | Slash command | Source spec |
|---|---|---|---|
| 46 | ralph | /ralph | `01-WORKFLOW-SPECS.md` Part B |
| 47 | eval | /eval | Part B |
| 48 | plugin-doctor | /plugin-doctor | Part B |
| 49 | memory-init | /memory-init | Part B |
| 50 | memory-recall | /memory-recall | Part B |
| 51 | learnings-write | /learnings-write | Part B |
| 52 | context-load | /context-load | Part B |
| 53 | subagent-spawn | /subagent-spawn | Part B |
| 54 | plugin-skill-create | /plugin-skill-create | Part B |

**Math check (verified Round 5):** 20 KEEP + 13 REFACTOR + 2 MERGE-output + 17 NEW = **52** ✓
**User-invocable count:** 8 KEEP-invocable + 11 REFACTOR-invocable + 2 MERGE-invocable + 17 NEW-invocable = ?
Recount user-invocable: KEEP gives 3 (/analyze, /analyze-local, /analyze-prod), REFACTOR gives 11 (all REFACTOR except feature-dev, team-bugfix, team-protocols), MERGE gives 2, NEW gives 17. Total = 3 + 11 + 2 + 17 = **33** user-invocable.

> **Note:** the earlier "19 user-invocable" claim in plan §2.1 was undercounting. The actual user-invocable count is 33 (covers /analyze*, all refactored workflow skills, both merged content skills, and all 17 NEW). The "19" referred specifically to the 10 NEW workflows + 9 NEW companions = 19. Other 14 user-invocable skills come from KEEP/REFACTOR/MERGE.

---

## 3. Agents (26 total)

### Existing normalized (22) — drop `permissionMode` from 9 + add `effort`/`maxTurns`/`max_output_tokens`

| # | Agent | Model | Effort | max_output_tokens | Drops `permissionMode`? |
|---|---|---|---|---|---|
| 1 | cloud-architect | inherit | high | 1500 | YES |
| 2 | content-designer | inherit | medium | 1200 | YES |
| 3 | content-writer | inherit | medium | 1200 | YES |
| 4 | data-engineer | inherit | high | 2000 | no |
| 5 | db-engineer | inherit | high | 2000 | no |
| 6 | devops-architect | inherit | high | 1500 | YES |
| 7 | devops-engineer | inherit | high | 2000 | no |
| 8 | frontend-engineer | inherit | high | 2000 | no |
| 9 | java-engineer | inherit | high | 2000 | no |
| 10 | marketing-strategist | inherit | medium | 1500 | YES |
| 11 | ml-engineer | inherit | high | 2000 | no |
| 12 | mobile-engineer | inherit | high | 2000 | no |
| 13 | product-manager | inherit | medium | 1500 | YES |
| 14 | prompt-engineer | inherit | medium | 1000 | no |
| 15 | python-engineer | inherit | high | 2000 | no |
| 16 | qa-engineer | inherit | medium | 800 | no |
| 17 | seo-engineer | inherit | low | 800 | no |
| 18 | software-engineer | inherit | medium | 1000 | no |
| 19 | solution-architect | inherit | high | 1500 | YES |
| 20 | sre-engineer | inherit | high | 2000 | no |
| 21 | system-architect | inherit | high | 1500 | YES |
| 22 | ui-ux-designer | inherit | medium | 1200 | YES |

**Permissions cleanup:** 9 of 22 drop `permissionMode: plan` per Anthropic plugin agent restrictions; intent preserved by existing `disallowedTools: Write, Edit`.

### New (4)

| # | Agent | Model | Effort | maxTurns | max_output_tokens | Tools | Purpose |
|---|---|---|---|---|---|---|---|
| 23 | security-engineer | sonnet | high | 30 | 1500 | Read, Grep, Glob, Bash | OWASP GenAI/LLM + Web Top 10; powers /security-audit |
| 24 | feature-design-lead | opus | xhigh | 50 | 1200 | Task | Orchestrates 6-10 subagents in waves for /feature-design (only agent with Task tool). `effort: xhigh` per Round 5 Appendix A7 — Anthropic now defaults Opus to xhigh; explicit setting ensures full reasoning depth |
| 25 | eval-judge | haiku (Sonnet override per-rubric) | medium | 5 | 600 | Read, Grep, Glob | Rubric scoring for /eval and RALF subjective oracles |
| 26 | memory-curator | haiku | low | 10 | 800 | Read, Write (memory dirs only) | Curates L4 / optional L5 writes; PreCompact flush |

---

## 4. Rules (12 total)

| # | Rule file | Source | Purpose |
|---|---|---|---|
| 1 | failure-recovery.md | KEEP from `.claude/rules/` | Loop detection, goal drift recovery |
| 2 | geo-content.md | KEEP | GEO/AEO writing standards for public content |
| 3 | git-conventions.md | KEEP | Commit/branch/PR conventions |
| 4 | global-package-rules.md | KEEP | Package-level rules |
| 5 | global-rules.md | KEEP | Authoring standards (English, char limits) |
| 6 | humanize-content.md | KEEP | Anti-AI-vocabulary rule |
| 7 | memory-validation.md | KEEP | Memory entry validation, conflict resolution |
| 8 | task-completion.md | KEEP | Pre-completion audit (mandatory checklist before declaring done) |
| 9 | subagent-isolation.md | NEW | When to delegate vs inline; bounded recursion guarantee (Round 4 O1) |
| 10 | memory-discipline.md | NEW | Layer write rules; PII filter mandatory |
| 11 | ralph-budget.md | NEW | RALF caps + mandatory `--kill-on` |
| 12 | untrusted-content-wrapping.md | NEW (G1) | `<untrusted_content>` wrapper for L0/L2/L4 reads + subagent returns + tool outputs >200 tokens |

---

## 5. Hooks (16 total, across 13 lifecycle events)

### Existing carried (4)

| # | Script | Event | Purpose |
|---|---|---|---|
| 1 | block-dangerous-commands.py | PreToolUse(Bash) | Blocks `rm -rf /` etc. |
| 2 | block-secrets-in-code.py | PreToolUse(Write\|Edit) | Detects secrets in code edits |
| 3 | block-sensitive-files.py | PreToolUse(Read) | Blocks reads of credential files |
| 4 | log-actions.py | PostToolUse(*) | Audit log |

### New (11) + 1 shared module

| # | Script | Event | Purpose |
|---|---|---|---|
| 0 | _lib.py (shared module, Round 5 S2) | — | normalize_hook_input, apply_pii_filter, wrap_untrusted, read/emit wrap_marker, token meter helpers, log_to |
| 5 | session-start-context.py | SessionStart | Load CLAUDE.md/AGENTS.md/ARCHITECTURE.md (≤8KB), PII filter, G1 wrap, init token meter |
| 6 | instructions-loaded-augment.py | InstructionsLoaded | Supplement loaded files with `.committed/conventions.md` excerpt |
| 7 | ralph-stop.py | Stop | RALF oracle check, kill-on signal check, budget enforcement, prompt re-injection |
| 8 | pre-compact-memory-flush.py | PreCompact | CRITICAL: invokes memory-curator before context loss (isolated subagent context) |
| 9 | session-end-finalize.py | SessionEnd | Archive sessions/, update baselines, release dangling RALF locks |
| 10 | subagent-start-budget.py | SubagentStart | Validate G7 spawn payload, check token meter |
| 11 | subagent-stop-learnings.py | SubagentStop | Validate G7 return contract; opt-in capture for memory-curator |
| 12 | task-event-log.py | TaskCreated, TaskCompleted | TodoList events to runs.jsonl |
| 13 | tool-failure-log.py | PostToolUseFailure, StopFailure | Errors to errors.log |
| 14 | tool-output-wrap.py (G1) | PostToolUse(Read\|Bash for memory/project paths) | Wraps outputs >200 tokens in `<untrusted_content>` |
| 15 | tool-output-normalize.py (G2) | PostToolUse(same as wrap, AFTER) | Outputs >2000 tokens: extract → Haiku-summarize → annotate; asserts wrap marker (Round 5 S6) |
| 16 | pre-tool-use-committed-write.py (Round 8 CRIT-1) | PreToolUse(Write\|Edit) | Validates writes to `.ai-assets-memory/.committed/*` against allowlist from `committed-allowlist.txt`; exit 2 if not matched |

---

## 6. Eval rubrics (17 total)

### Per-workflow (10)

feature-design, develop, bugfix, refactor, migrate, spike, security-audit, docs-pack, env-analyze, ai-assets-init

### Cross-cutting (7)

| # | Rubric | Applies to |
|---|---|---|
| 11 | humanizer-compliance.md | feature-design, develop, bugfix, docs-pack, spike |
| 12 | code-quality.md | develop, bugfix, refactor, migrate |
| 13 | security-soundness.md | develop, bugfix, refactor, migrate, security-audit |
| 14 | geo-readiness.md | feature-design, docs-pack, content-creation |
| 15 | subagent-handoff-quality.md | feature-design, develop, security-audit, migrate |
| 16 | memory-write-discipline.md | all workflows that write memory |
| 17 | faithfulness.md (G5) | every workflow reading project files / tool outputs / RALF iterations |

---

## 7. Other plugin assets

### JSON schemas (2)
- `plugin/schemas/spawn-payload.schema.json` (G7 — orchestrator → subagent)
- `plugin/schemas/return-contract.schema.json` (G7 — subagent → orchestrator)

### Output styles (2)
- `plugin/output-styles/concise-pr.md` (for /develop PR descriptions)
- `plugin/output-styles/design-pack.md` (for /feature-design artefacts)

### Monitors (1)
- `plugin/monitors/monitors.json` → `env-watch.sh` (opt-in via `userConfig.env_watch_enabled`)

### Memory templates L1 (7 in `plugin/memory/templates/` + 1 in `plugin/hooks/scripts/`)
- ai-assets-memory.gitignore
- committed-readme.md
- learnings-schema.md
- conventions-schema.md
- eval-baseline.schema.json
- committed-allowlist.txt
- untrusted-content-wrapper.md
- (separate: `plugin/hooks/scripts/pii-patterns.txt`)

### `userConfig` knobs (11) in `plugin/.claude-plugin/plugin.json`

**Session-level token budget (2):**
1. `session_token_soft_cap` (default 1_000_000) — warn user when session reaches this aggregate
2. `session_token_hard_cap` (default 1_500_000) — hard pause; user must confirm to continue

**RALF per-workflow defaults (3, per D12):**
3. `ralph_default_max_iter` (default 10)
4. `ralph_default_token_budget` (default 200_000)
5. `ralph_default_time_cap_minutes` (default 120)

**RALF session-aggregate caps (3, added Round 6 HIGH-3):**
6. `ralph_session_max_iter` (default 20) — total RALF iterations across all workflows in one session
7. `ralph_session_token_budget` (default 400_000) — total RALF token spend across all workflows in one session
8. `ralph_session_time_cap_minutes` (default 180) — total RALF wall-time across all workflows in one session

**Opt-in toggles (3):**
9. `subagent_learnings_enabled` (default false)
10. `user_global_memory_enabled` (default false)
11. `env_watch_enabled` (default false)

> **Cascade history (Pattern 11):** count was 7 → 8 (Round 5 glossary build) → 11 (Round 6 HIGH-3). Each fix triggered Pattern 1 sweep across glossary §1, glossary §7, plan §3.2 plugin.json example, plan §3.5 RALF integration text, plan §7b counts table.

---

## 8. Locked decisions D1-D13

| ID | Decision (one-liner) |
|---|---|
| D1 | Single monolithic plugin |
| D2 | Public distribution, fully generic; operations/data split |
| D3 | Operations live in plugin · Data lives in target repo (CLAUDE.md / AGENTS.md read at runtime) |
| D4 | Existing assets are seed; plugin built in parallel (`plugin/` dir) |
| D5 | Eval = full Anthropic-style + lightweight linters + RALF loop |
| D6 | Long workflows = slash commands → workflow-specific orchestrators or inline coordination; no single universal orchestrator |
| D7 | Chat in Russian, persisted artefacts in English |
| D8 | Plugin lives at `ai-assets/plugin/` in same repo |
| D9 | `.ai-assets-memory/` gitignored; opt-in `.committed/` for versioned content |
| D10 | No MCP in v0.1; planned for v0.3+ |
| D11 | Eval budgets in tokens (Max-subscription model); Haiku for judge/comparator |
| D12 | RALF defaults: 10 iter / 200K tokens / 2h; mandatory `--kill-on`; per-workflow overrides |
| D13 | brand-voice:* skills NOT migrated; remain as separate plugin |

---

## 9. File path conventions

| Convention | Path | Used for |
|---|---|---|
| Plugin install root | `${CLAUDE_PLUGIN_ROOT}/` | All plugin internal references |
| Plugin source (in repo) | `<workspace>/plugin/` | Authoring location |
| Project memory (L4) | `<target-repo>/.ai-assets-memory/` | Per-project persistent memory |
| User-global memory (L5) | `~/.claude/ai-assets/learnings.md` | Cross-project learnings (opt-in) |
| Cowork host memory (L0) | `~/.../spaces/<id>/memory/` | Out-of-plugin; non-interference contract |
| Design pack output | `<target-repo>/docs/features/<feature-id>/` | /feature-design only (versioned in git) |
| Workflow run logs | `.ai-assets-memory/<workflow>/<run-id>/` | All other workflows (gitignored) |
| Versioned `.committed/` | `.ai-assets-memory/.committed/` | Opt-in git-tracked sub-dir |

---

## 10. Round/Section ID namespaces (to prevent future collisions per Round 4 N3 / Round 5 P8)

| Prefix | Used by | Reserved? |
|---|---|---|
| D | Plan §0 Locked Decisions D1-D13 | YES — do not reuse |
| Q | Plan §7 Resolved Questions Q1-Q6 | YES |
| P | Critique Round 1 patches P1-P25 | YES |
| F | Critique Round 2 friendly4ai F1-F4 | YES |
| H | Critique Round 2 best-practices H1-H9 | YES |
| M | Critique Round 2 missing concepts M1-M10 (renamed from D in Round 3 to avoid collision) | YES |
| G | Critique Round 3 context-engineering Gaps G1-G10 | YES |
| N | Critique Round 4 practical N1-N6 | YES |
| O | Critique Round 4 architectural O1-O4 | YES |
| (Round 4 P1-P2 best-practices) | RESERVED but small | YES — use sparingly |
| S | Critique Round 5 substantive S1-S11 | YES |
| T | Critique Round 5 process improvements T1-T8 | YES |
| U | Critique Round 5 patches U1-U9 | YES |
| **Free for future rounds** | V, W, X, Y, Z, A, B, C, E, I, J, K, L, R | No collision risk |
