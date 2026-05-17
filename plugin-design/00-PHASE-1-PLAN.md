# AI-Assets Plugin — Phase 1: Plan & Design

> **Status:** Draft for review · **Date:** 2026-04-26
> **Goal of Phase 1:** Lock down architecture, scope, and migration path for the new Claude Code plugin before writing any plugin code.
> **Independence statement:** This plugin is fully generic and project-agnostic. Operations live in the plugin; project-specific data (brand, ICP, terminology, conventions) lives in the target repository's `CLAUDE.md` / `AGENTS.md` / `marketing/MARKETING.md` and is read at runtime. The plugin contains no hard dependency on any specific consumer project.

---

## 0. Decisions Already Locked

| # | Decision | Source |
|---|---|---|
| D1 | Single monolithic plugin (one `.claude-plugin/plugin.json`) | User answer |
| D2 | Public distribution, fully generic — no project-specific terminology, ICP, products, or defaults. Plugin = operations, target repo = data. Independent from any specific consumer project | User answer |
| D3 | Operations live in plugin · Data lives in target repo (`CLAUDE.md` / `AGENTS.md` are read at runtime to derive project context) | User answer |
| D4 | Existing assets are the seed; plugin is built in parallel (`plugin/` dir) without breaking the current `.claude/` setup | User answer |
| D5 | Eval = full Anthropic-style + lightweight linters + RALF loop (all three layers) | User answer |
| D6 | Long workflows = slash commands → workflow-specific orchestrators or inline subagent coordination. **No single universal orchestrator gating all workflows**; per-workflow specialist orchestrators (e.g., `feature-design-lead`) are allowed and used | User answer (clarified after self-review) |
| D7 | Chat in Russian, all persisted artefacts in English | User preference |
| D8 | Plugin lives at `ai-skills/plugin/` in same repo (no sibling repo in v0.1) | Q1 resolved 2026-04-26 |
| D9 | `.ai-skills-memory/` gitignored; opt-in `.committed/` sub-dir for versioned content | Q2 resolved 2026-04-26 |
| D10 | No MCP in v0.1.0 (memory-server, eval-server, git-context-server queued for v0.3.0+) | Q3 resolved 2026-04-26 |
| D11 | Eval budgets measured in tokens (Max-subscription model), Haiku for judge/comparator | Q4 resolved 2026-04-26 |
| D12 | RALF caps: 10 iter / 200K tokens / 2 h, overridable per workflow, mandatory kill-criterion | Q5 resolved 2026-04-26 |
| D13 | `brand-voice:*` skills NOT migrated; remain as separate standalone plugin | Q6 resolved 2026-04-26 |

---

## 1. Research Summary (April 2026, sourced from Anthropic docs + community)

### 1.1 Plugin anatomy (latest)
- A plugin is a self-contained directory. Manifest at `.claude-plugin/plugin.json` is **optional** — Claude Code auto-discovers components from canonical paths.
- Component locations (must sit at plugin root, NOT inside `.claude-plugin/`):
  `skills/<name>/SKILL.md` · `commands/<name>.md` · `agents/<name>.md` · `hooks/hooks.json` · `.mcp.json` · `monitors/monitors.json` · `output-styles/` · `themes/`
- Distribution via marketplace (`.claude-plugin/marketplace.json`) — possible later as a second deliverable. Phase 1 scope: single-plugin git repo installable via `/plugin install <git-url>`.
- `${CLAUDE_PLUGIN_ROOT}` is the canonical env variable for hook scripts and MCP server paths — all paths must be relative and start with `./`.
- Plugin agents support a restricted frontmatter set: `name, description, model, effort, maxTurns, tools, disallowedTools, skills, memory, background, isolation`. **Plugin-shipped agents cannot define `hooks`, `mcpServers`, or `permissionMode`** — security boundary.
- **Verified impact on existing assets:** 9 of our current 22 agents (cloud-architect, content-designer, content-writer, devops-architect, marketing-strategist, product-manager, solution-architect, system-architect, ui-ux-designer) carry `permissionMode: plan`. They MUST be refactored before plugin migration: drop the field and rely on `disallowedTools: Write, Edit` (already present on most of them) to keep them read-only.

### 1.2 Subagents & teams (2026 model)
- Subagent = isolated Claude instance with its own context window, system prompt, tool list, permission mode. Returns only the final output to parent.
- Two delegation primitives now ship: `Agent` (always available) and the optional team layer (`TeamCreate`, `SendMessage`, `TaskOutput`, `TaskStop`, `TeamDelete`) which adds a shared task list, peer-to-peer messaging, and file locking.
- Cost reality: agent teams use 4–10× the tokens of a single session. Use them only when teammates can operate in parallel and benefit from independent context (independent investigation, multi-stack code).
- For sequential/single-file work — single agent or sequential subagents are cheaper and more reliable.

### 1.3 Skill best practices (Skills 2.0)

**Frontmatter:**
- `name` (≤64 chars, lowercase + hyphens)
- `description` (≤1024 chars) — drives discovery; written **in third person**; must include both **WHAT** the skill does AND **WHEN** to use it
- Optional: `user-invocable: true` (or `context: fork` per existing convention), `argument-hint`, `allowed-tools`, `disable-model-invocation`

**Description authoring contract (verified pattern from official Anthropic docs):**

Every skill description follows this shape:
```
<one sentence WHAT, third person, imperative>. Use when <trigger 1>, <trigger 2>, or when user mentions "<keyword 1>", "<keyword 2>", "<keyword 3>". <Optional: when NOT to use>.
```

The "Use when" / "or when user mentions" pattern is the model's primary trigger signal. Skills without explicit triggers fire either too broadly or not at all. All NEW and REFACTOR skills must conform.

**Progressive disclosure** is the contract:
- **Level 1 (~100 tokens per skill):** name + description loaded for every installed skill on session start
- **Level 2 (≤5K tokens ideal):** full SKILL.md body loaded only when activated
- **Level 3:** companion files (`reference.md`, `scripts/*.py`, sub-md per topic) loaded on demand from skill body

**Body authoring:**
- Imperative language ("Always run tests", not "You might consider running tests")
- Keep skills short and scannable; if approaching ~50 lines or 5K tokens, split into focused skills or move depth to companion resources
- One responsibility per skill; do not bundle unrelated concerns

**Description optimization is a first-class lever.** Small wording changes shift activation precision/recall noticeably. This is exactly what Anthropic's `skill-creator` `Eval` mode targets — and our `/eval` skill mirrors that approach with `description-optimizer` as a sub-agent step.

**Cache-friendly skill authoring (G6):** Anthropic prompt caching reuses KV-state for stable prefixes. To maximize cache hits, every SKILL.md MUST be authored with stable content at the TOP and dynamic content at the BOTTOM:

- TOP (cacheable prefix): persona, hard rules, tool contracts, output schema, agent-selection table — content that is identical every time the skill activates
- MIDDLE (semi-stable): cross-references to other skills, default patterns, examples
- BOTTOM (dynamic): user-input slot, retrieved file content, last-iteration diff (for RALF), session state

NEVER interleave static and dynamic blocks — each interleave kills cache hit potential downstream. If a skill must include user input mid-body, refactor: move static content above, dynamic below.

**Verification task for Phase 1 hardening:** test whether Claude Code automatically applies Anthropic prompt caching for plugin contexts. Method: instrument 5 invocations of the same skill with identical fixed input + varying user prompt; compare reported `cached_tokens` between calls. If caching is automatic, document expected hit rate ≥ 80% on the prefix; if not, file an upstream feature request and document the manual workaround. Track `cache_prefix_ratio` per call (G8).

### 1.4 Memory & context engineering
- Anthropic Memory Tool (GA October 2025): client-side `/memory` directory with `read/create/update/delete` ops. Internal evals report +39% on agentic search and −84% tokens on 100-turn runs.
- Best paired with **context editing** (clear old tool outputs) and **compaction** (summarize at boundaries).
- Memory layers we will use (5 plugin-managed + 1 host layer we coexist with):
  - **L0. Cowork host auto-memory** (out-of-plugin, read-only acknowledgment) — Cowork ships its own auto-memory at `~/.../spaces/<id>/memory/`. Plugin NEVER writes here; if exposed to the agent context, plugin reads but treats as advisory only.
  - **L1. Plugin-state** (read-only at runtime): plugin-shipped knowledge base (skills, agents, rules, eval rubrics, memory templates)
  - **L2. Project-state** (read at session start): `CLAUDE.md`, `AGENTS.md`, `ARCHITECTURE.md` in target repo
  - **L3. Session-state** (in-conversation only): TodoList, plan files, conversation, in-flight subagent reports
  - **L4. Project-cross-session** (persistent): plugin-managed `.ai-skills-memory/` directory in the target repo (gitignored by default; opt-in `.committed/` sub-dir)
  - **L5. User-global** (across all projects, opt-in): `~/.claude/ai-skills/learnings.md` (RALF accumulator + cross-project patterns the user explicitly opted to remember)

### 1.5 RALF (Ralph) loop
- Pattern: a `while` loop that re-invokes the agent with the same prompt until a mechanically-verifiable success signal (test passes, file matches schema, screenshot diff < threshold) is reached or the iteration cap is hit.
- Mechanism in Claude Code: a **Stop hook** intercepts the model's exit attempt and re-injects the original task prompt + the diff/error summary from the previous iteration.
- Best fit: greenfield work with a clear pass/fail oracle, eval scoring, doc generation with structural validation.
- Worst fit: open-ended exploration, ambiguous requirements, costly verifications.
- Will be wired as a slash command (`/ralph`), a Stop hook (`hooks/ralph-stop.py`), and a `memory/ralph/` directory holding iteration log + last-error summary.

### 1.6 Eval framework (Skills 2.0)
- Anthropic now ships eval as a first-class skill mode in `skill-creator`: `Create / Eval / Improve / Benchmark`.
- Pipeline pattern: 4 sub-agents in parallel — executor, scorer, blind-comparator (skill vs. no-skill), description-optimizer.
- Evals are JSON test cases: `{prompt, expected_behaviors, anti_patterns, oracle_command}`. Oracle is a CLI that returns 0/non-0 (for objective tests) or a Claude Judge prompt (for subjective tests).
- We will adopt the same shape and ship it as the `/eval` slash command, plus `eval/` directory inside each skill.

### 1.7 Hooks & guardrails

**Full lifecycle event catalogue (verified against latest docs, not all used in v0.1):**

| Event | Phase | Use in v0.1 |
|---|---|---|
| `SessionStart` | session start/resume | YES — `session-start-context.py` |
| `UserPromptSubmit` | before model receives prompt | NO (room for v0.2: route slash commands by intent) |
| `UserPromptExpansion` | when typed command expands | NO |
| `InstructionsLoaded` | on `CLAUDE.md` / rule load | YES — better fit than SessionStart for some context loading |
| `PreToolUse` | before tool call | YES — 3 existing block-* hooks |
| `PostToolUse` | after tool success | YES — `log-actions.py` |
| `PostToolUseFailure` | after tool failure | YES (NEW) — `tool-failure-log.py` writes to error log |
| `PostToolBatch` | after parallel batch | NO |
| `PermissionRequest` / `PermissionDenied` | permission UI | NO (room for guardrail v0.2) |
| `SubagentStart` | subagent spawned | YES (NEW) — `subagent-start-budget.py` checks token meter before spawn |
| `SubagentStop` | subagent finished | YES — `subagent-stop-learnings.py` (opt-in) |
| `TeammateIdle` | team agent idle | NO |
| `TaskCreated` / `TaskCompleted` | TodoList events | YES (NEW) — `task-event-log.py` writes structured run log entries |
| `Stop` | turn ends normally | YES — `ralph-stop.py` |
| `StopFailure` | turn ends due to API error | YES (NEW) — distinguished from Stop in observability log |
| `PreCompact` / `PostCompact` | context compaction | YES (NEW) — `pre-compact-memory-flush.py` writes durable learnings to L4 BEFORE context loss |
| `SessionEnd` | session terminates | YES (NEW) — `session-end-finalize.py` summarizes run, updates baselines |
| `ContextWindowExceeded` | window full | NO (PreCompact handles graceful path) |
| `Elicitation` / `ElicitationResult` | MCP user input | NO (no MCP in v0.1) |

**Hook execution types** (NOT just `command` — major omission in earlier draft):

| Type | What it does | Where we use it |
|---|---|---|
| `command` | execute shell/Python script | All existing 4 hooks; most new hooks |
| `prompt` | evaluate a prompt with an LLM via `$ARGUMENTS` placeholder | NEW — judge-style oracles in RALF, lightweight rubric checks (avoids writing custom Python for LLM-driven verification) |
| `agent` | run an agentic verifier with tools | NEW — complex eval verification (e.g., does this PR description actually match the diff?) |
| `http` | POST event JSON to URL | NO (no observability backend in v0.1) |
| `mcp_tool` | call MCP tool from hook | NO (no MCP in v0.1) |

Exit code 2 = block with stdout reason; exit code 0 = allow. JSON in/out via stdin/stdout. The `prompt` and `agent` hook types simplify several spots where the original draft proposed custom Python — e.g., `eval-judge` rubric scoring becomes a `prompt:judge-rubric.md` hook instead of a Python wrapper around an LLM call.

### 1.8 Plugin features beyond components

**`userConfig` declarative configuration** — declared in `plugin.json`, prompts user for values at install time. Replaces the original draft's `.ai-skills-memory/config.json` hand-editing model for top-level toggles. Sensitive fields (tokens) marked with `"sensitive": true`. We use this for: session token budget overrides, RALF cap overrides, opt-in subagent learnings, opt-in user-global memory writes.

**`outputStyles`** — control how Claude formats responses. We ship two named styles in `output-styles/`:
- `concise-pr` — terse, change-focused output for `/develop` PR descriptions
- `design-pack` — structured Markdown with consistent heading hierarchy for `/feature-design` artefacts

**`monitors`** — background processes that emit notifications. We use this in v0.1 for one case: `env-watch.sh` monitor (declared in `monitors/monitors.json`) that polls `docker compose ps` if a compose file is detected at session start, surfacing container health changes as Claude notifications. Optional, opt-in via `userConfig.env_watch.enabled`. Requires Claude Code v2.1.105+.

**`channels`** — message injection from Telegram/Slack/Discord. NOT in v0.1.

**`dependencies`** — declare other plugins this plugin requires with semver constraints. v0.1 declares **zero plugin dependencies** — fully standalone. Recorded explicitly in `plugin.json` for transparency.

**Plugin namespacing** — components are namespaced by plugin name. Our slash command `/feature-design` becomes `/ai-skills:feature-design` if any other installed plugin defines a colliding name. Documented in user docs; built-in slash commands assume no collision.

### 1.9 Hook implementation guidance

- All scripts MUST use `${CLAUDE_PLUGIN_ROOT}` for paths — never absolute, never relative to cwd
- Hooks marked `command` type MUST be executable (`chmod +x`) — installer-time check in `/plugin-doctor`
- Existing 4 hooks (`block-dangerous-commands`, `block-secrets-in-code`, `block-sensitive-files`, `log-actions`) are battle-tested — **carry over as-is**, just relocate paths
- Per E3, plugin agents cannot define `permissionMode` — guardrails enforced via hooks instead

---

## 2. Existing Assets — Audit & Disposition

Inventory (verified 2026-04-26): **42 skills**, **22 agents**, **8 rules**, **4 hook scripts**, **7 templates**, **26 workflows** (Windsurf-side, mirrored in skills).

### 2.1 Skills disposition (explicit, sums to 42 existing + 17 new = 52 in-plugin total)

> **Slash-command-to-skill-name mapping policy:** every slash command exposed to users matches a skill directory name in `plugin/skills/`. When refactoring an existing skill changes its purpose to a workflow with a different command name, RENAME the directory in REFACTOR (e.g., `team-dev` → `develop`).

**KEEP as-is — 20 skills** (carry into plugin unchanged):
`humanizer`, `geo-writer`, `code-review`, `docs`, `pre-commit`, `architecture`, `prompt-engineering`, `context-engineering`, `qa`, `seo-review`, `security-scan`, `analyze-local`, `analyze-prod`, `analyze`, `cloud-platforms`, `deployment-procedures`, `social-media-manager`, `worktree-isolation`, `test-strategy`, `ui-ux-design`

**REFACTOR — 13 skills** (rewrite for plugin: subagent-aware, memory-aware, eval-ready). One is RENAMED to match its slash command:
`feature-dev`, `bugfix`, `team-dev` **→ renamed to `develop`** (matches `/develop` slash command per workflow specs), `team-bugfix`, `team-protocols`, `plan`, `release`, `create-pr`, `infra-change`, `deploy-staging`, `deploy-production`, `run-tests`, `test-local`

**MERGE — 4 skills → 2 skills** (net: 4 inputs collapse to 2 outputs):
- `marketing` + `marketing-operations` → single `marketing` (drop `marketing-operations` after merge)
- `blog-post` + `content-creation` → single `content-creation` (drop `blog-post` after merge — its template moves into the new content-creation)

**ARCHIVE — 5 skills** (do not migrate; functionality replaced or repo-specific):
- `ai-skills` → replaced by new `plugin-doctor`
- `asset-validation` → replaced by new `plugin-doctor`
- `ml-pipeline` → archive in v0.1 (highly project-specific; revisit in v0.3 if generalisable)
- `product` → archive (overlaps with product-manager agent capabilities; agent does the work directly)
- `project-init` → replaced by new `ai-skills-init` (which bootstraps a target repo with broader scope)

**NEW — 17 skills** (build for plugin):

**Workflow skills (8 NEW, exposed as slash commands per `01-WORKFLOW-SPECS.md` Part A):**
- `feature-design` (design pack from idea)
- `env-analyze` (standalone environment diagnostic) — note: renamed from earlier draft `env-analyzer` to match slash command `/env-analyze`
- `refactor` (refactor across N files with safety nets)
- `migrate` (schema/library/version migration)
- `spike` (time-boxed exploration)
- `security-audit` (full repo security scan + threat model)
- `docs-pack` (user-facing docs generation; distinct scope from existing `docs` knowledge skill which stays in KEEP)
- `ai-skills-init` (bootstrap a target repo)

**Companion skills (9 NEW, per `01-WORKFLOW-SPECS.md` Part B):**
- `ralph` (RALF loop power-user entry)
- `eval` (skill/agent eval runner)
- `memory-init`
- `memory-recall`
- `plugin-doctor` (self-diagnostic)
- `context-load` (project context loader with per-agent slicing)
- `subagent-spawn` (typed delegation helper)
- `learnings-write` (curated write to L4/L5)
- `plugin-skill-create` (plugin-scoped skill scaffolding — narrower than Anthropic's `skill-creator`)

**Math check (verified clean 2026-04-26 Round 4):**
- Existing handled: 20 KEEP + 13 REFACTOR + 4 MERGE-input + 5 ARCHIVE = **42 ✓** matches the verified count of existing skill directories
- In-plugin total: 20 KEEP + 13 REFACTOR (one renamed: team-dev → develop) + 2 MERGE-output + 17 NEW = **52 skills**

**Slash command coverage (each maps to a skill directory of the same name):**
- 10 user-invocable workflow slash commands: `/feature-design` (NEW), `/develop` (REFACTOR-RENAMED from team-dev), `/bugfix` (REFACTOR), `/env-analyze` (NEW), `/refactor` (NEW), `/migrate` (NEW), `/spike` (NEW), `/security-audit` (NEW), `/docs-pack` (NEW), `/ai-skills-init` (NEW)
- 9 companion slash commands: `/ralph`, `/eval`, `/plugin-doctor`, `/memory-init`, `/memory-recall`, `/learnings-write`, `/context-load`, `/subagent-spawn`, `/plugin-skill-create` (all NEW)
- = 19 user-invocable skills total. Other 33 skills are knowledge / auxiliary, activated by Claude on context match.

### 2.2 Agents disposition

All 22 existing agents are domain-clean — independent of any specific consumer project (verified by grep on company-specific terms, ICP language, product names). They carry over with the following targeted changes:

**Mandatory refactor — drop `permissionMode: plan` field on these 9 agents:**
`cloud-architect`, `content-designer`, `content-writer`, `devops-architect`, `marketing-strategist`, `product-manager`, `solution-architect`, `system-architect`, `ui-ux-designer`. The intent (read-only behaviour) is preserved by their existing `disallowedTools: Write, Edit` setting.

**Defensive normalization on all 22 agents:**
- Verify `tools` list is minimal (least privilege)
- Add `effort` field (`low`/`medium`/`high`) where missing
- Add `maxTurns` cap (default 30) where missing
- Add `max_output_tokens` recommendation per role type (**G4** — values from context-engineering guide §7.4):
  - Summarization roles (e.g., reviewer summarising findings): 300–600
  - Q&A / RAG-style roles (e.g., context-engineering, prompt-engineer answering questions): 500–1000
  - Report/explanation roles (e.g., system-architect writing ARCHITECTURE.md): 800–1500
  - Code-generation roles (e.g., python-engineer, java-engineer): 1500–2500
  - Orchestrator roles (feature-design-lead): 800–1500 (lead writes briefs, not code)
- Confirm absence of `hooks`, `mcpServers` (none have these — already verified)

**Four new agents introduced (22 → 26):**

| New Agent | Purpose | Model | Effort | Tools |
|---|---|---|---|---|
| `security-engineer` | Threat modelling, dependency CVE checks, secret-handling, authn/authz patterns, **OWASP GenAI/LLM Top 10 (2025)** baseline (LLM01 prompt injection, LLM02 sensitive info disclosure, LLM06 excessive agency, LLM07 system prompt leakage, LLM10 unbounded consumption), OWASP Web Top 10 for code-level review. Powers `/security-audit`, contributes to `/feature-design` Wave 2 (**G3**) | Sonnet | high | Read, Grep, Glob, Bash; disallowedTools: Write, Edit |
| `feature-design-lead` | Orchestrates multi-role design pack assembly (PRD + ARD + UX + plan). Spawns 6–10 subagents in waves | Opus | high | (orchestrator only) Task; disallowedTools: Write, Edit, Bash |
| `eval-judge` | Grades skill/agent outputs against rubrics; powers `/eval` and RALF subjective oracles | Haiku (override to Sonnet on weak rubrics) | medium | Read, Grep, Glob; disallowedTools: Write, Edit, Bash |
| `memory-curator` | Reviews session output (when triggered) and writes durable learnings to `.ai-skills-memory/learnings.md` and optionally `~/.claude/ai-skills/learnings.md` | Haiku | low | Read, Write (limited to memory dirs by hook guard) |

### 2.3 Rules disposition

Carry over all 8 rules. Promote two from project-only to plugin-shipped:
- `task-completion.md` → makes mandatory pre-completion audit a plugin-wide guardrail
- `failure-recovery.md` → loop-detection becomes a plugin guardrail

Add **four** new plugin-shipped rules:
- `subagent-isolation.md` — when to delegate vs. when to inline
- `memory-discipline.md` — what types belong in which memory layer (mirrors Anthropic memory tool best practices)
- `ralph-budget.md` — iteration caps, cost ceilings, mandatory kill-criterion for any RALF loop
- `untrusted-content-wrapping.md` (**G1**) — every read of L0/L2/L4 content, every subagent return, every tool output >200 tokens MUST be wrapped in `<untrusted_content>` envelope before injection. Treats indirect prompt injection as the highest-risk vector per OWASP LLM01. Wrapper template canonical to `plugin/memory/templates/untrusted-content-wrapper.md`

### 2.4 Hooks disposition

Carry over all 4 existing Python scripts unchanged (just relocated to `plugin/hooks/scripts/`).

**New hooks added in v0.1** (significantly expanded after the best-practices reverse-check):

| Hook | Event | Type | Purpose | Toggle |
|---|---|---|---|---|
| `session-start-context.py` | `SessionStart` | command | Detects target repo, reads up to 8KB of `CLAUDE.md`/`AGENTS.md`/`ARCHITECTURE.md`, runs PII filter, surfaces presence of `.ai-skills-memory/`, injects compact project summary, initializes session token meter. No-op if no project files | Always on |
| `instructions-loaded-augment.py` | `InstructionsLoaded` | command | When CLAUDE.md or any rule loads, supplements with relevant `.ai-skills-memory/.committed/conventions.md` excerpt | Always on (no-ops if no committed memory) |
| `ralph-stop.py` | `Stop` | command | If active RALF session exists at `.ai-skills-memory/ralph/<run-id>/active.lock`, intercepts exit, evaluates oracle, checks budget caps (iter/tokens/wall-time/kill-on signal), re-injects original prompt + last-iteration diff on failure | Always on (no-ops without active RALF) |
| `pre-compact-memory-flush.py` | `PreCompact` | command | **CRITICAL for memory architecture** — writes durable session learnings to L4 (`.ai-skills-memory/learnings.md`) BEFORE context is lost to compaction | Always on |
| `session-end-finalize.py` | `SessionEnd` | command | Summarizes session run log (`runs/<id>.jsonl`), updates project baselines, releases any RALF locks left dangling | Always on |
| `subagent-start-budget.py` | `SubagentStart` | command | Checks session token meter against soft/hard caps before allowing subagent spawn; prompts user if approaching cap | Always on |
| `subagent-stop-learnings.py` | `SubagentStop` | command | Captures non-trivial subagent outputs for memory-curator review | **Opt-in** via `userConfig.subagent_learnings_enabled` |
| `task-event-log.py` | `TaskCreated`, `TaskCompleted` | command | Writes structured TodoList events to `runs/<id>.jsonl` for observability | Always on |
| `tool-failure-log.py` | `PostToolUseFailure`, `StopFailure` | command | Logs tool/turn failures to `.ai-skills-memory/errors.log` separate from successes | Always on |
| `tool-output-wrap.py` (**G1**) | `PostToolUse` (matcher: `Read|Bash` for memory dirs and project files) | command | Wraps tool outputs >200 tokens in `<untrusted_content>` envelope before injection. Defends against indirect prompt injection from CLAUDE.md, /env-analyze logs, learnings.md content | Always on |
| `tool-output-normalize.py` (**G2**) | `PostToolUse` (matcher: same as wrap, fires after wrap) | command | For tool outputs >2000 tokens: extract top-k items, summarize via Haiku, annotate with `{tool, call_id, ts, original_tokens, injected_tokens, truncated}` envelope. Tracks `injected_tokens` against session token meter | Always on |

PII regex patterns for SessionStart and PreCompact filters live in `plugin/hooks/scripts/pii-patterns.txt` (emails, SSNs, common API key shapes, AWS/GCP/Azure secret patterns). Users extend per-project via `.ai-skills-memory/.committed/pii-patterns.txt`.

**Hook execution types in use:** all `command` (Python scripts) in v0.1. Plans for v0.2: migrate `eval-judge` invocation from custom Python wrapper to `prompt:rubric.md` hook type — eliminates ~200 lines of LLM-call boilerplate.

---

## 3. Plugin Design

### 3.1 Repository layout

```
ai-skills/                                    # repo root (current working dir)
├── .claude/                                  # LEGACY — keep working until plugin lands
├── .codex/                                   # LEGACY — frozen
├── .windsurf/                                # LEGACY — frozen
├── .agents/                                  # LEGACY — frozen
├── plugin/                                   # NEW: the plugin source
│   ├── .claude-plugin/
│   │   └── plugin.json                       # manifest
│   ├── skills/                               # 52 skills (20 KEEP + 13 REFACTOR + 2 MERGE-output + 17 NEW = 52; per §2.1)
│   │                                          #   ALL slash-invokable workflows are user-invocable skills here
│   │                                          #   (no separate commands/ dir per modern Anthropic guidance)
│   ├── agents/                               # 26 (22 existing normalized + security-engineer + 3 orchestrators)
│   ├── hooks/
│   │   ├── hooks.json                        # event wiring
│   │   └── scripts/                          # 4 existing + 3 new
│   ├── rules/                                # 8 existing + 3 new
│   ├── eval/                                 # plugin-wide eval framework
│   │   ├── runner.py                         # tier 1/2/3 entrypoint
│   │   ├── config.json                       # token budgets per tier
│   │   ├── judge-rubrics/                    # one .md per workflow + cross-cutting rubrics
│   │   ├── cases/<skill-name>/               # JSON eval cases per skill
│   │   ├── baselines/                        # last-good scorecard per skill
│   │   └── calibration/<rubric>/             # 5 known-good + 5 known-bad samples per rubric
│   ├── examples/                             # few-shot example library (G9, content authored Phase 3)
│   │   └── <skill-name>/
│   │       └── <example-id>.json             # {input, output, tags[], output_contract_version}
│   ├── schemas/                              # JSON schemas for spawn payload, return contract (G7)
│   │   ├── spawn-payload.schema.json
│   │   └── return-contract.schema.json
│   ├── memory/                               # plugin-shipped templates only (read-only)
│   │   └── templates/
│   │       ├── ai-skills-memory.gitignore
│   │       ├── committed-readme.md
│   │       └── learnings-schema.md
│   ├── output-styles/                        # named output styles for workflow-specific formatting
│   │   ├── concise-pr.md
│   │   └── design-pack.md
│   ├── monitors/                             # background monitors (opt-in via userConfig)
│   │   └── monitors.json
│   ├── docs/                                 # USER-FACING documentation (Phase 2)
│   │   ├── getting-started.md
│   │   ├── workflows/                        # one .md per workflow
│   │   └── concepts/                         # memory.md, eval.md, ralf.md
│   ├── CHANGELOG.md
│   └── README.md
├── plugin-design/                            # THIS DOC + follow-ups
│   ├── 00-PHASE-1-PLAN.md                    # ← you are here
│   ├── 01-WORKFLOW-SPECS.md                  # to be written
│   ├── 02-EVAL-FRAMEWORK.md
│   ├── 03-MEMORY-ARCHITECTURE.md
│   └── 04-MIGRATION-CHECKLIST.md
└── PARITY.md                                 # (eventually deprecated)
```

### 3.2 `plugin.json` (proposed)

```json
{
  "name": "ai-skills",
  "version": "0.1.0",
  "description": "Reusable team-of-agents plugin for the full SDLC — feature design, development, bugfix, environment analysis — with built-in RALF iteration loop, layered memory, and systematic eval. Project-agnostic: operations live in plugin, project context lives in target repo (CLAUDE.md / AGENTS.md).",
  "author": { "name": "<author-name>", "email": "<author-email>" },
  "license": "MIT",
  "homepage": "https://github.com/<owner>/ai-skills",
  "repository": "https://github.com/<owner>/ai-skills",
  "keywords": ["sdlc", "agent-team", "feature-design", "ralf", "eval", "memory", "subagents", "code-review", "bugfix"],

  "dependencies": [],

  "userConfig": {
    "session_token_soft_cap": {
      "type": "number",
      "title": "Session token soft warn",
      "description": "Cumulative session token count at which the plugin warns the user.",
      "default": 1000000
    },
    "session_token_hard_cap": {
      "type": "number",
      "title": "Session token hard pause",
      "description": "Cumulative session token count at which the plugin pauses and asks for confirmation.",
      "default": 1500000
    },
    "ralph_default_max_iter": {
      "type": "number",
      "title": "RALF default max iterations",
      "description": "Default --max-iterations cap for /ralph (per D12).",
      "default": 10
    },
    "ralph_default_token_budget": {
      "type": "number",
      "title": "RALF default token budget",
      "description": "Default --token-budget cap for /ralph (per D12).",
      "default": 200000
    },
    "ralph_default_time_cap_minutes": {
      "type": "number",
      "title": "RALF default wall-time cap (minutes)",
      "description": "Default --time-cap for /ralph (per D12).",
      "default": 120
    },
    "ralph_session_max_iter": {
      "type": "number",
      "title": "RALF session-aggregate max iterations",
      "description": "Total RALF iterations across ALL workflows in one session (Round 6 HIGH-3). Prevents runaway when chaining /feature-design → /develop etc.",
      "default": 20
    },
    "ralph_session_token_budget": {
      "type": "number",
      "title": "RALF session-aggregate token budget",
      "description": "Total RALF token spend across all workflows in one session (Round 6 HIGH-3).",
      "default": 400000
    },
    "ralph_session_time_cap_minutes": {
      "type": "number",
      "title": "RALF session-aggregate wall-time cap (minutes)",
      "description": "Total RALF wall-time across all workflows in one session (Round 6 HIGH-3).",
      "default": 180
    },
    "subagent_learnings_enabled": {
      "type": "boolean",
      "title": "Capture subagent outputs as learnings",
      "description": "Opt-in: enables subagent-stop-learnings hook to capture non-trivial outputs for memory-curator review.",
      "default": false
    },
    "user_global_memory_enabled": {
      "type": "boolean",
      "title": "Allow writes to user-global memory (L5)",
      "description": "Opt-in: allows /learnings-write to persist patterns to ~/.claude/ai-skills/learnings.md across all projects.",
      "default": false
    },
    "env_watch_enabled": {
      "type": "boolean",
      "title": "Enable Docker compose health monitor",
      "description": "Opt-in: starts a background monitor watching docker-compose services if a compose file is detected at session start.",
      "default": false
    }
  },

  "outputStyles": "./output-styles/",
  "monitors": "./monitors/monitors.json"
}
```

The `userConfig` block is the **declarative config surface**. Users set these values once at install via the plugin install dialog; no hand-editing JSON files. Sensitive fields (none in v0.1, but credentials in v0.3+) get `"sensitive": true`.

### 3.3 Component map

In modern Claude Code, **slash commands ARE user-invocable skills** — there is no separate "thin entrypoint" file layer. A `/feature-design` invocation activates `skills/feature-design/SKILL.md` directly.

```
USER PROMPT  →  Main thread (Claude Code)
                  │
                  ├─ SessionStart hook  →  load project context (CLAUDE.md, memory)
                  │                          → init session token meter
                  │
                  ├─ Skill activation
                  │     • Slash-invoked (user-invocable, context: fork):
                  │       /feature-design  /develop  /bugfix  /env-analyze
                  │       /ralph    /eval    /plugin-doctor
                  │       /memory-init  /memory-recall  /learnings-write
                  │       /refactor  /migrate  /spike  /security-audit
                  │       /docs-pack  /ai-skills-init  /plugin-skill-create
                  │     • Auto-activated (by description match):
                  │       knowledge skills, validators, content-load slicers
                  │
                  ├─ Agent delegation (Task / Agent tool)
                  │     22 normalized domain agents
                  │     + 1 new domain agent (security-engineer)
                  │     + 3 new orchestrators (feature-design-lead, eval-judge, memory-curator)
                  │
                  └─ Hook enforcement (always-on, fail-open with warn)
                        block-dangerous · block-secrets · block-sensitive · log-actions
                        session-start-context · ralph-stop · subagent-stop-learnings(opt-in)
```

### 3.4 Memory architecture (5 layers + 1 host coexistence)

| Layer | Lives in | Lifetime | Writer | Purpose |
|---|---|---|---|---|
| **L0. Cowork host** (out-of-plugin) | `~/.../spaces/<id>/memory/` | Cowork-managed | Cowork only | Plugin NEVER writes. Reads only if exposed as advisory context |
| **L1. Plugin templates** | `${CLAUDE_PLUGIN_ROOT}/memory/templates/` | Read-only, ships with plugin | Plugin author | Schemas, gitignore template, learnings-schema, rubric defaults |
| **L2. Project static** | `<repo>/CLAUDE.md`, `AGENTS.md`, `ARCHITECTURE.md` | Per-repo, owned by repo | Repo maintainer | Read at SessionStart, ≤8KB slice with PII filter |
| **L3. Session** | In-conversation TodoList + `<repo>/.ai-skills-memory/sessions/<run-id>/` | Until session ends (then summarized) | Main thread + subagents | Active plan, subagent reports, RALF iteration logs, run jsonl |
| **L4. Project cross-session** | `<repo>/.ai-skills-memory/` | Per-repo, persistent. Gitignored by default; opt-in `.committed/` | Hooks + skills + memory-curator | Known traps, confirmed conventions, RALF run summaries, eval baselines, learnings |
| **L5. User-global** | `~/.claude/ai-skills/learnings.md` | Forever, across all projects | memory-curator (opt-in only) | Patterns the user explicitly opted to remember globally |

**Non-interference contract with L0 (Cowork):** Plugin treats L0 as opaque. Never writes. May read if Cowork exposes content as advisory context. On any conflict between L0 and L4, plugin trusts the more recently confirmed layer.

**Discipline enforcement** by the new `memory-discipline.md` rule:
- L4/L5 writes go through `memory-curator` agent (centralized review)
- PII filter runs on every write
- L5 writes require explicit user opt-in (`/learnings-write --global`)
- Per-project paths NEVER written to L5
- Secrets NEVER written to any layer
- `.ai-skills-memory/.committed/` writes are schema-validated (allowlist patterns)

### 3.5 RALF integration

**Invocation contract:**
```
/ralph "<task>" --oracle <oracle-spec> --kill-on <signal-spec>
       [--max-iterations N=10] [--token-budget N=200000] [--time-cap MIN=120]
```

**Oracle types** (`--oracle TYPE:VALUE`):
- `cli:./test.sh` — shell command, exit 0 = pass
- `judge:rubric-name.md` — invokes `eval-judge` agent against named rubric, threshold from rubric file
- `regex:./out.log:^DONE$` — pattern match in named file
- `python:./check.py` — custom predicate

**Kill-on signal types** (`--kill-on TYPE:VALUE`, mandatory unless using a workflow with built-in signal):
- `oracle-pass` — happy stop on first oracle success
- `same-error-repeats:3` — same error string 3 iterations in a row
- `regex:PATTERN` — regex matches in latest model output
- `python:./kill.py` — custom kill predicate (exit 0 = continue, 2 = kill)
- `no-progress:N` — N iterations with no file diff

**Loop machinery:**
```
/ralph entrypoint validates args (rejects if --kill-on missing)
  → writes  .ai-skills-memory/ralph/<run-id>/{config.json, active.lock, initial-prompt.md}
  → enters loop:
       iteration N:
         Claude works → tries to Stop
         ralph-stop.py intercepts:
           a. run oracle → if pass: write SUCCESS, release lock, allow Stop
           b. check kill-on signal → if hit: write KILLED, release lock, allow Stop
           c. check budgets (iter / tokens / wall-time) → if exceeded: write BUDGET_EXCEEDED, allow Stop
           d. otherwise: append iteration log, re-inject prompt + last-iteration diff/error
       writes per-iteration: .ai-skills-memory/ralph/<run-id>/iter-NNN/{prompt.md, output.md, diff.patch, oracle-result.json}
  → on exit: writes .ai-skills-memory/ralph/<run-id>/budget.json with totals
```

**Session-level RALF aggregate budget (Round 6 HIGH-3):** beyond per-workflow RALF caps (D12), `ralph-stop.py` enforces a **session-level aggregate** to prevent runaway cost when workflows chain (e.g., `/feature-design` → `/develop` in one session). Defaults:
- Aggregate iter cap: **20** (across all workflows in one session)
- Aggregate token cap: **400K**
- Aggregate wall-time cap: **3 hours**

`ralph-stop.py` reads cumulative RALF token spend from session token meter (§3.11) before allowing iteration ≥ 2 of any workflow. Hard kill on aggregate exceedance, regardless of per-workflow budget remaining. Overridable via 3 `userConfig` knobs: `ralph_session_max_iter`, `ralph_session_token_budget`, `ralph_session_time_cap_minutes` (defined in §3.2; total `userConfig` knob count = 11).

**Three uses already locked:**
1. **Inside `/feature-design`** — oracle = `judge:feature-design-rubric.md`, kill-on = `regex:RUBRIC_FAILED_3X`. Built-in caps: 5 iter, 250K tokens, 60 min.
2. **Inside `/develop`** — oracle = `cli:./run-tests.sh`, kill-on = `same-error-repeats:3`. Built-in caps: 8 iter, 640K tokens, 90 min.
3. **Inside `/bugfix`** — oracle = `cli:./reproduction-test.sh`, kill-on = `no-progress:2`. Built-in caps: 6 iter, 300K tokens, 60 min.
4. **Standalone `/ralph` command** — power-user mode; defaults 10 iter / 200K tokens / 120 min.

### 3.6 Eval framework (3-tier)

**Tier 1 — Linters (every commit, ZERO LLM cost):**
- frontmatter validator (`name`, `description`, char limits, required fields)
- internal reference validator (`@skill-name`, `Agent(role)`, file paths resolve)
- char-limit guard (12K skills hard cap, 5K SKILL.md body soft target)
- Python AST check on hooks
- JSON schema check on `plugin.json`, `hooks.json`, `eval/config.json`
- Forbidden-field check on agent frontmatter (`hooks`, `mcpServers`, `permissionMode`)

**Tier 2 — Smoke tests (CI, sampled, ~60K tokens budget):**
- `claude plugin validate` on each PR (zero LLM cost)
- **Sampled** skill activation precision: 10 randomly sampled skills × 20 prompts each (= 200 prompts). Goal: ≥80% correct activation, ≤5% false positive on adversarial prompts. ~60K tokens with Haiku.
- Subagent contract smoke: each new/refactored agent gets one canary prompt; output must match its declared schema. ~30K tokens.

**Tier 3 — Anthropic-style behavioral evals (release gate, ~30K-60K per skill):**
- Per skill: `plugin/eval/cases/<skill>/<case-id>.json`
- Executor sub-agent runs case (Sonnet)
- Judge sub-agent grades against rubric (**Haiku default; Sonnet override per case if rubric calibration is weak — see judge calibration below**)
- Blind-comparator: see mechanism below
- `/eval <skill>` runs all cases for one skill; `/eval --all` gates release

**Eval case JSON schema:**
```json
{
  "id": "feature-design-001",
  "skill": "feature-design",
  "prompt": "Design a feature for live collaborative cursors in a markdown editor.",
  "context_files": [".ai-skills-memory/.committed/sample-CLAUDE.md"],
  "oracle": {
    "type": "judge",
    "rubric": "feature-design.md",
    "min_score": 4.0,
    "judge_model": "haiku"
  },
  "expected_artefacts": ["docs/features/*/PRD.md", "docs/features/*/IMPLEMENTATION-PLAN.md"],
  "anti_patterns": ["mentions specific company name", "PRD < 500 words", "no acceptance criteria"],
  "max_tokens": 50000,
  "tags": ["workflow", "design", "p0"]
}
```

**Blind-comparator mechanism:** runs the same prompt in an isolated `Agent` call with `skills: []` set in agent frontmatter (suppresses skill activation in that subagent). If skills cannot be empty in agent frontmatter, fall back to instruction-based suppression: prepend `IMPORTANT: do not invoke or load any skills for this turn.` (weaker but workable). Comparator's score is subtracted from full-run score → "skill lift."

**Judge calibration check:** at install time, `/plugin-doctor --calibrate-judge` runs eval-judge against 5 known-good and 5 known-bad outputs per rubric. Reports Spearman correlation. Threshold ≥0.7. Below threshold: prompt user to upgrade rubric to Sonnet judge.

**feature-design rubric skeleton** (full rubric in Phase 2 at `plugin/eval/judge-rubrics/feature-design.md`):

| Dimension | L1 (poor) | L3 (acceptable) | L5 (excellent) |
|---|---|---|---|
| Completeness | Missing required artefacts | All artefacts present, some shallow | All artefacts deeply specified |
| Internal consistency | Cross-doc contradictions | Mostly consistent, minor gaps | Fully traceable, zero contradiction |
| Traceability (req→component→test) | Mostly absent | Partial coverage | Every requirement maps to component AND test |
| Handoff clarity (engineer-readiness) | Engineer cannot start | Workable with questions | Engineer starts immediately |
| Risk coverage | Risks ignored | Top risks mentioned | Risks named, scored, mitigations specified |
| GEO/marketing readiness (if public) | Generic AI-sounding | Some optimization | Passes geo-audit + humanizer |

Average ≥4.0 with no dimension below 3 to pass.

All three tiers wrap the same machinery — `eval/runner.py` is the single entrypoint with `--tier {1,2,3}` flag. Token budgets per tier from Section 7a Q4.

### 3.7 Subagent / team integration

Routing rules baked into `subagent-isolation.md`:

| Use case | Mechanism | When |
|---|---|---|
| Independent investigation (research, audit, parallel reviews of distinct artefacts) | `Agent` × N in parallel | Multiple findings can be merged at the end; outputs are documents, not code edits |
| Multi-stack code change | `TeamCreate` + role-mapped developers + reviewer + qa | When `TeamCreate` available |
| Code-modifying stages of any workflow (write/edit ops) | Sequential `Agent` calls or `SendMessage` (one writer at a time per file) | Mandatory — file conflict prevention |
| Document-production stages (analysis, design, audit) | Parallel `Agent` × N permitted | Even within code-touching workflows, design phases may parallelize |
| Single-file edit | Inline (no subagent) | Cost discipline |
| Anything > 3 deliverables / > 30 min | Mandatory subagent decomposition | Context budget discipline |

**Hot rule:** "code-modifying stages are sequential per file; analysis and document-production stages may be parallel." This replaces the over-broad "always sequential for code-touching" wording.

**Runtime detection of `TeamCreate`:** the `team-dev` / `team-bugfix` skills probe for the team primitive at activation time (per existing `team-protocols/SKILL.md` detection logic) and fall back to standalone `Agent` calls if absent. No design changes needed; existing logic carries over.

Existing `team-protocols/` resources (`developer-protocol.md`, `reviewer-protocol.md`, `lead-protocol.md`, `role-selection-table.md`) **carry over verbatim** — they are excellent.

### 3.8 Failure modes and recovery

| Failure | Detection | Action |
|---|---|---|
| Subagent error / non-zero exit | `Agent` tool result | Lead retries once with explicit error context. If retry fails, escalate to user with full trace from `.ai-skills-memory/sessions/<id>/subagent-errors.log` |
| Hook script crash | Stderr / non-2 exit | **Fail open with warning** — never block all tool use because of a buggy hook. Append crash to `.ai-skills-memory/hook-errors.log`. `/plugin-doctor` surfaces |
| Oracle error in RALF | Oracle exit ≠ 0 AND ≠ 2 (ambiguous) | Treat as unknown state → kill loop, write `ORACLE_ERROR` status, full diagnostic to user |
| Eval runner crash mid-suite | Python exception | Partial results saved per case as completed; `--resume` flag picks up from last completed case |
| Token budget hit during workflow | Per-session token meter | Soft warn at threshold; hard pause at cap; user prompted to confirm continuation, raise budget, or abort |
| RALF kill-criterion missing at invocation | `/ralph` arg validator | Hard reject with helpful error pointing to kill-on signal docs |
| Cowork host memory conflict (L0 vs L4) | memory-curator detection | Trust most-recently-confirmed layer; flag the conflict to user |

### 3.9 Observability

Every workflow writes a structured run log:

```
.ai-skills-memory/runs/<run-id>.jsonl
```

Schema per line: `{ts, event, workflow, agent, model, tokens_in, tokens_out, duration_ms, ...}`

Events captured: `workflow_start, skill_activated, agent_spawned, agent_returned, hook_fired, oracle_checked, ralf_iter, budget_warn, workflow_end`.

`/plugin-doctor --runs [--last N]` summarizes recent runs: durations, token totals, success rates, hot skills.

### 3.10 Locale handling

- **Conversational replies:** orchestrators inject `RESPOND IN: <user-locale>` into spawned-subagent prompts when user's prior turn was non-English. Default English.
- **Persisted artefacts:** ALL files written to disk (PRD, code, comments, memory, eval cases, judge rubrics) MUST be in English. This is a global rule in `plugin/rules/global-rules.md` (carries over from existing).
- **Locale detection:** `session-start-context.py` probes the user's prior turn(s) for non-English content (Cyrillic / CJK / etc. unicode block check) and writes `.ai-skills-memory/session/<id>/locale.txt`. Skills read this file.

### 3.11 Per-session token meter

`session-start-context.py` initializes `.ai-skills-memory/session/<id>/token-meter.json`. Every skill body includes a small post-call increment (helper available from `plugin/skills/_lib/meter.py`). Triggers:

- Soft warn at 1M cumulative session tokens — orchestrator surfaces a warning to user
- Hard pause at 1.5M — orchestrator stops mid-workflow, asks user to confirm continuation, raise the cap, or abort

User can override defaults in `.ai-skills-memory/config.json` → `session_token.{soft,hard}`.

### 3.12 Context manifest pattern

When the Lead spawns multiple subagents for the same workflow, naively passing the full project context to each agent multiplies setup cost (5 agents × 30K = 150K tokens just to brief them).

The `context-load` skill produces **per-agent context slices**:

- `context-load --for db-engineer` returns DB-relevant excerpts only (schemas, migrations dir, ARCHITECTURE.md DB section)
- `context-load --for ui-ux-designer` returns UI-relevant excerpts (component dir, design doc, accessibility rules)
- `context-load --for security-engineer` returns auth/secrets/dependency surface

Each orchestrator (e.g., `feature-design-lead`) calls `context-load --for <role>` once before spawning each subagent and embeds the slice in the spawn prompt. Cuts wave-2 setup from ~150K to ~40K tokens.

---

## 4. Long Workflow Specs (overview — full specs in `01-WORKFLOW-SPECS.md`)

### 4.1 `/feature-design` — Design pack from idea
**Input:** 1-3 sentence idea.
**Output:** Complete design pack in `<repo>/docs/features/<feature-id>/`:
- `PRD.md` (product-manager)
- `MARKET-ANALYSIS.md` (marketing-strategist) — competitive snapshot, GTM angle
- `ARCHITECTURE.md` (system-architect / solution-architect)
- `UX-FLOW.md` + Mermaid wireframes (ui-ux-designer)
- `DATA-MODEL.md` (db-engineer if relevant)
- `IMPLEMENTATION-PLAN.md` (lead consolidates per-stack engineer input)
- `RISKS.md` (system-architect + qa-engineer)
- `REVIEW-LOG.md` (auto-generated trace of review cycles)

**Mechanism:** `feature-design-lead` orchestrates 6–10 subagents in parallel waves. Each agent receives a **per-role context slice** from `context-load --for <role>`, not the full project context.

- **Wave 1** (parallel — independent drafts): product-manager (PRD), marketing-strategist (MARKET-ANALYSIS if public-facing), system-architect (ARCHITECTURE skeleton). Each produces a first draft from the user's idea + their context slice.
- **Wave 2** (parallel — domain reviews of wave-1 outputs): ui-ux-designer (UX-FLOW + wireframes), db-engineer (DATA-MODEL if relevant), **security-engineer** (threat model + risk surface). Each reviews wave-1 in its lane and produces its own artefact.
- **Wave 3** (sequential — cross-check): product-manager-reviewer (a fresh product-manager subagent) + system-architect (the original, in reviewer role) cross-check coherence; eval-judge scores against `feature-design.md` rubric.
- **RALF loop** (built-in): if rubric score < 4.0 OR any dimension < 3, re-prompt the relevant wave with reviewer feedback. Caps: 5 iter / 250K tokens / 60 min. Kill-on: `regex:RUBRIC_FAILED_3X`.
- Lead writes `IMPLEMENTATION-PLAN.md` last, with explicit work packages mapped to engineer roles for `/develop`.

**Coordination of inputs:** the user's 1–3 sentence idea is the only required input. `context-load` produces per-role slices from the target repo. Wave 1 outputs feed Wave 2 inputs. The Lead enforces gate rules (Wave 2 cannot start until Wave 1 complete; Wave 3 cannot start until Wave 2 complete).

**Eval rubric** (skeleton in 3.6, full rubric in `plugin/eval/judge-rubrics/feature-design.md`): 6 dimensions × 5 levels — completeness, internal-consistency, traceability, handoff-clarity, risk-coverage, GEO-readiness-if-public.

### 4.2 `/develop` — Full SDLC implementation
**Input:** path to design pack from `/feature-design` (or a PRD).
**Output:** Working code + tests + PR.

**Mechanism:** evolution of existing `team-dev`:
- Reads `IMPLEMENTATION-PLAN.md`, spawns engineers per work package using `role-selection-table.md`
- Pipeline preserved as **3-gate**: DEVELOP → REVIEW → QA. **SRE-smoke is a verification step inside QA**, not a new gate. QA passes only if both unit/integration tests AND SRE-smoke pass (when SRE-smoke is applicable, i.e., Docker compose detected).
- SRE-smoke step (inside QA): spins up local env per `analyze-local`, runs smoke tests, tears down
- New: PR description auto-built from `REVIEW-LOG.md` of the design pack + actual diff summary + run jsonl token totals
- RALF loop on the test gate — if QA fails, the assigned developer subagent re-runs (oracle = test-suite exit code; kill-on = `same-error-repeats:3`; caps: 8 iter / 640K tokens / 90 min)

### 4.3 `/bugfix` — Triage → diagnose → fix → ship
Refactor of existing `bugfix` + `team-bugfix`:
- Step 1: env-analyzer (new, see 4.4) decides if infra or code
- Step 2: if code, parallel investigation by 2 developers (different roles if cross-stack) to triangulate the cause
- Step 3: single developer fixes (chosen by Lead based on convergent diagnosis)
- Step 4: full DEVELOP → REVIEW → QA pipeline
- RALF on reproduction test: must reproduce → must fail → must pass after fix

### 4.4 `/env-analyze` — Environment diagnostic (NEW standalone)
Promotes the embedded env-analyzer in `team-bugfix` to first-class:
- Scope: local Docker compose, K8s (kind/minikube/cloud), CI runner state
- Applies sre-engineer + devops-engineer in parallel
- Produces `ENV-REPORT.md` with: container/pod status table, log excerpts (filtered), networking sanity, resource saturation, identified anomalies, recommended actions
- Optional `--auto-fix` flag — only for the safe class (restart, clear cache, regenerate config)

### 4.5 Recommended additional workflows

| Slash command | Purpose | Why include |
|---|---|---|
| `/refactor` | Plan + execute a refactor across N files with safety nets | Distinct enough from `/develop` to deserve its own pipeline (no new behavior, must preserve external contract) |
| `/migrate` | Schema/library/version migration (DB schema, framework upgrade) | Specialized review checklist (rollback plan, data integrity, dual-write) |
| `/spike` | Time-boxed exploration with structured writeup | Outputs a spike report with go/no-go recommendation; opposite discipline of `/develop` |
| `/release` | Pre-release checklist + changelog + version bump + tag | Already in skills, formalize as workflow |
| `/security-audit` | Full repo security scan + threat model | Different rubric from code-review; audit is broader |
| `/docs-pack` | Generate user-facing docs (README, API ref, runbook) for an existing module | Multi-agent (content-writer + engineer subject expert + GEO/SEO pass) |
| `/ai-skills-init` | Bootstrap a new project with `CLAUDE.md`, `AGENTS.md`, `.ai-skills-memory/` | Critical for the data/operations split: this is how a target repo becomes "ai-skills-aware" |
| `/plugin-skill-create` | Plugin-scoped skill scaffolding with our eval/memory/RALF wiring pre-built. NARROWER than Anthropic's existing `skill-creator` plugin — defer general skill creation to that tool | Avoids duplicating Anthropic's tool while still giving users a fast path to add a skill that fits OUR plugin conventions |

### 4.6 Workflow common pattern

Every long workflow follows the same scaffold:

```
1. Context load    — read CLAUDE.md, AGENTS.md, .ai-skills-memory/
2. Clarify         — AskUserQuestion if ambiguity > threshold
3. Plan            — present plan (dependency-ordered work packages)
4. User approval gate
5. Spawn team      — per role-selection-table.md
6. Pipeline        — sequential gates DEVELOP → REVIEW → QA (per workflow's variant)
7. Eval            — eval-judge scores against rubric
8. RALF            — loop if rubric not met, capped
9. Memory write    — durable learnings to .ai-skills-memory/
10. Final report   — TodoList check + completion report (per task-completion rule)
```

---

## 5. Migration Plan (incremental, parallel to current system)

> **Phase numbering reconciled to user mental model (Round 5 S4):** Phase 1 = design (this body of docs). Phase 2 = implementation begins. Older drafts called design "Phase 0"; updated for clarity.

### Phase 1 — Design (COMPLETE as of 2026-04-26)
The 7 design documents in `plugin-design/` (this doc + 00a + 01-05). All design decisions, architecture, asset disposition, migration plan, gap analysis. No code written.

### Phase 2 — Implementation: Core scaffolding (per `04-MIGRATION-CHECKLIST.md` batches B1-B10a)
- Plugin skeleton + manifest + hook config format upgrade (B1-B2)
- Migrate 20 KEEP skills as-is (B3)
- Migrate 22 agents (drop `permissionMode` from 9, add `effort`/`maxTurns`/`max_output_tokens`) (B4)
- Add 4 new agents: `security-engineer`, `feature-design-lead`, `eval-judge`, `memory-curator` (B5)
- Carry 8 existing rules + add 4 new (B6-B7)
- Add 12 new hooks across 13 lifecycle events + shared `_lib.py` helper (B8) — per Round 8 CRIT-1 (was 11, +1 for `pre-tool-use-committed-write`)
- JSON schemas + memory templates (B9)
- Output styles + Tier 1 linter scaffold + 17 rubric skeletons (B10)
- Calibration samples seed: 34 minimal (1 good + 1 bad × 17 rubrics) (B10a)

### Phase 3 — Implementation: Workflows + user-facing docs (per `04-MIGRATION-CHECKLIST.md` batches B11-B13)
- Refactor `feature-dev`, `bugfix`, `team-*` skills against new patterns (note: `team-dev` is RENAMED to `develop` to match `/develop` slash command per Round 4 N2)
- Build NEW skills: `feature-design`, `env-analyze` (renamed from `env-analyzer` per N2), `ralph`, `eval`, `memory-init`, `memory-recall`, `learnings-write`, `plugin-doctor`, `context-load`, `subagent-spawn`, `ai-skills-init`, `plugin-skill-create`, plus 5 NEW workflow skills `refactor`/`migrate`/`spike`/`security-audit`/`docs-pack` (added Round 4 N1) — total 17 NEW skills
- New agents already added in Phase 2 B5 (no agents in Phase 3)
- **User-facing documentation:**
  - `plugin/README.md` — install + first-run + workflow tour
  - `plugin/docs/getting-started.md` — 30-min tutorial (B13.1)
  - `plugin/docs/workflows/<name>.md` × 10 — one per workflow slash command (B13.2-B13.11)
  - `plugin/docs/concepts/{memory,eval,ralf}.md` — concept overviews (B13.12-B13.14)
- v0.1.0-alpha tag at end of Phase 3

### Phase 4 — Implementation: Hardening + dogfooding
- Run plugin against three diverse target repos covering different stacks (e.g., Next.js + Python + Java)
- Capture findings in `04-MIGRATION-CHECKLIST.md`
- Tune skill descriptions based on activation data
- **Caching verification task (G6):** instrument 5 repeat-invocations of the same skill, compare `cached_tokens` across calls; document expected cache hit rate; file upstream issue if Claude Code does not auto-cache plugin contexts
- **G1/G2 attack-surface validation:** author 5 indirect-prompt-injection test fixtures (CLAUDE.md with hidden instructions, malicious env-analyze logs, poisoned learnings.md entries); confirm `<untrusted_content>` wrapper + tool-output-normalize prevent escape
- **Author `env-watch.sh` monitor script (Round 9 R9-1):** referenced by `plugin/monitors/monitors.json` since B1 but not previously tracked. Polls `docker compose ps` if compose file detected, surfaces health changes as notifications. No-op if `userConfig.env_watch_enabled: false`
- **Refactor 4 carried hook scripts to use `_lib.py`:** B2 left `_normalize_hook_input()` duplicated across all 4 scripts. After B8 ships `_lib.py`, refactor block-* and log-actions to import from it. Also wires `apply_pii_filter` into log-actions (closes Round 8 MEDIUM-3 PII gap)
- v0.2.0 release

### Phase 5 — Sunset legacy (when v0.2.0 stable)
- Move `.claude/`, `.codex/`, `.windsurf/`, `.agents/` to `archive/`
- Update root `README.md` to point to plugin install
- Optionally publish to `claude-plugins-official` marketplace
- **ARCHIVE skill sunset migration guide (Round 5 S3):** author `archive/MIGRATION.md` with one entry per legacy archived skill that has a plugin equivalent: `ai-skills` → `/plugin-doctor`, `asset-validation` → `/plugin-doctor`, `project-init` → `/ai-skills-init`, `ml-pipeline` → no replacement (revisit v0.3+ if generalisable), `product` → use `product-manager` agent directly. Document migration command for each.
- Optional: in v0.2 emit deprecation warnings on invocation of any of the 5 archived skill names (low priority since we control distribution, but defensive)

**"Stable" defined as:** Tier 3 eval suite passes (`/eval --all` ≥ pass threshold) on three different target repos covering distinct tech stacks, AND zero P0/P1 issues open against plugin v0.2.0 for 7 consecutive days, AND user-facing docs reviewed.

## 5a. Distribution & Install

**Install methods:**
```bash
# From git (primary distribution method for v0.1)
claude plugin install https://github.com/<owner>/ai-skills

# From local path (developer mode)
claude plugin install ./plugin

# From marketplace (v0.2+, after marketplace publish)
claude plugin install ai-skills/ai-skills
```

On install, Claude Code prompts the user for `userConfig` values (with defaults). User can re-run `/plugin configure ai-skills` later to change them.

**Validation after install:**
```bash
claude plugin validate ai-skills         # schema + structure check
/plugin-doctor                           # full self-test: skills load, hooks run, eval-judge calibration
/plugin-doctor --calibrate-judge         # baseline judge against known samples
/plugin-doctor --runs --last 5           # recent run summary
```

**Update / uninstall:**
```bash
claude plugin update ai-skills
claude plugin uninstall ai-skills
```

**First-run UX:** on first activation, the plugin prompts `Run /ai-skills-init in this repo? (creates .ai-skills-memory/, optional CLAUDE.md scaffolding)`. User can skip — plugin still works, just without persistent project memory.

---

## 6. Proposed Changes to Existing Components

### 6.1 Skills (refactor list)

| Skill | Change |
|---|---|
| `feature-dev` | Add automatic env-detect of design pack input, hand off to `team-dev` if multi-stack, add memory-write step |
| `team-dev` | Replace inline plan creation with mandatory `/plan` subagent call; add eval gate before declaring DONE; add RALF loop on test failures |
| `team-bugfix` | Extract env-analyzer logic into standalone `env-analyzer` skill; reference it instead |
| `team-protocols` | Add a section on RALF integration; add a section on memory write points |
| `bugfix` | Same env-analyzer extraction; add reproduction-test RALF gate |
| `plan` | Add output schema (Markdown sections + JSON sidecar for machine-readable plan) so `/develop` can consume reliably |
| `release` | Add memory-write step (release notes go to project memory); add changelog generation |
| `marketing` + `marketing-operations` | Merge into single `marketing`. Skill body reads `marketing/MARKETING.md` from target repo at runtime — never hardcodes brand, ICP, terminology, or domain examples (operations/data split per D2) |
| `ai-skills` + `asset-validation` | Replace with `plugin-doctor` skill that does both |

### 6.2 Agents (normalize)

See §2.2 for the authoritative list. Summary:
- Drop `permissionMode: plan` from 9 specific agents (named in §2.2); rely on existing `disallowedTools: Write, Edit`
- Add `max_output_tokens` per role type (G4)
- Add `effort` and `maxTurns` where missing
- Add 4 new agents: `security-engineer`, `feature-design-lead`, `eval-judge`, `memory-curator`
- Final agent count: 26

### 6.3 Rules (carry + add)

See §2.3 for the authoritative list. Summary:
- Carry all 8 existing rules
- Add 4 new rules: `subagent-isolation.md`, `memory-discipline.md`, `ralph-budget.md`, `untrusted-content-wrapping.md` (G1)
- Final rule count: 12

### 6.4 Hooks (carry + add)

See §2.4 for the authoritative list. Summary:
- Carry all 4 existing hooks unchanged
- Add 12 new hooks across 13 lifecycle events (Rounds 1+2+3+8 amendments combined; +1 for `pre-tool-use-committed-write` per R8 CRIT-1)
- Final hook count: 16

### 6.5 Removed from plugin

- Codex / Windsurf parity machinery (stays in legacy dirs)
- `install.sh` / `install.ps1` (replaced by `claude plugin install <git-url>`)
- `review/parity-matrix.md` (no longer relevant — single runtime)
- `PARITY.md` (deprecate when legacy archived)

### 6.6 Versioning and deprecation policy

Plugin uses **semver** (`MAJOR.MINOR.PATCH`):
- **PATCH** — bug fixes, doc tweaks, frontmatter normalization, no behavioural changes
- **MINOR** — new skills, new agents, new workflows, additive changes; existing skills MUST remain backwards-compatible
- **MAJOR** — breaking changes: skill renames, removed skills, signature changes, frontmatter schema breaks

**Deprecation flow** (anything removed in MAJOR):
1. MINOR N: skill keeps working but emits deprecation warning on activation, points to replacement
2. MAJOR N+1: skill removed; skill file deleted; deprecation message remains as a `removed-skills.md` reference

**CHANGELOG.md** at plugin root, Keep a Changelog format. Every PR that ships a behavioural change updates CHANGELOG.

**Skill-level versioning:** individual skills do NOT have separate version fields — plugin version covers them. Major refactor of a skill = MAJOR plugin bump if backwards-incompatible.

---

## 7. Open Questions — RESOLVED (2026-04-26)

### Q1. Repo separation — **DECISION: same repo**
Plugin lives at `ai-skills/plugin/`. Sibling-repo extraction is deferred until marketplace publish (v0.2.0+).

### Q2. Memory commit policy — **DECISION: gitignored, with opt-in `.committed/`**
- Default: `.ai-skills-memory/` is gitignored.
- Opt-in versioned content: `.ai-skills-memory/.committed/` is excluded from gitignore. Used for team-confirmed conventions, eval baselines worth tracking, durable architectural decisions.
- The `/ai-skills-init` workflow seeds the `.gitignore` rule and creates `.committed/README.md` explaining the contract.

### Q3. MCP servers — **DECISION: none in v0.1, planned for later**
- v0.1.0 ships without `.mcp.json`. Zero external dependencies.
- v0.3.0+ candidates (separate design doc when we get there):
  - `memory-server` — structured CRUD over `.ai-skills-memory/` with schema validation
  - `eval-server` — exposes eval-runner as a tool callable from any session
  - `git-context-server` — exposes `git log`, `git blame`, PR metadata as a typed tool

### Q4. Eval cost ceiling — **DECISION: token-based budgets (Max subscription model)**

Token-based makes more sense than dollar-based given the user's Max subscription. Budgets are configured in `plugin/eval/config.json`:

| Tier | Soft warn | Hard kill | Notes |
|---|---|---|---|
| Tier 1 (linters) | n/a | n/a | No LLM calls; pure Python |
| Tier 2 (smoke) | 50K tokens | 150K tokens | Per `/eval --tier smoke` run across all skills |
| Tier 3 (behavioral) per skill | 30K tokens | 100K tokens | Per skill, includes executor + judge + blind-comparator |
| Tier 3 full suite (`/eval --all`) | 500K tokens | 1.5M tokens | Sanity ceiling; warns user before run, requires confirm if soft exceeded mid-run |

`eval/runner.py` accumulates `usage.input_tokens + usage.output_tokens` across sub-agent calls and bails (exit 2) when the hard limit is hit. The eval-judge and blind-comparator use `model: haiku` by default to keep behavioral evals affordable.

### Q5. RALF default cap — **DECISION: 10 iter / 200K tokens / 2 hours (overridable)**

Defaults in `plugin/rules/ralph-budget.md` and `plugin/skills/ralph/SKILL.md`:

| Limit | Default | Override flag | Per-workflow override |
|---|---|---|---|
| Max iterations | 10 | `--max-iterations N` | `/feature-design`: 5 (rubric converges fast); `/develop` test loop: 8; `/bugfix` reproduction loop: 6 |
| Token budget | 200K | `--token-budget N` | Inherits unless overridden |
| Wall time | 2 hours | `--time-cap MINUTES` | Inherits unless overridden |
| Mandatory kill-criterion | required | `--kill-on PATTERN` | Each workflow defines a domain-appropriate signal (e.g., `same-error-3-times`, `oracle-passes`, `rubric-stalls`) |

The Stop hook tracks all four; the first one to trip wins. Every RALF run writes `.ai-skills-memory/ralph/<run-id>/budget.json` so the user can audit cost after the fact.

### Q6. Brand-voice domain — **DECISION: out of scope for v0.1**

Brand-voice skills are too company-specific to generalize cleanly (they encode a specific sales motion, terminology, and persona model). They will not be migrated. They remain available as the existing standalone `brand-voice:*` plugin (already separately installed in user environment).

If a generic version is needed later (e.g., `voice-extraction` skill that derives a brand profile from any user-provided corpus without baking in a specific company's voice), it ships as a separate optional plugin in v0.4.0+ — not bundled with `ai-skills`.

---

## 7a. Decisions Locked Summary

| ID | Decision |
|---|---|
| Q1 | Plugin lives at `ai-skills/plugin/` in same repo |
| Q2 | `.ai-skills-memory/` gitignored; opt-in `.committed/` sub-dir versioned |
| Q3 | No MCP in v0.1.0; design separately for v0.3.0+ |
| Q4 | Eval budgets in tokens — see table above; Haiku for judge/comparator |
| Q5 | RALF: 10 iter / 200K tokens / 2 h, overridable per workflow, kill-criterion mandatory |
| Q6 | Brand-voice skills NOT in plugin; remain as separate standalone plugin |

### 7b. Counts after Phase 1 review

| Component | Count | Notes |
|---|---|---|
**Skills (authoritative list in §2.1):**

| | Count | Detail |
|---|---|---|
| KEEP as-is | 20 | (see §2.1 list) |
| REFACTOR | 13 | one renamed: team-dev → develop |
| MERGE input → output | 4 → 2 | marketing+ops, blog-post+content-creation |
| ARCHIVE | 5 | ai-skills, asset-validation, ml-pipeline, product, project-init |
| NEW | 17 | 8 workflow skills + 9 companion skills |
| **Existing handled** | **42** | matches verified inventory |
| **Skills in plugin v0.1** | **52** | 20 + 13 + 2 + 17 |
| User-invocable (slash commands) | 19 | 10 workflows + 9 companions |
| Knowledge / auxiliary | 33 | activated on context match |

**Agents (authoritative list in §2.2):**

| | Count | Detail |
|---|---|---|
| Existing normalized | 22 | 9 drop `permissionMode`; all add `effort`, `maxTurns`, `max_output_tokens` (G4) |
| New | 4 | security-engineer, feature-design-lead, eval-judge, memory-curator |
| **Agents in plugin v0.1** | **26** | |

**Rules (authoritative list in §2.3):**

| | Count | Detail |
|---|---|---|
| Existing | 8 | all carry over |
| New | 4 | subagent-isolation, memory-discipline, ralph-budget, untrusted-content-wrapping (G1) |
| **Rules in plugin v0.1** | **12** | |

**Hooks (authoritative list in §2.4):**

| | Count | Detail |
|---|---|---|
| Existing | 4 | block-dangerous-commands, block-secrets-in-code, block-sensitive-files, log-actions |
| New (Round 1) | 3 | session-start-context, ralph-stop, subagent-stop-learnings (opt-in) |
| New (Round 2 expansion) | 6 | instructions-loaded-augment, pre-compact-memory-flush, session-end-finalize, subagent-start-budget, task-event-log, tool-failure-log |
| New (Round 3 G1+G2) | 2 | tool-output-wrap, tool-output-normalize |
| New (Round 8 CRIT-1) | 1 | pre-tool-use-committed-write (was missing — referenced by memory-discipline rule + 03-MEMORY-ARCHITECTURE.md §8 + B5 memory-curator agent) |
| **Hooks in plugin v0.1** | **16** | across 13 lifecycle events |

**Other plugin assets:**

| Asset | Count | Source |
|---|---|---|
| Output styles | 2 | concise-pr, design-pack (§1.8) |
| Monitors | 1 | env-watch.sh (opt-in via userConfig) (§1.8) |
| JSON schemas | 2 | spawn-payload, return-contract (G7) |
| Eval rubrics (per-workflow + cross-cutting) | 17 | 10 per-workflow + 7 cross-cutting (humanizer-compliance, code-quality, security-soundness, geo-readiness, subagent-handoff-quality, memory-write-discipline, faithfulness G5) |
| Examples directory | convention only | content authored Phase 3 (G9) |
| `userConfig` knobs | 11 | (§3.2 plugin.json: session_token soft/hard, ralph per-workflow defaults × 3, ralph session-aggregate × 3 added Round 6 HIGH-3, opt-in toggles × 3) |
| `dependencies` | 0 | fully standalone in v0.1 |

---

## 8. What Phase 1 Delivers

Phase 1 deliverable set (all complete as of 2026-04-26):

1. **`00-PHASE-1-PLAN.md`** (this doc) — locked decisions, architecture, asset disposition, plugin design, migration plan, counts.
2. **`00a-CRITIQUE-AND-CORRECTIONS.md`** — review trail across three rounds (Round 1 self-review patches P1-P25; Round 2 friendly4ai independence F1-F4 + best-practices reverse-check H1-H9 + missing concepts M1-M10; Round 3 user decisions Q1-Q4 + context-engineering gaps G1-G10).
3. **`01-WORKFLOW-SPECS.md`** — full per-workflow spec for `/feature-design`, `/develop`, `/bugfix`, `/env-analyze`, `/refactor`, `/migrate`, `/spike`, `/security-audit`, `/docs-pack`, `/ai-skills-init`. Each spec contains: input schema, output schema, agent roster (with model + effort + tools), pipeline diagram, eval rubric pointer, RALF wiring (oracle + kill-on + caps), memory writes (which layer, what shape), failure modes, observability events emitted. Also: 9 companion skills, common patterns, structured spawn payload + return contract schemas (G7), few-shot example library convention (G9).
4. **`02-EVAL-FRAMEWORK.md`** — eval case JSON schema (full), judge rubric library (10 per-workflow + 7 cross-cutting), baseline policy, release gate definition, blind-comparator implementation (verified mechanism after Q3), judge calibration procedure, token budget enforcement code sketch.
5. **`03-MEMORY-ARCHITECTURE.md`** — memory schemas per layer (L0-L5), write rules per skill, conflict resolution algorithm (L0 vs L4, L4 vs L5), retention/expiry policy, PII filter mechanics + extensible patterns, `.committed/` allowlist enforcement, tool output normalization (G2), context health metrics (G8) in observability schema.
6. **`05-CONTEXT-ENGINEERING-GAP-ANALYSIS.md`** — section-by-section audit against `context_engineering_guide.md`; G1-G10 gaps identified, prioritized, and (per Round 3) all applied immediately rather than deferred.

**Pending for Phase 2 (NOT a Phase 1 deliverable):**
- `04-MIGRATION-CHECKLIST.md` — dry-run migration script for each existing asset; before/after frontmatter diff for the 9 agents losing `permissionMode`; merge plan for the 4 collapsing skills (marketing+ops, blog-post+content); archive justification for the 5 skipped skills. To be authored at the start of Phase 2 once `plugin/` skeleton is being created.

---

## 8a. Plugin Features Out of Scope for v0.1 (deliberately, with rationale)

| Feature | Why deferred |
|---|---|
| `themes/` (color themes) | Visual personalization, not SDLC-related |
| `channels/` (Telegram/Slack injection) | No external messaging surface in v0.1 |
| `lspServers/` | LSP is a different concern from agent orchestration; users add LSP plugins separately |
| MCP servers (`.mcp.json`) | v0.3.0+ candidates documented in Q3; v0.1 stays zero-dependency |
| `http` hook type | No observability backend in v0.1; structured logs in `runs/*.jsonl` are sufficient |
| `mcp_tool` hook type | Requires MCP, deferred with #4 |
| Hook events not used: `UserPromptSubmit`, `UserPromptExpansion`, `PostToolBatch`, `PermissionRequest`, `PermissionDenied`, `TeammateIdle`, `WorktreeRemove`, `ConfigChange`, `CwdChanged`, `Elicitation*` | Not needed for v0.1 capabilities; documented for transparency |
| Marketing/content scope (geo-writer, seo-review, marketing, social-media-manager, content-creation, blog-post merged variants, humanizer) | Carried forward as KEEP for backward compatibility, but **clearly extended-scope** — these are content/marketing skills not core SDLC. May split to a sibling marketplace plugin in v0.3+. They are project-agnostic (no hard friendly4ai or any specific company dependency); brand context comes from target repo's `marketing/MARKETING.md` at runtime |
| `outputStyles` beyond two named styles | Two styles cover the highest-volume workflows; more on demand |
| Plugin marketplace publish | v0.2.0+ after dogfooding |

## 9. Sources

- [Plugins reference — Claude Code Docs](https://code.claude.com/docs/en/plugins-reference)
- [Plugin marketplaces — Claude Code Docs](https://code.claude.com/docs/en/plugin-marketplaces)
- [Orchestrate teams of Claude Code sessions](https://code.claude.com/docs/en/agent-teams)
- [Skill authoring best practices — Claude API Docs](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
- [Extend Claude with skills — Claude Code Docs](https://code.claude.com/docs/en/skills)
- [Equipping agents for the real world with Agent Skills (Anthropic engineering)](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)
- [The Complete Guide to Building Skills for Claude (Anthropic resource)](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf)
- [Memory tool — Claude API Docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool)
- [Effective context engineering for AI agents (Anthropic engineering)](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [Effective harnesses for long-running agents (Anthropic engineering)](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
- [Demystifying evals for AI agents (Anthropic engineering)](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
- [Anthropic Drops Claude Code Skills 2.0 with Evals + A/B Testing](https://www.geeky-gadgets.com/anthropic-skill-creator/)
- [Hooks reference — Claude Code Docs](https://code.claude.com/docs/en/hooks)
- [Ralph Loop — Claude Plugin (Anthropic)](https://claude.com/plugins/ralph-loop)
- [From ReAct to Ralph Loop — Alibaba Cloud Community](https://www.alibabacloud.com/blog/from-react-to-ralph-loop-a-continuous-iteration-paradigm-for-ai-agents_602799)
- [Claude Code Plugin Marketplaces](https://claude.yourdocs.dev/docs/claude-code/plugin-marketplaces)
- [7 Rules for Creating an Effective Claude Code Skill (UX Planet, 2026)](https://uxplanet.org/7-rules-for-creating-an-effective-claude-code-skill-2d81f61fc7cd)
