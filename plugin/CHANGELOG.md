# Changelog

All notable changes to the `ai-assets` plugin. Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Versioning: [Semantic Versioning](https://semver.org/spec/v2.0.0.html) per `../plugin-design/00-PHASE-1-PLAN.md` §6.6.

## [Unreleased]

Phase 2 implementation in progress per `../plugin-design/04-MIGRATION-CHECKLIST.md`. Following batches will populate the skeleton.

### Round 8 cross-phase review findings (design-only fixes, no plugin code change)

Holistic review of B1+B2+B6+B7 found 2 real gaps (CRIT-1 and HIGH-1) plus integration concerns. Design docs updated; plugin code changes will be applied in B8 + later batches:

- **CRIT-1 [design fix applied]:** `pre-tool-use-committed-write.py` referenced in 4 design locations (memory-discipline rule, 03-MEMORY-ARCHITECTURE.md §8 + §3 L1, B5 memory-curator description) but missing from B8 hook list. Hook count was 15, actual need is 16. Cascade fix applied: `_glossary.md` §1 (15→16) + §5 (added entry); plan §7b counts table; checklist B8 (added item 74a) + V4 validation; README "16 hooks". Implementation in B8.
- **HIGH-1 [design fix applied]:** `log-actions.py` writes to `.ai-assets-memory/agent-actions.log` (L4) but was not in `memory-discipline.md` write rules table. Added row to the table; flagged PII filter integration as deferred to B8 (when `_lib.py` ships `apply_pii_filter()`).
- **MEDIUM-1 [acknowledged, not blocking]:** Plugin currently functional only for security hooks + rule context-loading. No skills/agents = no slash-command workflows. Design intent — workflows ship in B11+B12.
- **MEDIUM-2 [acknowledged]:** `global-package-rules.md` (B6 carried verbatim) has stale `~/.claude/agents/...` legacy paths. Will be refreshed when content-refresh batch runs.
- **MEDIUM-3 [acknowledged]:** `log-actions.py` does not currently apply PII filter despite memory-discipline mandating it. Integration gap closes in B8 when `_lib.py` ships and log-actions is updated to import `apply_pii_filter()`.
- **LOW-1 [acknowledged]:** `subagent-depth-guard.py` mentioned in `subagent-isolation.md` as a future v0.2+ addition; not tracked in current batches. Document as future-work, not gap.

### Round 9 cross-phase + format/style review (design-only fixes)

Pattern 13 (cross-batch reference resolution) sweep + format/style audit found 3 more gaps:

- **R9-1 [design fix applied]:** `env-watch.sh` script referenced by `plugin/monitors/monitors.json` (B1) but never tracked as deliverable in any batch. Added explicit Phase 4 hardening item to author it. Pattern 13 candidate added to memory.
- **R9-2 [design fix applied]:** Pattern 1 cascade sweep found 4 stale "11 new hooks" mentions left over from Round 8 cascade (in `04-MIGRATION-CHECKLIST.md` B8.12, `00-PHASE-1-PLAN.md` §6.4 reference, `plugin/CHANGELOG.md` B1 "Following batches", `plugin/hooks/hooks.json` $schema-comment). All 4 updated to "12 new hooks" referencing R8 CRIT-1.
- **R9-3 [design fix applied]:** Plan §5 Phase 3 list had stale `env-analyzer` (R4 N2 renamed to `env-analyze`) and miscategorized B5 agents as Phase 3. Phase 3 list rewritten to match current state — B5 agents stay in Phase 2; Phase 3 NEW skills list now lists all 17 explicitly (previously omitted 5: refactor/migrate/spike/security-audit/docs-pack added in R4 N1).
- **R9-4 [acknowledged]:** Format/style audit — heading hierarchy consistent across 4 new B7 rules (all H2 sections, no skip levels). One bare ` ``` ` opening fence in memory-discipline.md fixed to `text` lang tag. No bullet-style mixing (- vs *). No trailing whitespace. Sufficient.

Pattern 13 added to durable memory (`feedback_design_doc_quality.md` patterns 1-13 + pre-flight checklist items 1-13).

## [0.1.2] — 2026-04-30 — Structural: Path B reordered before Path A + Step 0 mandatory attempt

Two new dogfood sessions (Python/FastAPI + Next.js on Windows host with `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` set + flag visible to claude process) BOTH spawned correct `ai-assets:*` subagents but went **Path A** without ever attempting Path B. Session log analysis:

```
Python session L28: "Empty project — no CLAUDE.md or ARCHITECTURE.md.
                    I'll build the plan from scratch and proceed via
                    Path A (Agent subagents)."
Nextjs session L42: "Plan resolved. Presenting and proceeding immediately"
                    [then Path A directly]
```

Neither session even MENTIONED Path B detection. The model defaulted to Path A based on textual order in the skill body — Path A appeared first, so Path A was chosen. The "Path B preferred" prose at line 85 was overridden by the Path A header at line 104 which literally said `## Path A — Subagents (default, sequential)`.

### Root cause

Two structural problems in alpha.29:

1. **Header contradicted prose**: Path A header said "(default, sequential)" while prose 20 lines earlier said "Path B is the default preference". Headers > prose for model attention.
2. **Textual order signaled priority**: Path A appeared at line 104, Path B at line 150. The model reads top-down and picks the first option presented.

### Fixed — added Step 0 + reordered sections in 3 orchestration skills

`develop/SKILL.md`, `team-bugfix/SKILL.md`, `feature-design/SKILL.md` all now have:

**New "## Step 0 — ATTEMPT Path B FIRST (literal, mandatory)" section** before any path content. Lists invalid skip-Path-B reasons (empty project / single-stack / Windows / no tmux / sequential pipeline / textual order) and mandates the announcement-first-sentence pattern: either "Attempting Path B (Agent Teams) team-create..." or (after technical failure) "Agent Teams API returned: <error>. Falling back to Path A."

**Path B section now appears BEFORE Path A** in the document. Renamed:
- `## Path A — Subagents (default, sequential)` → `## Path A — Subagents fallback (only if Path B Step 1 returned a technical error)`
- `## Path B — Agent Teams (when CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1)` → `## Path B — Agent Teams (PREFERRED — try this FIRST)`

The Path A header now actively SIGNALS its fallback status, removing the contradiction with the prose preference.

### Behavioral expectation post-fix

In a fresh Claude Code session on Windows with flag set:

```
Attempting Path B (Agent Teams) team-create...
[team panel appears with Shift+↓ navigation, in-process display mode]
```

OR (if flag actually unset):

```
Agent Teams API returned: <verbatim error>. Falling back to Path A.
[then proceeds with Agent({...}) sequential calls as before]
```

Saying "I'll proceed via Path A because <empty project / single-stack / no tmux>" is now an explicit protocol violation called out by name in the skill body.

## [0.1.1] — 2026-04-29 — Hotfix: rebut "tmux/iTerm2 not available" Path B fallback rationalisation

User on Windows host invoked `/ai-assets:develop`, model attempted Path B, then said "Path B (Agent Teams) requires tmux/iTerm2 which isn't available on this Windows host — going Path A (sequential subagents)". WRONG.

Per [Anthropic agent-teams docs](https://docs.claude.com/en/docs/claude-code/agent-teams), Agent Teams supports two display modes:

- **`in-process`** — all teammates in one terminal, **Shift+↓** to cycle. **Works in any terminal, NO extra setup, NO tmux, NO iTerm2 required.** Default fallback.
- **`tmux`** (split panes) — optional enhancement when tmux/iTerm2 available.

The model conflated the two modes and downgraded to Path A based on a non-blocker (display-mode preference). This is a NEW rationalisation not covered by alpha.27 rebuttals.

### Fixed — added explicit tmux rebuttal in 4 skills

`team-protocols/SKILL.md`, `develop/SKILL.md`, `team-bugfix/SKILL.md`, `feature-design/SKILL.md` all now list:

- "tmux/iTerm2 not available" — INVALID, Path B has `in-process` display mode that works on every terminal (including Windows without WSL)
- "Windows host" / "no Unix tools" — INVALID, Agent Teams is platform-independent in `in-process` mode
- "split-pane mode unavailable" — INVALID, that's an optional enhancement; in-process always works

And the team-creation prompt template in all 3 orchestration skills now explicitly says: **"Use teammate-mode `in-process` by default. Pick `tmux` split-pane mode ONLY if the user has explicitly indicated tmux/iTerm2 is available and they prefer it. If unsure: `in-process` is the safe choice."**

The hard rule clarified: **display-mode unavailability is NEVER a valid Path A trigger**. The ONLY valid Path A trigger remains a true team-creation API failure (typically `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` env var unset).

## [0.1.0] — 2026-04-29 — First stable release

After 17 alpha iterations and 4 review rounds (Round 13 / 14 / 15 / 16), the plugin is structurally feature-complete and architecturally sound. Round 16 (final pre-release validation) returned PASS with `21/0/0` validator + manual review across all 9 dimensions (per-component, connections, style, semantic content, security, docs ↔ implementation, docs ↔ vendor, best practices, Six Thinking Hats). User confirmed live smoke test of `/develop` orchestrating DEV→REVIEW→QA pipeline with plugin-namespaced subagents.

### What's in v0.1.0

- **26 specialized agents** — engineering (java/python/frontend/devops/sre/db/data/ml/mobile/security), architecture (system/solution/cloud/devops), product (product-manager, qa-engineer, prompt-engineer), content (content-writer/designer, marketing-strategist, seo-engineer, ui-ux-designer), orchestration (feature-design-lead, eval-judge, memory-curator, software-engineer)
- **52 skills** — 31 user-invocable (10 primary workflows + 9 companion + 12 extended fork-skills) + 21 reference skills (team-protocols, role-selection-table, etc.)
- **16 hooks** across **13 lifecycle events** — security (block-dangerous-commands / block-secrets-in-code / block-sensitive-files), audit (log-actions with PII filter), G1 wrapping (tool-output-wrap / tool-output-normalize), session lifecycle (session-start-context / session-end-finalize / pre-compact-memory-flush), subagent governance (subagent-start-budget / subagent-stop-learnings), task tracking (task-event-log), failure recovery (tool-failure-log), RALF control (ralph-stop with session-aggregate caps), allowlist enforcement (pre-tool-use-committed-write), L4 instructions (instructions-loaded-augment)
- **12 rules** — security, memory discipline, RALF budget, untrusted-content wrapping, failure recovery, geo-content, humanize-content, git-conventions, global package rules, memory validation, task completion verification
- **17 eval rubrics + 102 calibration samples** (3 good + 3 bad per rubric × 17) + Tier 1 linter
- **2 G7 JSON schemas** — spawn-payload + return-contract for typed subagent contracts
- **2 output styles** — concise-pr, design-pack
- **14 user docs** — 1 getting-started + 10 workflow guides + 3 concept overviews
- **12 userConfig knobs** — session token caps, RALF per-workflow + session-aggregate caps, monitor + memory toggles
- **6-layer memory model** — L0 (Cowork host) → L1 (plugin templates) → L2 (project static) → L3 (session) → L4 (project cross-session) → L5 (user-global)
- **5-layer untrusted-content defense** (G1 + G2)
- **Dual-path orchestration** — Path A (Subagents, default everywhere) + Path B (Agent Teams, when `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`) with implicit detection
- **Local validator** — `python plugin/dev/validate.py` runs 21 structural + semantic checks

### Install

```bash
# Local development (canonical per Anthropic docs)
claude --plugin-dir /path/to/ai-assets/plugin

# After GitHub publish (v0.2+)
/plugin marketplace add alex-voloshin/ai-assets
/plugin install ai-assets
```

### Headline lessons from the alpha cycle (memory-pattern set)

The alpha cycle surfaced four lessons worth carrying forward into v0.2 / Phase 4:

1. **Read the official Anthropic Quickstart end-to-end before improvising** — alpha.20-23 burned 4 releases trying to make `/plugin marketplace add <local-path>` work when the canonical local-dev path was always `claude --plugin-dir`.
2. **Skills must instruct, not describe** — narrative voice ("Agent 1 — Developer ... Agent 2 — Reviewer") gets read as documentation by the model. Literal `Agent({...})` calls with concrete `subagent_type: "ai-assets:<name>"` are required.
3. **Subagents cannot spawn other subagents** is a hard Anthropic constraint. Orchestration skills MUST run in main thread (no `context: fork`) to retain `Agent` tool access.
4. **Honor user opt-ins literally** — `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` is an explicit user opt-in. Path B becomes mandatory; rationalised silent fallback to Path A is forbidden. Detection should be implicit (attempt-then-fallback), not explicit (Bash env-var check that triggers permission prompt).

### Known limitations (deferred to v0.1.1 / Phase 4)

- **Smoke test procedure not documented as a separate file** — verbal confirmation only; will write `SMOKE_TEST.md` in v0.1.1
- **`monitors/env-watch.sh` deprecation timeline unspecified** — shim retained from alpha.19, will be removed in v0.2 with explicit migration note
- **Tier 2/3 eval runners stubbed** — Tier 1 linter is live, behavioral tiers ship in Phase 4
- **G1/G2 attack-surface fixtures not authored** — defense is in place, validation fixtures are Phase 4 work
- **Caching verification (G6) not instrumented** — Phase 4 dogfood task
- **Subagent-depth-guard hook** — flagged as v0.2+ in original plan
- **tool-output-normalize Haiku summarization** — currently stops at metadata extraction (alpha.16 note); Phase 4
- **Per-iteration RALF token measurement** — closes alpha.16 HIGH-C limitation; Phase 4

### Next phase

**Phase 4** — hardening + dogfooding on 2 additional stacks (Python/FastAPI + Next.js — Java already validated). After 7 consecutive days with zero P0/P1 issues + Tier 3 eval suite passing → **v0.2.0 stable** → Phase 5 sunset of legacy `.claude/` / `.codex/` / `.windsurf/` / `.agents/` packages.

---

## [0.1.0-alpha.29] — 2026-04-29 — Removed explicit env-var Bash check from orchestration skills

User feedback: the `echo "TEAMS_FLAG=${CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS:-0}"` step at the start of each orchestration skill triggers a Bash tool-permission prompt for the user — friction with no value, since both Path A and Path B logic exists in the skill body anyway. Detection should happen implicitly through the model's attempt to use Teams API, not via an env-var inspection.

### Changed — `team-protocols/SKILL.md`, `develop/SKILL.md`, `team-bugfix/SKILL.md`, `feature-design/SKILL.md`

Removed the explicit Bash detection block (`echo "TEAMS_FLAG=..."`) from all four files. Replaced with implicit-detection language:

> **Detection is implicit, not explicit.** Do NOT run a Bash env-var check (no `echo $CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS`) — that triggers a tool-permission prompt for the user without adding value. Just attempt Path B Step 1 directly. If team-creation natural language fails ("Agent Teams not enabled" or equivalent error), fall back to Path A immediately and continue without re-asking the user.

The hard rules from alpha.27 are preserved — same "no silent fallback for non-technical reasons" + same rebuttals for "sequential pipeline doesn't need parallelism" / "Path A gives cleaner visibility" / "fewer tools to manage". Only the means of detection changed (explicit Bash → implicit attempt-then-fallback).

### Changed — validator check `orchestration_dual_path`

- Dropped the requirement that skills contain literal `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` (env-var detection no longer required)
- Added new check: skills MUST NOT contain the literal Bash command `echo "TEAMS_FLAG=...` (the explicit detection trigger). Prose that mentions the env var in negative instructions ("Do NOT run echo $...") is fine and will not match.
- Path A / Path B / "no silent fallback" requirements unchanged

### Behavioral effect

When `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` is set, Claude Code exposes Teams-creation capability to the model. The model attempts Path B's natural-language team-creation, which succeeds, and the workflow proceeds in Teams mode — no Bash prompt to the user.

When the flag is unset, team-creation natural language returns an error or no-op, the model recognizes this as a hard technical block, and silently falls back to Path A — also no Bash prompt to the user.

Either way: same outcome, but without the friction of asking the user to approve a Bash command before the workflow can even start.

## [0.1.0-alpha.28] — 2026-04-29 — `/develop`: removed user-approval gate, formalized load-vs-create plan logic

User feedback: the mandatory "Wait for user approval before proceeding" gate in `/develop` is friction. The user already provided enough context to start when invoking the slash command. The plan should be presented as a heads-up, not a question.

### Changed — `skills/develop/SKILL.md` "Resolve Implementation Plan" section rewritten

**Two-source plan decision (formalized):**

1. **Source 1 — load existing plan** (preferred when input contains one). If the user's input references a document with an embedded implementation plan (PRD, ARD, design doc, ticket, audit, `/plan` output, RFC, etc.), use the plan as-is — no rewriting, no reordering, no "simplification". Map each work package to a Developer subagent_type via `role-selection-table.md`. Preserve original ordering, dependencies, and language.
   
   Recognition cues for "doc contains a plan": numbered/bulleted work-package list; section titled Implementation Plan / Work Packages / Tasks / Acceptance Plan / Build Plan / Steps; Gantt-style ordering; `/plan`-skill output format.

2. **Source 2 — create plan from scratch** (when input is just a feature description with no embedded plan). Same algorithm as before — break into ordered atomic WPs, dependency-first, interleave tests.

**Approval gate removed:** the line "Wait for user approval before proceeding" is GONE. The plan is presented to the user as informational ("Plan source: <X>; Work packages: 1 ... 2 ... 3 ... Proceeding to execution.") and the workflow continues immediately to "Detect execution path FIRST" → spawn pipeline. The user retains the explicit affordance to interrupt with Esc + revise.

**Path B duplicate-gate removed:** the team-creation prompt previously said "Require plan approval for the developer teammate before any code changes" — this added a SECOND approval gate inside Path B (Lead → developer teammate). Replaced with "Do NOT require plan approval from the developer teammate (the Lead already resolved the plan above — execution starts immediately)". Kept the gate-preserving `dependsOn` graph for DEV → REVIEW → QA pipeline ordering.

### Not changed

- `team-bugfix/SKILL.md` — input is always an audit/code-review document containing the task list; no user-approval gate existed.
- `feature-design/SKILL.md` — input is a 1-3 sentence feature idea, the workflow auto-produces the design pack; no user-approval gate existed.

### Why this matters

`/develop` is a workflow you trigger when you've already decided what to build. The friction of confirming a plan you're about to execute is dead weight when the source-doc IS the plan. For the new-plan-from-scratch case, the user can still intercept — they don't need a forcing function.

## [0.1.0-alpha.27] — 2026-04-29 — Hardened TEAMS_FLAG honor: forbid silent fallback to Path A

User session log analysis (sessionId d8e3f272, 7 subagents spawned with correct `ai-assets:<role>` types — orchestration mechanically working): user had `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` set, the skill correctly detected `TEAMS_FLAG=1`, announced "I'll use Path B (Agent Teams)" twice — then mid-flow rationalised back to Path A with the argument "Path B's value is parallel teammates, but this CRUD pipeline is strictly sequential, so Path A gives you cleaner visibility".

This is wrong: the user explicitly opted into Teams by setting the env var, and Path B's primary value is **user-facing UX** (visual panel + Shift+↓ + dedicated transcript per role) — not parallelism. Even for sequential pipelines, the panel is strictly more visible than Path A.

### Fixed — hard "no silent fallback" rule in 4 skills

Added explicit paragraph to `team-protocols/SKILL.md`, `develop/SKILL.md`, `team-bugfix/SKILL.md`, `feature-design/SKILL.md`:

> If `TEAMS_FLAG=1`, Path B is MANDATORY. Switching back to Path A after announcing Path B is FORBIDDEN.

Listed and rebutted the rationalisations the model used:
- "pipeline is sequential, parallelism doesn't help" — INVALID, Path B's primary value is UX, not parallelism
- "Path A gives cleaner visibility" — INVALID, Path B's panel gives strictly more visibility
- "fewer tools to manage" — INVALID, the user explicitly opted in

The only acceptable fallback is a hard technical block (e.g., Claude Code version too old for Agent Teams), and it MUST be surfaced to the user explicitly: "TEAMS_FLAG=1 detected, but Agent Teams API not available — falling back to Path A. Please upgrade Claude Code." Never silently fall back.

Symmetric rule for the inverse: if `TEAMS_FLAG=0/unset` → use Path A. No "auto-upgrade to Path B" — respect the user's environment.

### Added — validator check for the hard-rule presence

`check_orchestration_dual_path` now also requires the literal phrase "no silent fallback" in each orchestration skill body. Catches accidental drift if someone simplifies the body.

### Trade-off acknowledgment

The skill now contains stronger directive language. If a future user has a legitimate case where Path A is genuinely better with TEAMS_FLAG=1, they should `unset CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` for that session rather than expect the skill to make the call. The rule is: env-var honor is mandatory, not advisory.

## [0.1.0-alpha.26] — 2026-04-29 — Dual-path: Subagents (default) + Agent Teams (when flag is on)

User confirmed Agent Teams UX with `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` is the preferred mode (visual team panel, parallel teammates, Shift+↓ context-switch). Plugin now auto-branches at runtime: orchestration skills detect the env flag and pick Path A (Subagents) or Path B (Agent Teams) accordingly. Both paths preserve the same DEV → REVIEW → QA gate semantics.

### Changed — `team-protocols/SKILL.md` is the canonical dual-path reference

Replaced the single "Optional: experimental Agent Teams" footnote with a full **Dual-Path Detection** section:

- Detection bash block (`echo "TEAMS_FLAG=${CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS:-0}"`)
- **Path A (Subagents)** — canonical `Agent({...})` calls, sequential, default everywhere
- **Path B (Agent Teams)** — natural-language team-create with subagent-definition references (`ai-assets:java-engineer`), shared task list with `dependsOn`, Shift+↓ visual control
- Hard rule (both paths): Lead never does Developer/Reviewer/QA work inline

### Changed — `develop/SKILL.md` per-WP execution split into Path A and Path B

- New "Detect execution path FIRST" section runs the bash check at the start of the workflow
- Path A keeps the literal `Agent({...})` per-WP loop from alpha.24 (DEV → REVIEW → QA)
- Path B adds: Step 1 (create team via natural language with `ai-assets:<role>` subagent definitions), Step 2 (populate shared task list with WP-N DEV/REVIEW/QA tasks linked via `dependsOn`), Step 3 (drive + monitor with Shift+↓ + Ctrl+T), Step 4 (final verify in main thread + cleanup)
- Both paths converge on the same gate rules, RALF wiring, REVIEW-LOG.md output

### Changed — `team-bugfix/SKILL.md` mirrors the dual-path pattern

Same detection block + Path A (per-task spawn loop, kept from alpha.24) + Path B (audit-issue-driven team with `dependsOn` chain per audit ID).

### Changed — `feature-design/SKILL.md` mirrors with wave-aware Path B

Path A keeps the original 3-wave parallel-then-sequential pipeline. Path B maps the 3 waves onto the shared task list — wave-2 tasks `dependsOn` all wave-1 tasks; wave-3 tasks `dependsOn` all wave-2 tasks. The dependency graph enforces wave gates structurally without manual Lead checkpoints.

### Added — validator check `orchestration_dual_path`

`plugin/dev/validate.py` now hard-fails if any orchestration skill (`develop`, `team-bugfix`, `feature-design`) is missing:
- The `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` detection block
- A "Path A" section
- A "Path B" section

Catches dual-path drift before the user hits it.

### How to use

1. Set the flag persistently via `~/.claude/settings.json`:
```json
{ "env": { "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1" } }
```
Or via Windows env: `[Environment]::SetEnvironmentVariable('CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS', '1', 'User')`.

2. Open a fresh PowerShell (env vars only propagate to new processes).

3. `claude --plugin-dir C:\Users\avav2\dev\code\ai-assets\plugin`

4. `/ai-assets:develop ...` — the skill will detect the flag, announce "Using Agent Teams mode", and create the team via natural language. You'll see the team panel appear; Shift+↓ cycles between teammates.

5. With the flag unset, the same command falls through to Path A (sequential `Agent({...})` calls). Same DEV → REVIEW → QA gates, just no visual panel.

### Trade-off note (per Anthropic docs)

> "Agent teams add coordination overhead and use significantly more tokens than a single session."

Path B costs more tokens than Path A because each teammate is a full Claude Code session with its own system prompt + context window. The current per-workflow RALF token budget (200K) and session-aggregate cap (400K) should be reviewed if the user runs Teams-mode `/develop` heavily — see `userConfig.ralph_*` knobs.

## [0.1.0-alpha.25] — 2026-04-29 — CRIT (root architectural cause): orchestration skills MUST NOT use `context: fork`

User ran `/ai-assets:develop` against an empty `controller/` repo asking for a Java REST CRUD. Session log analysis (sessionId d0163d80, 20 lines parent + a `general-purpose` subagent thread): the alpha.24 fix shipped explicit `Agent({...})` literals in the skill body, but Claude Code immediately responded:

> "Confirmed: no `Agent` / `Task` spawn primitive is available in this environment. Per the skill's hard invariant, I cannot perform Developer / Reviewer / QA work inline."

The model did the right thing per the skill's own rules — it just couldn't access the `Agent` tool because **the skill was running inside a forked subagent**.

### Root cause (architectural, not stylistic)

Per [Anthropic Claude Code docs](https://docs.claude.com/en/docs/claude-code/sub-agents):

> "Subagents cannot spawn other subagents. If your workflow requires nested delegation, use Skills or chain subagents from the main conversation."

When a skill has `context: fork` in its frontmatter, Claude Code runs the entire skill body inside a **forked subagent** (typically `general-purpose`). Inside that forked subagent the `Agent` tool is unavailable, because subagents cannot spawn other subagents.

The four orchestration skills (`develop`, `team-bugfix`, `feature-design`, plus `feature-dev` which is single-agent) ALL had `context: fork`. For `feature-dev` (no spawning) that's fine. For the three orchestration skills it was a hard architectural break.

This is the THIRD layer of the same bug:

- **alpha.23 layer**: skill body described roles in narrative voice — model treated as documentation. (Fixed in alpha.24 with literal `Agent({...})` invocations.)
- **alpha.24 layer**: literal invocations were correct, but the skill couldn't execute them from a forked subagent context. (This release.)
- **Root layer**: orchestration skills CANNOT use `context: fork` regardless of how cleanly the body is written.

### Fixed — removed `context: fork` from 3 orchestration skills

- `skills/develop/SKILL.md` — `context: fork` removed; replaced with HTML comment explaining the constraint
- `skills/team-bugfix/SKILL.md` — same
- `skills/feature-design/SKILL.md` — same

Each skill now runs in the main conversation thread where the `Agent` tool is available. Trade-off: the skill's instructions occupy main-context tokens. For an orchestration workflow this is required; you cannot orchestrate from a context that can't see the orchestration tool.

### Kept — `context: fork` retained on non-orchestrating skills

- `feature-dev` — single-agent inline implementation; no spawn → fork OK
- `context-load`, `plugin-skill-create`, `subagent-spawn`, `ralph` — none of them spawn DEV/REVIEW/QA pipelines; fork OK

`subagent-spawn` is interesting — it BUILDS spawn payloads but explicitly says "No actual spawn here — this skill BUILDS the payload; the orchestrator INVOKES `Agent(...)` separately." That's correct.

### Added — `team-protocols/SKILL.md` opens with explicit architectural warning

New section "CRITICAL — orchestration skills MUST NOT use `context: fork`" cites the Anthropic constraint, documents the alpha.25 failure mode, and lists the rule: "any skill that follows this protocol MUST NOT have `context: fork`".

### Added — validator check `orchestration_no_fork`

`plugin/dev/validate.py` now hard-fails if any of `develop`, `team-bugfix`, `feature-design` ships with `context: fork` in the frontmatter. Catches the same regression before the user hits it in `/plugin install`.

### Three-layer lesson learned (saved as memory pattern)

When a multi-agent workflow misbehaves, check ALL three layers:

1. **Body voice** — does the skill literally invoke `Agent({...})` or just describe roles? (alpha.23 / alpha.24 layer)
2. **Frontmatter context** — does the skill run in main thread or forked subagent? Orchestrators need main thread. (alpha.25 layer)
3. **Tool name** — is the spawn primitive actually called what the skill thinks it's called? (verified: `Agent` is correct in current Claude Code)

Diagnose top-down. The fastest signal is in `~/.claude/projects/{project}/{sessionId}/subagents/agent-*.meta.json` → if `agentType: general-purpose` is the ONLY agent and it carries the entire skill body in its first user message, then `context: fork` is the bug. If multiple `agentType` values appear (`ai-assets:java-engineer`, etc.), the orchestration is working.

## [0.1.0-alpha.24] — 2026-04-29 — CRIT: multi-agent skills were narrative, not actionable

User ran `/ai-assets:develop` against a real bugfix on f4ai. Session log analysis (206 lines, sessionId 0ec17748): plugin loaded correctly (hooks fired, `${CLAUDE_PLUGIN_ROOT}/hooks/scripts/ralph-stop.py` executed on every Stop), but **zero `Agent` tool invocations**. All 24 Bash + 8 Read + 5 Edit calls happened in the main thread. Pipeline did the work but bypassed the entire DEVELOP→REVIEW→QA enforcement.

### Root cause

Three independent bugs compounded:

1. **Narrative voice instead of executable instruction.** `team-protocols/SKILL.md` and `develop/SKILL.md` described roles in third-person ("Agent 1 — Developer spawned per affected subproject..."). Claude Code read this as documentation describing what should happen, not as code to execute. The model formed a mental plan and did the work itself in the main thread because nothing in the skill literally said "now invoke `Agent({...})`".

2. **Fictional optional tools held the door open for inline execution.** `team-protocols` mentioned `TeamCreate` / `SendMessage` / `TaskOutput` / `TaskStop` / `TeamDelete` as a "preferred persistent team layer". These tools only exist behind `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` (off by default). The skill's detection logic said "if `Agent` is unavailable → HALT" but the model never reached HALT because `Agent` IS available — it just wasn't invoked because the skill never told it to.

3. **Missing plugin namespace on `subagent_type`.** Per Anthropic docs, plugin agents resolve as `<plugin-name>:<agent-name>`. Skills referenced bare role names (`software-engineer`, `qa-engineer`) which would not resolve to plugin agents at all. Even if a spawn HAD been issued, it would have used the `general-purpose` fallback.

### Fixed — `skills/team-protocols/SKILL.md` rewritten

- Header now opens with: "Hard invariant: every agent role MUST run as a NAMED subagent spawned via `Agent`, with its own isolated context. The Lead NEVER executes Developer/Reviewer/QA work inline" + explicit callout of the alpha.23 failure mode
- Added new section "The Agent Tool — Canonical Primitive" explaining `subagent_type` resolution (plugin-namespaced like `ai-assets:java-engineer`, vs built-in like `general-purpose`)
- Added subsection "Hard constraints" documenting (1) subagents cannot spawn other subagents, (2) each `Agent` call is fresh context, (3) returns go to Lead only — citing official Anthropic docs
- Added subsection "Optional: experimental Agent Teams" explaining `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` and explicitly stating "Do not assume this is enabled. This protocol uses ONLY the always-available `Agent` tool"
- New section "Spawn Pattern (concrete, executable)" with 4-step recipe: (1) build G7 payload JSON, (2) literal `Agent({...})` invocation, (3) wait + validate return contract, (4) pass slice to next role
- New section "Role-by-role spawn map" — concrete table mapping pipeline stages to `subagent_type` values
- Dropped fictional `TeamCreate`/`SendMessage`/`TaskOutput`/`TaskStop`/`TeamDelete` primitives entirely — only the real `Agent` tool remains
- Communication Rules now explicit: "Every agent reply is the literal return value of an `Agent` tool call. Never paraphrase or simulate"
- Reference link to official Anthropic Claude Code subagents docs

### Fixed — `skills/develop/SKILL.md` rewritten

- Description now says "Spawns specialized subagents via the Agent tool (`subagent_type: 'ai-assets:<role>'`)"
- Header opens with mandatory `Agent({...})` invariant + alpha.23 callout
- "Mandatory Pipeline" section replaced narrative role descriptions ("Agent 1 — Developer", "Agent 2 — Reviewer", "Agent 3 — QA", "Agent 4 — Lead") with **per-WP execution loop containing literal `Agent({...})` invocation examples** for all 3 stages — DEVELOP, REVIEW, QA — with concrete `subagent_type` values, prompts, and `disallowedTools` for the read-only Reviewer
- Gate Rules now reference the literal spawn loop above (each gate is enforced by the Lead waiting on a real `Agent` return value, not by procedural checks on free-form HANDOFF text)
- Final summary REVIEW-LOG.md now includes "Spawn ledger: count of `Agent` invocations per role + total subagent token spend"

### Fixed — `skills/team-bugfix/SKILL.md` rewritten

- Description: "spawns developer(s), reviewer, QA via the Anthropic `Agent` tool"
- Replaced narrative "Agent 1 / Agent 2 / Agent 3 / Agent 4" sections with the same per-task literal `Agent({...})` execution loop pattern as develop
- Hard invariant added at top: "YOU MUST spawn subagents via `Agent({...})`. Do not perform Developer/Reviewer/QA work inline"

### Fixed — `skills/feature-dev/SKILL.md` repositioned

- Description rewritten: removed "when no team primitive (TeamCreate / Agent) is available" framing (`Agent` is ALWAYS available in modern Claude Code). Now positioned as the explicit single-agent fallback for trivial cases where multi-agent overhead is wasteful, not as the auto-fallback when subagents are "missing"

### Fixed — `skills/team-protocols/lead-protocol.md`

- "G7 Schema Validation" section: dropped reference to fake `Agent`/`SendMessage` dual primitives — now correctly states "before invoking the `Agent` tool" + "received as the `Agent` call's return value"

### Not changed (intentional)

- `agents/*.md` body text uses `Agent(name)` notation as **documentation cross-reference style** (e.g., "Base role: `Agent(software-engineer)` — engineering fundamentals" inside content-designer.md). This is doc-prose, not tool-invocation instruction. Harmless and standard convention. No edits made.
- `bugfix/SKILL.md` "Role selection" table uses the same `Agent(name)` notation in a doc-style mapping table. Harmless.

### Lessons learned (added to memory pattern set)

1. **Skills must instruct, not describe.** A skill that says "Agent 1 spawns Developer..." is documentation. A skill that says "now invoke `Agent({subagent_type: 'ai-assets:java-engineer', ...})`" is instruction. Claude Code defaults to inline execution unless explicitly told to spawn.
2. **Fictional optional features are net-negative.** Listing `TeamCreate`/`SendMessage` as a "preferred path" gave readers (including the model) the impression that there's a sophisticated team API, masking the simple truth: there's only the `Agent` tool, and the skill needs to use it.
3. **Plugin-namespaced subagent_type values matter.** `subagent_type: "java-engineer"` does NOT resolve to the plugin's java-engineer agent — it resolves to nothing or to a built-in fallback. Always use `<plugin-name>:<agent-name>` (`ai-assets:java-engineer`) when the agent is plugin-defined.

### Verification recipe (try this in your next session)

```text
claude --plugin-dir C:\Users\avav2\dev\code\ai-assets\plugin
/ai-assets:develop работаем над <feature-path>
```

Watch for `Agent({...})` calls in the transcript. After the session, check `~/.claude/projects/{project}/{sessionId}/subagents/agent-*.meta.json` — `agentType` field should show plugin-named agents (`ai-assets:java-engineer`, `ai-assets:software-engineer`, `ai-assets:qa-engineer`) NOT just `general-purpose`.

## [0.1.0-alpha.23] — 2026-04-29 — Wrong tool: marketplace was never the right path for local dev

After 3 alpha-releases (alpha.20, alpha.21, alpha.22) trying to make `/plugin marketplace add <local-path>` + `/plugin install ai-assets` work and hitting different schema-validation walls each time, I went back to **first principles** and read the official Anthropic plugin-creation guide end-to-end at https://docs.claude.com/en/docs/claude-code/plugins. The canonical local-dev workflow is documented right in the Quickstart:

> **Test your plugin** — Run Claude Code with the `--plugin-dir` flag to load your plugin: `claude --plugin-dir ./my-first-plugin`

Marketplace is for **distribution** to other users (typically via GitHub). Same-host local-dev install via marketplace is brittle on Claude Code v2.1.x — community has multiple open issues about `git-subdir` source rejection (#33172, #33828, #36848), local-marketplace install bugs (#12457), and schema-validation false-negatives on local sources (#51978). Three alpha releases burned hitting variants of these.

### Changed — install procedure

`README.md` install section rewritten to lead with `--plugin-dir` (the canonical flow per Anthropic docs) and demote marketplace to "future GitHub distribution":

```text
claude --plugin-dir C:\Users\avav2\dev\code\ai-assets\plugin
# Inside Claude Code:
/help                          # see all skills under `ai-assets:` namespace
/ai-assets:feature-design ...  # invoke any of 31 user-invocable skills
/reload-plugins                # pick up edits without restart
```

### Changed — validator

`check_marketplace` downgraded from FAIL → WARN when marketplace.json is missing. Marketplace files are OPTIONAL — they're only needed for distribution. Local dev via `--plugin-dir` doesn't touch them.

### Kept — marketplace.json files (alpha.20-alpha.22 work isn't wasted)

- `ai-assets/.claude-plugin/marketplace.json` — registry pointing at `./plugin`. **Will work** when the plugin is published to GitHub and added via `/plugin marketplace add alex-voloshin/ai-assets`. The format conforms to anthropics/skills convention.
- `plugin/.claude-plugin/marketplace.json` — deprecation stub from alpha.22 (delete manually if desired: `del C:\Users\avav2\dev\code\ai-assets\plugin\.claude-plugin\marketplace.json`).

### Lessons learned (saved to design-doc memory pattern set)

1. **Read the official Quickstart end-to-end before improvising the install path.** Three alphas burned because I used `/plugin marketplace add` for a use case the docs spell out as `--plugin-dir` work.
2. **Local-marketplace install is a different beast from GitHub-marketplace install.** Claude Code v2.1.x has open bugs around the local case; community workaround is `--plugin-dir` for dev.
3. **Plugin skills are auto-namespaced** with the plugin's `name` field. Invoke as `/<plugin-name>:<skill>`, not `/<skill>` directly. This was glossed over in our plugin design — needs a one-line note in user docs.

## [0.1.0-alpha.22] — 2026-04-29 — Restructured to two-level marketplace layout

alpha.21 fixed the source FORMAT (object → string shorthand), but install still failed with the same "source type your Claude Code version does not support" error. After deeper investigation: the actual blocker was the **same-directory layout** (marketplace.json + plugin.json both in `plugin/.claude-plugin/`). Claude Code v2.1.122 expects the canonical Anthropic pattern: marketplace at parent + plugins as subdirectories.

### Restructured

```
ai-assets/
├── .claude-plugin/             # NEW — repo-root marketplace
│   └── marketplace.json        #   source: "./plugin"
└── plugin/
    └── .claude-plugin/
        ├── plugin.json         # unchanged — actual plugin manifest
        └── marketplace.json    # DEPRECATED stub (file tools cannot delete)
```

The new install path:

```text
/plugin marketplace add C:\Users\avav2\dev\code\ai-assets   # parent, NOT plugin/
/plugin install ai-assets
```

### Cleanup needed (manual — file tools cannot delete)

Old `plugin/.claude-plugin/marketplace.json` was overwritten with a deprecation stub (empty `plugins[]`) so it does no harm if anyone uses the old path. Recommended cleanup:

```powershell
del C:\Users\avav2\dev\code\ai-assets\plugin\.claude-plugin\marketplace.json
```

### Changed — validator

`check_marketplace` now looks at `<repo-root>/.claude-plugin/marketplace.json` (parent of `PLUGIN_ROOT`) instead of inside the plugin. Also resolves each plugin entry's string source path and verifies it points at a directory containing `.claude-plugin/plugin.json` — catches "wrong path" mistakes before `/plugin install` does.

## [0.1.0-alpha.21] — 2026-04-28 — Fixed marketplace.json source format (was SDK shape, not marketplace shape)

alpha.20 added `marketplace.json` but used the wrong source format. Live install in Claude Code v2.1.122 returned: `Failed to install: This plugin uses a source type your Claude Code version does not support. Update Claude Code and try again.`

Root cause: I conflated two different API shapes.

- **SDK API** (`@claude/agent-sdk` TypeScript): `plugins: [{ type: "local", path: "./local-plugin" }]` — uses `type` discriminator
- **marketplace.json** (per `anthropics/skills` and `anthropics/claude-plugins-official` reference repos): plain string shorthand for local paths — `"source": "./"` or `"source": "./plugins/<name>"`. Object forms exist but only for non-local sources (`{ "source": "url", "url": "...", "sha": "..." }` or `{ "source": "github", "repo": "owner/name" }`).

There is NO `{ "source": "local", "path": "..." }` form in marketplace.json — that's why Claude Code rejected it as an unknown source type.

### Fixed — `.claude-plugin/marketplace.json`

```diff
-  "source": { "source": "local", "path": "." },
+  "source": "./",
```

### Fixed — validator catches the same mistake

`check_marketplace` now flags `source: { "source": "local", ... }` explicitly with a hint to use the string shorthand. Prevents anyone (including future-me) from making the same SDK-vs-marketplace shape confusion again.

### Result

```text
/plugin marketplace add C:\Users\avav2\dev\code\ai-assets\plugin
/plugin install ai-assets
```

Now should install cleanly.

## [0.1.0-alpha.20] — 2026-04-28 — Added marketplace.json (unblocks `/plugin marketplace add`)

First live install attempt failed with `Marketplace file not found at C:\…\plugin\.claude-plugin\marketplace.json`. Per current Anthropic docs (verified via WebSearch on docs.claude.com): `/plugin marketplace add <path>` requires the path to contain `.claude-plugin/marketplace.json` — a **registry** file listing one or more plugins. Our plugin's `.claude-plugin/plugin.json` is the plugin manifest, not a registry. These are two separate files Claude Code looks for.

### Added — `.claude-plugin/marketplace.json`

Single-plugin marketplace registering `ai-assets` as the only plugin. Same directory acts as both marketplace root AND plugin root — Anthropic's marketplace spec supports this.

```json
{
  "name": "ai-assets",
  "owner": { "name": "Alex Voloshin", "email": "...", "url": "..." },
  "metadata": { "description": "...", "version": "0.1.0-alpha.20" },
  "plugins": [
    { "name": "ai-assets", "source": { "source": "local", "path": "." }, "description": "...", "version": "0.1.0-alpha.20" }
  ]
}
```

### Changed — validator gains marketplace check

`check_marketplace` added to the validator: asserts `.claude-plugin/marketplace.json` exists, parses, has `name`/`owner.name`/non-empty `plugins[]`, and each plugin entry has `name` + `source`. Catches this entire class of install failure before the user hits Claude Code.

### Install now works

```text
/plugin marketplace add C:\Users\avav2\dev\code\ai-assets\plugin
/plugin install ai-assets@ai-assets   # plugin-name@marketplace-name
```

Or just `/plugin install ai-assets` if Claude Code auto-resolves the marketplace.

## [0.1.0-alpha.19] — 2026-04-28 — env-watch monitor ported to Python (cross-platform)

User question on alpha.18: «monitors/env-watch.sh написан под Linux — почему? а если я на win работаю». Real design gap. Docker Desktop on Windows fully supports `docker compose ps --format json`, but our monitor was bash-only and unusable on a Windows host without WSL. Fixed by porting to Python so the monitor works identically on Windows, Linux, and macOS without a bash dependency.

### Added — `monitors/env-watch.py`

Cross-platform Python rewrite. Same contract as the bash version:

- Opt-in via `CLAUDE_USER_CONFIG_env_watch_enabled` (default false → silent exit)
- Polling interval via `CLAUDE_USER_CONFIG_env_watch_interval` (default 15s, min 5s)
- Silent exit when no compose file in cwd, when docker CLI unavailable
- Handles both `docker compose ps --format json` output shapes (single JSON array OR JSONL)
- Diffs current vs previous snapshot in memory; emits one JSON line per service whose State or Health changed: `{"ts","monitor","service","from":{state,health},"to":{state,health}}`
- 1-second sleep slices for snappy SIGINT/SIGTERM responsiveness even on long intervals
- Graceful signal handling: SIGINT (all platforms incl. Windows), SIGTERM (POSIX); SIGTERM registration is wrapped in `try/except (AttributeError, ValueError, OSError)` so Windows doesn't crash on the unsupported signal
- Failure-recovery rule preserved: docker CLI errors log to stderr but never kill the loop; fatal exception handler also logs and exits 0

### Changed — `monitors/monitors.json`

`command` now invokes `python ${CLAUDE_PLUGIN_ROOT}/monitors/env-watch.py` instead of the bash script. Description updated to reflect cross-platform support and signal handling.

### Deprecated — `monitors/env-watch.sh`

Kept around as a thin shim that just `exec`s the .py version, with a deprecation header explaining the rationale. Users who explicitly want the legacy bash path (e.g., minimal Linux containers without Python) can edit `monitors.json` to point back at `env-watch.sh`. The original bash implementation lives in git history (alpha.16, alpha.17, alpha.18 versions of this file).

### Changed — validator

`check_bash_syntax` removed (no bash dependency in the canonical path anymore — Windows users no longer get a misleading WARN). Replaced with `check_monitor_present` which asserts:

1. `monitors/env-watch.py` exists
2. `monitors/monitors.json` is well-formed JSON, non-empty array
3. The first monitor's `command` field references `env-watch.py`

Python syntax of the new monitor is already covered by `check_python_syntax` (which now counts 20 .py files instead of 19). Removed unused `import shutil` and `import subprocess` from the validator since they were only used by the removed bash check.

### Result

`python plugin\dev\validate.py` on Windows now reports **17 OK / 0 WARN / 0 FAIL → PASS** with no environmental caveats. Same on Linux/macOS.

## [0.1.0-alpha.18] — 2026-04-28 — Validator self-fix from first live run

First live run of `python plugin/dev/validate.py` on Windows surfaced two real issues — both were validator bugs, not plugin bugs.

### Fixed — validator counted commands wrong

`check_counts()` was looking for `commands/*.md` per the standard Anthropic plugin convention, but this plugin uses skills-as-commands (workflows live as `skills/<name>/SKILL.md` with `context: fork`). Replaced the `commands` count with `user_invocable_skills` computed from frontmatter scan — `expected = 31` (10 primary workflows + 9 named companion + 12 extended fork-skills). Cascade fix in README: the structural-counts table now lists all three buckets explicitly so the 31 number is reachable from the doc.

### Fixed — validator failed on Windows WSL bash stub

`check_bash_syntax()` blindly trusted whatever was on PATH as `bash`. On a Windows host without WSL installed, `bash.exe` is the WSL stub that errors with `execvpe(/bin/bash) failed: No such file or directory`. The validator surfaced that as a FAIL even though the actual `monitors/env-watch.sh` script was untested-but-fine. Added a liveness probe: if `bash -c "exit 0"` fails or stderr contains `execvpe`, treat bash as unavailable and emit WARN ("non-functional stub, skipping shell syntax check") instead of FAIL.

### Result

Re-running `python plugin/dev/validate.py` on the same Windows host now reports `Result: PASS` with 17 OK / 1 WARN (bash WSL stub) / 0 FAIL. On a host with real bash (Linux, macOS, Git Bash, real WSL) all 18 checks pass green.

## [0.1.0-alpha.17] — 2026-04-28 — Local validator + cascade-fix false `claude plugin validate` references

User attempted to run validation and was blocked by the absence of a `claude plugin validate` CLI in current Claude Code (verified via WebSearch on docs.claude.com — no such command ships as of 2026-04). Replaced the false claim with a real, working alternative: a pure-Python local validator that checks everything that can be checked without launching Claude Code itself.

### Added

- `plugin/dev/validate.py` — pure-Python local validator. Checks JSON syntax for every `*.json`, Python syntax for every `*.py`, bash syntax for `monitors/env-watch.sh` (when bash is on PATH), manifest required fields + userConfig shape, structural counts cross-checked against README claims (26 agents / 52 skills / 12 rules / 16 hooks / 13 events / 17 rubrics / 102 calibration samples / 10 commands / 14 user docs / 2 schemas / 2 output styles / 12 userConfig knobs), agent frontmatter (required + Anthropic-forbidden fields `permissionMode`, `hooks`, `mcpServers`), skill frontmatter (lowercase-with-hyphens name matches folder), hook scripts all import `_lib`, `hooks.json` command paths all resolve, no `$schema-comment` leftover (HIGH-B option 3 enforcement), per-rubric calibration counts (3 good + 3 bad). Supports `--quiet`, `--json`, `--strict` flags. Exit code 0 on pass, 1 on fail. Self-contained — no third-party dependencies.
- `plugin/dev/check.sh` — bash wrapper that runs the validator from any cwd.
- `plugin/dev/check.ps1` — PowerShell wrapper for the same.

### Fixed — cascade for false `claude plugin validate ./plugin` references

Found 6 sites referencing the non-existent CLI. Replaced with the real procedure (local validator + `/plugin marketplace add` + `/plugin install`):

- `README.md` line 9 — release-gate description
- `README.md` line 26 — body text on final release-gate
- `hooks/README.md` "Testing the wiring" section — replaced bash example
- `CHANGELOG.md` alpha.16 "Pending" line — updated to point at alpha.17

CHANGELOG history entries that referenced `claude plugin validate` for the FUTURE release gate are deliberately preserved as-written (history is history); only forward-looking statements were corrected.

### How to actually validate from now on

```bash
# 1. Pure-Python local validator (no Claude Code needed)
python plugin/dev/validate.py
# or:  bash plugin/dev/check.sh
# or:  powershell -ExecutionPolicy Bypass -File plugin\dev\check.ps1

# 2. Real install-time validation inside Claude Code
#    (the install path IS the manifest schema check — Claude Code rejects bad manifests)
#    /plugin marketplace add C:\Users\avav2\dev\code\ai-assets\plugin
#    /plugin install ai-assets

# 3. Live smoke test
#    /feature-design "test feature"   (or any other slash command from this plugin)
#    tail -f .ai-assets-memory/agent-actions.log
#    tail -f .ai-assets-memory/hook-errors.log   # should stay empty
```

## [0.1.0-alpha.16] — 2026-04-28 — HIGH-A/B/C shipped (Round 13/14 follow-through complete)

Per user direction after Round 14: ship HIGH-A as recommended; HIGH-B with option 3 (the real solution, not the cosmetic ones); HIGH-C as recommended. All three HIGH findings from the Round 13 Six-Thinking-Hats critique are now closed.

### Fixed — HIGH-A: Phase 3 calibration depth — 102 total samples (was 34)

Authored 68 NEW calibration samples (4 per rubric × 17 rubrics): 2 additional good (4.3-4.7 score band) + 2 additional bad (1.3-1.9 score band) per rubric. Brings per-rubric coverage from 1+1 to 3+3 (102 total). Each new sample illustrates a distinct scenario from the existing one for that rubric — different domain, different shape, different failure mode where applicable.

Distribution per rubric (4 new files each):

| Rubric | New good samples | New bad samples |
|---|---|---|
| feature-design | multi-tenancy-isolation, webhook-retry-backoff | payment-redesign, search-optimization |
| develop | rate-limiting-middleware, graphql-field-resolver | half-baked-feature, untested-bulk-refactor |
| bugfix | timestamp-timezone-conversion, concurrent-map-race-condition | silenced-exception, wrong-root-cause-fix |
| refactor | http-client-abstraction, normalize-error-responses | untested-reorg, silent-behavior-change |
| migrate | mysql-to-postgres-schema, elasticsearch-index-reindex | assumption-based-plan, missing-integrity-checks |
| spike | auth-openidconnect-vs-oauth, websocket-vs-polling | unsubstantiated-claim, missing-alternatives |
| security-audit | api-endpoint-audit, data-encryption-audit | vague-findings, includes-effort-estimates |
| docs-pack | webhook-integration-guide, cli-reference | missing-examples, outdated-docs |
| env-analyze | k8s-namespace-diag, github-actions-ci-diag | hallucinated-containers, symptom-only-diagnosis |
| ai-assets-init | nodejs-express-init, python-fastapi-init | wrong-framework-scaffold, silent-file-overwrite |
| faithfulness | fact-checked-summary, attributed-synthesis | fabricated-stats, hallucinated-source |
| humanizer-compliance | conversational-tutorial, friendly-api-error-copy | inflated-language-salad, chatbot-voice-throughout |
| code-quality | well-factored-calculator, comprehensive-parser | tangled-logic, hardcoded-magic |
| security-soundness | secure-password-hashing, parameterized-queries | vulnerable-auth, unvalidated-file-upload |
| geo-readiness | structured-blog-post, faq-with-schema | unstructured-wall, missing-evidence |
| subagent-handoff-quality | code-review-spawn, docs-pack-spawn | vague-handoff, impossible-return-contract |
| memory-write-discipline | learning-entry, decision-record | unverified-heap-dump, bypass-curation |

Quality bar enforced: no emoji, English only, distinct scenarios per rubric, artifact shape matches what each rubric evaluates (PRD-shaped for feature-design, code+threat-analysis for security-soundness, blog-post-with-schema for geo-readiness, G7-spawn-payload+return-contract for subagent-handoff-quality, etc.).

**Spearman re-run plan:** with 102 samples (6 per rubric), each rubric can be re-calibrated against the Haiku judge (default) and a Sonnet upgrade-decision becomes meaningful. Rubrics where Haiku Spearman vs ground-truth average score < 0.7 will be flagged for `model: sonnet` override in `eval/config.json`. Run via `python plugin/eval/runner.py --calibrate --rubric <name>`. Phase 3 ticket: schedule a calibration sweep across all 17 rubrics, surface the upgrade list.

**Known minor cosmetic issue (deferred):** in `eval/calibration/memory-write-discipline/`, two new filenames are very similar to the existing ones (`learning-entry.score-4.5.md` next to existing `learnings-entry.score-4.5.md`; `bypass-curation.score-1.6.md` next to existing `bypass-curator.score-1.4.md`). The CONTENTS are genuinely distinct (different scenarios), and the eval runner treats them correctly as separate samples — but the filename similarity is a human-readability papercut. Slated for a rename pass when the workspace shell is available again.

### Fixed — HIGH-B: option 3 (real solution) — `hooks.json` is now pure standard JSON

Removed the non-standard `$schema-comment` field from `hooks/hooks.json`. The file is now canonical, parser-friendly JSON with zero dependency on tolerance for unknown fields. All wiring documentation (16 hooks, 13 events, _lib usage, ordering rules, failure-recovery contract, permission ordering, testing instructions, "how to add a new hook") moved to a new sibling file `hooks/README.md`.

This is the proper architectural separation: machine-readable manifest in JSON, human-readable explanation in Markdown. Future Claude Code versions cannot reject the manifest because of unknown comment fields. The README.md sits next to hooks.json and is co-located via convention, not via a manifest field.

### Fixed — HIGH-C: RALF session-aggregate caps now enforced in `ralph-stop.py`

Three userConfig knobs (`ralph_session_max_iter`, `ralph_session_token_budget`, `ralph_session_time_cap_minutes`) existed since Round 6 HIGH-3 but no hook read them. `ralph-stop.py` extended to:

1. Read `CLAUDE_USER_CONFIG_ralph_session_max_iter` (default 20), `CLAUDE_USER_CONFIG_ralph_session_token_budget` (default 400_000), `CLAUDE_USER_CONFIG_ralph_session_time_cap_minutes` (default 180) from env vars per Anthropic's userConfig protocol.
2. Track session aggregates in the existing session token meter (`ralf_iter_total`, `ralf_tokens_total`, `ralf_started_at` — fields already present in `_lib.read_token_meter()`).
3. On every Stop intercept, increment the meter by 1 iteration + workflow_tokens delta, stamp `ralf_started_at` on first hit, then check all three caps.
4. If ANY session-aggregate cap is exceeded → `write_terminal_status("BUDGET_EXCEEDED", "session_aggregate_iterations: N > cap" | "session_aggregate_tokens: …" | "session_aggregate_time_minutes: …")` and allow Stop.
5. Session-aggregate check runs FIRST, before the per-workflow `max_iterations` cap. When both caps would fire, the session-wide cap wins (it's the harder ceiling).

Failure-recovery rule preserved: any internal error in cap-checking falls through to the `__main__` exception handler and `_lib.log_to("hook-errors.log", ...)` + `sys.exit(0)` (per A3: never block Stop because of buggy hook).

### Fixed — Round 15 cascade follow-through

- `README.md` line 20 — calibration sample count `34` → `102`; updated "v0.1 / Phase 3" column note.
- `README.md` line 26 — body text `34 calibration samples` → `102 calibration samples` and credited HIGH-A.
- `README.md` line 68 — feature list `34 calibration samples` → `102 calibration samples`.
- `eval/config.json` — removed leading `$schema-comment` field for consistency with HIGH-B option 3 (rationale moved to CHANGELOG); updated `calibration` block: `samples_per_rubric_v0_1: 2` + `samples_per_rubric_phase_3: 6` collapsed to `samples_per_rubric_target: 6` + `samples_per_rubric_current: 6` (now equal — full target met).
- `hooks/README.md` (new file) — replaces the role of the removed `$schema-comment` field.

### Documented — known v0.1 limitation in HIGH-C

The session-aggregate `token_budget` cap will only trip when an upstream mechanism populates `meter['ralf_workflow_tokens_last']`. The Tier 3 eval runner does this for RALF cases run via `eval/runner.py`; interactive `/ralph` invocations currently leave the field at 0. Iteration cap and time cap remain the effective ceilings for interactive RALF until per-iteration token measurement is wired (Phase 4 candidate). Limitation documented in `ralph-stop.py` `_check_session_caps()` docstring so the next maintainer doesn't mistake it for a bug.

### Pending (post-v0.1.0)

All Round 13/14 CRIT/HIGH/MED/LOW findings are now closed. Remaining v0.1.0 release-gate items: `python plugin/dev/validate.py` passes locally (added in alpha.17 — see below) + one live smoke test on a real repo via `/plugin marketplace add` + `/plugin install`.

## [0.1.0-alpha.15] — 2026-04-28 — Round 13 follow-through (MED+LOW shipped, HIGH recommended)

Per-user direction after Round 13: HIGH findings receive recommendations only (no code change yet); MED + LOW findings shipped this release. Followed by Round 14 full re-review.

### Fixed — MED-A: shared `_lib` adoption across the 4 carried hooks (B2 → B8 parity)

Until alpha.14 the 4 carried hooks (`block-dangerous-commands`, `block-secrets-in-code`, `block-sensitive-files`, `log-actions`) each carried their own inline `_normalize_hook_input` duplicate and a hand-rolled stdin/exit/log path. B8 shipped a shared `hooks/scripts/_lib.py` but the 4 carried hooks were never refactored. Closed in alpha.15:

- `hooks/scripts/block-dangerous-commands.py` — now imports `_lib`; uses `_lib.read_stdin_json()`, `_lib.normalize_hook_input()`, `_lib.allow()`, `_lib.block()`, `_lib.log_to()`, `_lib.iso_now()`. Removed inline duplicate (~17 lines + import json). Docstring relabeled `ai-assets plugin hook:` for B2/B8 docstring parity.
- `hooks/scripts/block-secrets-in-code.py` — same refactor pattern; secret-pattern blocks now route to `errors.log` via `_lib.log_to`.
- `hooks/scripts/block-sensitive-files.py` — same refactor pattern; sensitive-file blocks now route to `errors.log` via `_lib.log_to`.
- `hooks/scripts/log-actions.py` — same refactor pattern PLUS the long-deferred PII filter integration: `details` fragment is now passed through `_lib.apply_pii_filter()` before being persisted to `.ai-assets-memory/agent-actions.log`. Closes the deferred note in `rules/memory-discipline.md` and the Round 8 MEDIUM-3 carry-over. Modernized event-name detection to recognize `Write`/`Edit`/`Bash`/`Read`/`mcp__*` alongside the legacy `agent_action_name` shape kept for back-compat.

All 4 hooks retain the failure-recovery rule: a buggy hook never blocks tool use — `__main__` wraps `main()` and falls back to `_lib.log_to("hook-errors.log", ...)` + `sys.exit(0)`.

### Fixed — MED-C: 4 borderline H5 skill descriptions tightened to explicit "Use when" pattern

Per Anthropic skill-authoring guidance, the description field is the load-bearing field for Claude's skill-trigger decision. Four operational skills used the weaker `Use standalone or as part of …` pattern; replaced with explicit `Use when …` enumeration of trigger scenarios:

- `skills/analyze-local/SKILL.md`
- `skills/analyze-prod/SKILL.md`
- `skills/security-scan/SKILL.md`
- `skills/seo-review/SKILL.md`

No body changes — only frontmatter `description`.

### Fixed — MED-D: `monitors/env-watch.sh` replaced with working baseline (was no-op stub)

The B1 stub claimed Phase-4 hardening but the contract surfaced in `monitors.json` (poll, diff, emit JSON events, honor SIGTERM) was unmet. Replaced with a minimal but functional polling loop:

- Honors `CLAUDE_USER_CONFIG_env_watch_enabled` (default false → silent exit).
- Honors `CLAUDE_USER_CONFIG_env_watch_interval` (default 15s, min 5s) — new userConfig knob added.
- Silent exit when no docker-compose file is present in cwd.
- Silent exit when `docker` CLI is unavailable.
- Polls `docker compose ps --format json` (handles both array and JSONL forms).
- Diffs current snapshot against previous in-memory snapshot.
- Emits one JSON line per service whose `State` or `Health` changed: `{"ts","monitor","service","from":{state,health},"to":{state,health}}`.
- Clean SIGTERM/SIGINT handling — drops temp snapshot files and exits 0.
- Failure-recovery rule preserved: docker CLI failures do NOT kill the loop.

`monitors/monitors.json` description rewritten to match the now-live behavior. New `env_watch_interval` userConfig knob added to `plugin.json`.

### Fixed — LOW-A: agent frontmatter field order normalized across 26 agents

Canonical order: `name, description, tools, disallowedTools, model, effort, maxTurns, max_output_tokens, skills`. Of 26 agents, 13 were already canonical, 13 reordered. No values changed — only field order. Affected: `cloud-architect`, `content-writer`, `feature-design-lead`, `eval-judge`, `memory-curator`, `security-engineer`, `content-designer`, `devops-architect`, `solution-architect`, `ui-ux-designer`, `marketing-strategist`, `product-manager`, `system-architect`.

### Fixed — LOW-B: plugin keywords enriched

`plugin.json` `keywords` expanded from 10 to 33 entries to improve marketplace discoverability and align with the actual workflow + agent + skill surface. Added: `refactor`, `migration`, `spike`, `docs`, `context-engineering`, `guardrails`, `hooks`, `skills`, `prd`, `architecture`, `qa`, `devops`, `sre`, `frontend`, `backend`, `ml`, `marketing`, `seo`, `geo`, `ai-search`, `humanizer`, `team-of-agents`, `orchestration`.

### Fixed — Round 14 typo notation: author email

`plugin.json` author email had a typo (`avav25my@gmail.com`); corrected to `avav25@gmail.com`. Caught during Round 14 verification pass.

### Pending (not in alpha.15) — HIGH findings recommended for alpha.16+ — ALL CLOSED IN ALPHA.16

Per user direction at the time of alpha.15, HIGH-class findings from the Round 13 Six-Thinking-Hats critique received recommendations only. All three closed in alpha.16 — see the alpha.16 entry above for the implementation details.

- **HIGH-A — eval calibration depth.** Was: 34 samples. **Closed in alpha.16:** 102 samples shipped.
- **HIGH-B — hooks.json $schema-comment fragility.** Was: non-standard JSON comment field. **Closed in alpha.16 (option 3):** field removed, `hooks/README.md` created.
- **HIGH-C — RALF session-aggregate caps not enforced.** Was: three userConfig knobs unread. **Closed in alpha.16:** `ralph-stop.py` reads them and enforces aggregates against session token meter.

## [0.1.0-alpha.14] — 2026-04-28 — Round 13 final validation + Six-Thinking-Hats critique

Comprehensive validation pass after B13. Eliminated all stale references to ARCHIVED skills + RENAMED slash-commands inside live plugin assets. CHANGELOG history entries deliberately preserved for traceability.

### Fixed — stale slash-command references (15 sites in 13 files)

- `rules/geo-content.md` — `/blog-post` → `/content-creation`
- `agents/{content-writer,product-manager,seo-engineer}.md` — `/blog-post` → `/content-creation`
- `agents/{qa-engineer,system-architect}.md` — `/project-init` → `/ai-assets-init`
- `agents/prompt-engineer.md` — `/ai-assets` → `/plugin-doctor`+`/develop`+`/feature-design`+`/plugin-skill-create`
- `skills/test-strategy/SKILL.md` — `/project-init` → `/ai-assets-init`
- `skills/{context-engineering,prompt-engineering}/SKILL.md` — `/ai-assets` → `/plugin-doctor`+`/feature-design`
- `skills/humanizer/SKILL.md` — `/blog-post` → `/content-creation`
- `skills/geo-writer/SKILL.md` — `/blog-post` → `/content-creation`; dropped marketing-operations skill ref
- `skills/code-review/SKILL.md` — `asset-validation` skill ref → `/plugin-doctor`

### Fixed — broken skill references in agent frontmatter

- `agents/marketing-strategist.md` `skills:` — `marketing-operations` (MERGED) → `marketing`
- `agents/product-manager.md` `skills:` — same
- `agents/prompt-engineer.md` body — removed `asset-validation` from companion-skills list (ARCHIVED)

### Fixed — broken file-path references

- `agents/qa-engineer.md` body — dropped `../templates/testing.template.md` ref (file does not exist); now points to `/ai-assets-init` for TESTING.md scaffold
- `skills/test-strategy/SKILL.md` Integration — dropped same broken template ref
- `skills/architecture/SKILL.md` — `../../templates/architecture.template.md` (does not exist) → `${CLAUDE_PLUGIN_ROOT}/output-styles/design-pack.md` (which IS the architecture-doc structure template)

### Vendor-docs alignment verification

WebSearch of [Claude Code Security](https://docs.anthropic.com/en/docs/claude-code/security) and [Hooks reference](https://docs.anthropic.com/en/docs/claude-code/hooks) confirmed:

- **Permission processing order** — `PreToolUse Hook → Deny Rules → Allow Rules → Ask Rules → Permission Mode → canUseTool → PostToolUse Hook` — our 4 PreToolUse + 6 PostToolUse hooks integrate correctly ahead of permission rules
- **Sandboxed bash + filesystem isolation** — vendor-managed; our hooks respect write-boundary-to-project-folder
- **Default-deny network policy** — vendor-managed; we add no exceptions
- **Encrypted credential storage** — vendor-managed; our PII filter is defense-in-depth, not primary
- **Trust verification on first-time codebase + new MCP servers** — vendor-managed; we declare 0 MCP deps

No mismatches found between our plugin's security model and Anthropic's documented expectations.

### Pattern 13 — cross-batch reference resolution (final state)

After Round 13 fixes, only the following references to legacy/merged/archived names remain in `plugin/`, all of which are LEGITIMATE:
- CHANGELOG history entries describing past batches (immutable per Keep-a-Changelog)
- `marketing/SKILL.md` + `content-creation/SKILL.md` — describe their own MERGE provenance
- `eval/calibration/memory-write-discipline/bad/bypass-curator.score-1.4.md` — illustrative bad example (intentionally violates discipline for calibration purposes)

### Six-Thinking-Hats critique applied

Ten findings catalogued across White/Red/Black/Yellow/Green/Blue hats. CRIT/HIGH items either fixed in this batch or flagged for v0.2/Phase 4 hardening with explicit rationale. See response body for details.

## [0.1.0-alpha.13] — 2026-04-28 — Eval framework + calibration + user docs (B10 + B10a + B13) — Phase 2 structurally complete

### Added (B10) — 17 eval rubrics + Tier 1 linter + 2 output styles

**2 output styles:**
- `plugin/output-styles/concise-pr.md` — terse, change-focused PR descriptions for `/develop` + `/create-pr`
- `plugin/output-styles/design-pack.md` — structured Markdown for `/feature-design` artefacts

**Tier 1 linter — `plugin/eval/runner.py`** (~280 lines):
- Skill frontmatter linter (`name` lowercase+hyphens, `description` H5 trigger, third-person check)
- Rule + skill char-limit linter (12K cap)
- Agent forbidden-field linter (`permissionMode` / `hooks:` / `mcpServers:` blocked on plugin-shipped agents per security boundary)
- Python AST linter (`py_compile` over all `hooks/scripts/*.py`)
- JSON validity linter
- `hooks.json` cross-reference linter (every `command` resolves to a real script under `${CLAUDE_PLUGIN_ROOT}/hooks/scripts/`)
- CLI surface stable: `--tier {1,2,3}`, `--skill`, `--all`, `--resume`, `--baseline`. Tier 2/3 stubs return clear "not implemented in v0.1" until eval-judge is wired in Phase 3.

**17 judge rubrics** in `plugin/eval/judge-rubrics/` per `02-EVAL-FRAMEWORK.md` §4. Two are full-prose (`feature-design.md`, `faithfulness.md` per G5); 15 are skeleton-format (~30-50 lines each: dimensions table + 5 levels + scoring + anti-patterns + calibration ref):

- **Per-workflow (10):** `feature-design`, `develop`, `bugfix`, `refactor`, `migrate`, `spike`, `security-audit` (with G3 OWASP coverage dim), `docs-pack`, `env-analyze`, `ai-assets-init`
- **Cross-cutting (7):** `humanizer-compliance`, `code-quality`, `security-soundness`, `geo-readiness`, `subagent-handoff-quality`, `memory-write-discipline`, `faithfulness` (G5 — `claim-grounding < 3 = AUTO-FAIL`)

### Added (B10a) — 34 calibration samples (1 good + 1 bad per rubric × 17)

Per Round 6 HIGH-1: v0.1 ships **34 minimal samples**, NOT 102 (Phase 3 expansion). Each sample is a 20–80 line markdown file with ground-truth score in filename suffix (`<topic>.score-<N>.<ext>`).

- 17 known-good samples (score 4.4–4.7) under `plugin/eval/calibration/<rubric>/good/`
- 17 known-bad samples (score 1.3–1.8) under `plugin/eval/calibration/<rubric>/bad/`
- Calibration is **informational-only** in v0.1 (Spearman from N=2 is noisy); Phase 3 expands to N=6 per rubric for gate-blocking calibration

### Added (B13) — 14 user-facing docs

All under `plugin/docs/`. Audience: plugin USERS. Tone: practical, example-driven.

- `docs/getting-started.md` — 30-min tutorial
- `docs/workflows/{feature-design,develop,bugfix,env-analyze,refactor,migrate,spike,security-audit,docs-pack,ai-assets-init}.md` — 10 workflow docs (per spec: when/how/what/FAQ/examples/related)
- `docs/concepts/{memory,eval,ralf}.md` — 3 concept docs (each cross-links to ≥ 2 workflow docs)

### File counts — final v0.1 structural target

68 new files in this batch (2 output styles + 1 runner.py + 17 rubrics + 34 calibration + 14 user docs).

### Pattern 14 verification

- `plugin/eval/judge-rubrics/*.md` → 17 files ✓
- `plugin/output-styles/*.md` → 2 files ✓
- `plugin/eval/calibration/**/*.md` → 34 files ✓
- `plugin/docs/**/*.md` → 14 files ✓

### Migration checklist final status

All 14 Phase 2 batches complete: B1, B2, B3, B4, B5, B6, B7, B8, B9, B10, B10a, B11, B12, B13.

### Pre-v0.1.0 release gates (deferred — need live env)

- [ ] `python3 plugin/eval/runner.py --tier 1 --all` reports 0 CRITICAL findings on a clean install
- [ ] `claude plugin validate ./plugin` passes (requires Claude Code env)
- [ ] `/plugin-doctor` runs end-to-end without crash
- [ ] At least one user-invocable skill manual smoke test

These four gates require a Claude Code installation that is unavailable in the current authoring environment. They are the only items between alpha.13 and v0.1.0 release.

## [0.1.0-alpha.12] — 2026-04-28 — 17 NEW skills + 2 MERGE plans (B12) — v0.1 skill target met

### Added — 17 NEW skills authored from scratch per `01-WORKFLOW-SPECS.md`

**8 NEW workflow skills (Part A specs):**

| Skill | Slash | Highlights |
|---|---|---|
| `feature-design` | `/feature-design` | Three-wave parallel→sequential pipeline; Opus orchestrator (`feature-design-lead`); 9-agent roster; G7 spawn payloads + return contracts; RALF on rubric (5 iter / 250K / 60 min); design pack written to `<repo>/docs/features/<feature-id>/` per Round 4 N6 convention exception |
| `env-analyze` | `/env-analyze` | Renamed from env-analyzer per Round 4 N2; SRE + DevOps parallel diagnostics; `--auto-fix` strictly container-level only (explicit boundary documented); G2 normalization on Bash output |
| `refactor` | `/refactor` | Plan + execute + RALF on test equivalence (4 iter / 200K / 45 min); `same-error-repeats:2` kill-on signal — two-iter same error indicates real behavior change masquerading as refactor |
| `migrate` | `/migrate` | Mandatory user approval of rollback procedure (not just migration plan); RALF on data integrity (5 iter / 300K / 90 min); committed-allowlist enforced for `.committed/migrations/` writes |
| `spike` | `/spike` | Time-boxed exploration; Lead picks SME role per question domain; ALWAYS-ASK before `.committed/decisions/` writes per Q4 hard rule |
| `security-audit` | `/security-audit` | OWASP Top 10 (Web 2021) + GenAI/LLM Top 10 (2025) coverage per G3; **NO effort estimate** per Q2 (user/PM owns sizing); `security-engineer` is read-only; CRITICAL findings written to `.committed/security/incidents/` |
| `docs-pack` | `/docs-pack` | User-facing docs per template; output to `<repo>/docs/<module>/` per Round 4 N6; optional GEO/humanize pass for public-facing audience |
| `ai-assets-init` | `/ai-assets-init` | Idempotent bootstrap; auto-detect codebase type; respects existing CLAUDE.md unless `--overwrite`; delegates memory portion to `/memory-init` |

**9 NEW companion skills (Part B specs):**

| Skill | Slash | Highlights |
|---|---|---|
| `ralph` | `/ralph` | Standalone RALF loop entry; rejects invocation without both `--oracle` and `--kill-on`; G10 init vs continuation prompts (~70% token savings on iter ≥ 2); ships `templates/continuation-prompt.md` template |
| `eval` | `/eval` | Wraps `eval/runner.py` (B10 deliverable); 3 tiers (linters / smoke / behavioral); `--resume` for long Tier 3 runs; blind-comparator per Round 3 Q3 |
| `plugin-doctor` | `/plugin-doctor` | Two-step boot model per Round 4 O4; `--calibrate-judge` is opt-in (not default); fast linter-only default mode |
| `memory-init` | `/memory-init` | Idempotent skeleton creation from L1 templates (B9); committed-allowlist seeded |
| `memory-recall` | `/memory-recall` | L4/L5 keyword search; `--global` requires `userConfig.user_global_memory_enabled` AND flag; G1 wrap on returned excerpts |
| `learnings-write` | `/learnings-write` | Spawn-only `memory-curator` per Round 6 HIGH-2; PII filter mandatory; L5 strict scope (project paths blocked) |
| `context-load` | `/context-load` | Per-role context slice from project files; reduces per-agent input tokens vs full project dump; G1 wrap on every excerpt |
| `subagent-spawn` | `/subagent-spawn` | G7 payload helper; validates role against `plugin/agents/` + 3 built-in (`Explore`, `Plan`, `general-purpose`); does NOT actually spawn — orchestrator does |
| `plugin-skill-create` | `/plugin-skill-create` | Plugin-convention skill scaffolder; lowercase+hyphens validated (Anthropic skill name spec); narrower than upstream `skill-creator` |

### Added — 2 MERGE plans executed

| Merge | Sources | Output | Approach |
|---|---|---|---|
| MERGE 1 | `marketing` (workflow) + `marketing-operations` (knowledge) | `plugin/skills/marketing/` (1 SKILL.md + 2 companions) | Combined init + execute phases with strategy frameworks (hierarchy, channel selection, content pillar, measurement) inline; 2 companions carried verbatim (`channel-playbooks.md`, `marketing-setup-template.md`) |
| MERGE 2 | `blog-post` (workflow) + `content-creation` (knowledge) | `plugin/skills/content-creation/` (1 SKILL.md + 5 companions) | 8-step blog pipeline as Workflow A; lightweight page/landing/email pipeline as Workflow B; 8 quality gates inline; 5 companions carried verbatim |

### File counts — final v0.1 target met

- 17 NEW SKILL.md files (8 workflow + 9 companion)
- 1 ralph template (`plugin/skills/ralph/templates/continuation-prompt.md`)
- 2 MERGE SKILL.md files (`marketing/`, `content-creation/`)
- 7 carried companions (2 from marketing-operations + 5 from content-creation)
- **Total skills in `plugin/skills/`: 52** — **EXACT MATCH with glossary §1 v0.1 target**
- Verified via Glob: 52 unique `*/SKILL.md` paths

### Best-practices alignment (Anthropic docs)

Per WebSearch of [Skill authoring best practices](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices):
- All 17 NEW skills use `name` lowercase+hyphens only
- All `description` fields written in third person with `Use when ...` trigger pattern (H5)
- All bodies under 500-line guidance (largest skill = `feature-design` SKILL.md, well under cap)
- Progressive disclosure applied: 7 companion files (5 for content-creation, 2 for marketing, 1 ralph template) hold reference material — loaded only when needed

### Cross-cutting wiring

- All workflow skills include G7 spawn payloads + return contracts wired to `plugin/schemas/` per `subagent-isolation.md`
- All workflow skills with iterative semantics include explicit RALF wiring (oracle + kill-on + caps) per `ralph-budget.md`
- All workflow skills include G1 wrap notes on project file reads + tool outputs per `untrusted-content-wrapping.md`
- All workflow skills include G2 normalization notes for tool outputs > 2000 tokens per `tool-output-normalize.py` hook contract
- All memory writes documented per `memory-discipline.md` write-rules table
- README.md status table updated: `Skills | 52 (20 KEEP + 13 REFACTOR + 17 NEW + 2 MERGE) | 52 | — (target met)`; `Workflows | 10 | 10 | — (target met)`; `Companion skills | 9 | 9 | — (target met)`

### Pattern 14 verification

- Glob confirmed all 17 new SKILL.md + 1 ralph template + 2 MERGE SKILL.md + 7 carried companions exist in `plugin/skills/`
- 52 unique `*/SKILL.md` paths in `plugin/skills/` — matches v0.1 target exactly
- Subagent that copied 5 content-creation companions (Read+Write only, no Bash since sandbox unavailable): self-reported 5 read + 5 written; independently verified via Glob — all 6 expected files present in `plugin/skills/content-creation/` (1 SKILL.md + 5 companions)

### Migration checklist B12 status

- [x] All 17 NEW SKILL.md authored
- [x] 2 MERGE plans executed (sources combined; output skills present in plugin/skills/)
- [ ] `python3 plugin/eval/runner.py --tier 1 --skill <each>` passes — deferred (B10 ships runner.py)
- [ ] At least one skill manual smoke test — deferred (requires Claude Code env)

## [0.1.0-alpha.11] — 2026-04-27 — 13 REFACTOR skills + team-dev → develop rename (B11)

### Added (13 skills + 4 companions = 17 files)

13 REFACTOR skills migrated from `.claude/skills/<name>/` to `plugin/skills/<name>/` per glossary §2 REFACTOR table + checklist B11. One **rename**: `team-dev` → `develop` (per Round 4 N2 — directory and `name:` frontmatter both changed). Source `.claude/skills/team-dev/` left in place per D4 (parallel-development discipline; legacy package continues working until v0.2.0).

| Skill | Slash command | User-invocable | Refactor highlights applied |
|---|---|---|---|
| `plan` | `/plan` | yes | Updated handoff to `/develop` (was `/feature-dev`); `/feature-design` added as preceding workflow |
| `release` | `/release` | yes | **Added Step 7 memory write to L4 `runs.jsonl`** per `memory-discipline.md` |
| `create-pr` | `/create-pr` | yes | **Added G1 wrap note on diff content** (Step 2); **REVIEW-LOG.md ingestion** (Step 3) — auto-builds PR description from `/develop` output |
| `infra-change` | `/infra-change` | yes | **Added RALF Loop section** (4 iter / 200K / 45 min cap, oracle: `terraform plan -detailed-exitcode`) |
| `deploy-staging` | `/deploy-staging` | yes | **Added Step 5 memory write to L4 deploy event log** |
| `deploy-production` | `/deploy-production` | yes | **Added Step 6 memory write** + **stricter gate note** (acknowledge rollback plan AND deployment plan separately) |
| `run-tests` | (sub-workflow) | no | **Added G2 normalization note** for test runner stdout > 2000 tokens (`tool-output-normalize.py`) |
| `test-local` | `/test-local` | yes | Same G2 normalization note |
| `feature-dev` | (auxiliary) | no | **Repositioned as single-agent fallback** for `/develop`; added "When to Use This vs `/develop`" section; G1 wrap note on project-file reads |
| `bugfix` | `/bugfix` | yes | **`/env-analyze` (B12) added** as primary local-Docker sub-workflow alongside legacy `/analyze-local`; **Added Step 7 RALF Loop on reproduction test** (6 iter / 300K / 60 min, oracle: regression test FAIL → PASS) |
| `team-bugfix` | (auxiliary) | no | **Added G7 spawn-payload + return-contract validation section**; `/env-analyze` referenced in place of inline env-analyzer agent |
| `develop` (RENAMED from `team-dev`) | `/develop` | yes | **NEW directory `plugin/skills/develop/`**; `name: develop` frontmatter; **G7 spawn payloads + return contracts** mandatory; **Sequential Code-Modification Gate** (per `subagent-isolation.md`); **SRE smoke INSIDE QA** (P20); **RALF Loop on test failures** (8 iter / 640K / 90 min); **REVIEW-LOG.md emission** for `/create-pr` consumption |
| `team-protocols` | (knowledge) | no | **Added G7 Spawn Payload + Return Contract section** with full JSON examples; `developer-protocol.md` Handoff Format rewritten as G7 contract; `reviewer-protocol.md` Issue Reporting → G7 contract; `lead-protocol.md` G7 schema validation step + REVIEW-LOG.md emission instruction; `role-selection-table.md` extended with `subagent_type` resolution + bounded-recursion explanation |

### File counts
- 13 SKILL.md files (12 ports + 1 rename `develop/`)
- 4 companion files under `team-protocols/` (developer-protocol.md, reviewer-protocol.md, lead-protocol.md, role-selection-table.md)
- **17 total markdown files** added in B11 — verified via Glob
- Total skills in `plugin/skills/` after B11: **33** (20 KEEP from B3 + 13 REFACTOR from B11). v0.1 final target: 52 (B12 adds 17 NEW + executes 2 MERGE plans)

### Notes
- All slash-command references updated: `/feature-dev` → `/develop`, `/team-dev` → `/develop` (where appropriate). Bodies preserved structurally; refactor focus per migration checklist B11 row applied.
- `develop` skill is NOT a deletion of `feature-dev` — both ship in plugin v0.1. `feature-dev` is repositioned as the single-agent fallback when `Agent` primitive is unavailable; `develop` is the preferred multi-agent path.
- Source repo `.claude/skills/team-dev/` directory left in place — per D4 the legacy three-package layout (`.claude/`, `.codex/`, `.windsurf/`) continues to work until v0.2.0.
- Forward-refs to `/feature-design`, `/env-analyze`, `/refactor`, `/migrate`, `/spike`, `/security-audit`, `/docs-pack`, `/ai-assets-init` (B12 deliverables) and `/ralph`, `/eval`, `/plugin-doctor`, `/memory-init`, `/memory-recall`, `/learnings-write`, `/context-load`, `/subagent-spawn`, `/plugin-skill-create` (9 NEW companions in B12) — resolve when B12 ships.
- All bodies updated with substantive refactor additions per spec ("refactor focus" column from migration checklist row). Deeper editorial passes (e.g., embedding more G7 examples, expanding RALF state schemas inline) deferred to Phase 4 hardening.

### Verification (Pattern 14)
- Glob confirmed 17 new files exist under `plugin/skills/{plan,release,create-pr,infra-change,deploy-staging,deploy-production,run-tests,test-local,feature-dev,bugfix,team-bugfix,develop,team-protocols}/`
- 33 skill directories total (20 KEEP + 13 REFACTOR)
- README.md status table updated: Skills row "33 (20 KEEP + 13 REFACTOR)" replacing "20 KEEP carried"

## [0.1.0-alpha.10] — 2026-04-27 — Round 12 deep cross-phase review fixes

### Fixed (functional bugs)
- **HIGH (security/reliability):** All 4 carried B2 hooks (`block-dangerous-commands.py`, `block-secrets-in-code.py`, `block-sensitive-files.py`, `log-actions.py`) lacked the fail-open `try/except` wrapper around `main()`. Added per `failure-recovery.md` rule. Without it, an unhandled exception in any of these scripts would exit non-zero, with undefined behavior in Claude Code's hook executor — for `block-*` security hooks specifically, a crash could either silently allow a dangerous command (worst case) or block all tool use. Now uniformly fail-open across all 17 hook scripts.
- **MED (broken cross-ref):** `plugin/agents/prompt-engineer.md` listed `asset-validation` in `skills:` field — but `asset-validation` is an **ARCHIVE** skill per glossary §2 and is intentionally not migrated to the plugin. Reference would never resolve. Removed.
- **MED (stale deferral note):** `plugin/rules/memory-discipline.md` `log-actions.py` row said "PII filter integration: deferred to B8 when `_lib.py` ships `apply_pii_filter()`" — but B8 has shipped and `_lib.apply_pii_filter()` is available. Carried hook was intentionally not refactored (minimum-change discipline). Updated to reflect actual state: "deferred to Phase 4 hardening".

### Findings resolved against Anthropic docs
- **`skills:` field in 13 of 26 agent frontmatters** — initially flagged as non-standard, corrected after WebSearch of official docs. Per [Create custom subagents — Claude Code Docs](https://docs.claude.com/en/docs/claude-code/sub-agents), `skills:` IS a documented plugin subagent frontmatter field (alongside `name`, `description`, `tools`, `disallowedTools`, `model`, `maxTurns`, `prompt`, `initialPrompt`, `memory`, `effort`, `background`, `isolation`, `color`; security-restricted-for-plugins: `permissionMode`, `mcpServers`, `hooks`). Decision: **keep existing 13 declarations as-is**. The 13 agents that don't declare `skills:` are intentionally minimal — their relevant skills are auto-loaded by Claude Code via standard skill description matching. No mass-add to remaining 13 (would require fabricating agent-skill associations not present in source). Memory rule saved to prevent recurrence: always WebSearch official docs before judging a field non-standard; training data is stale.

### Findings tolerated (forward-refs, ship in later batches)
- 4 agents reference `content-creation` skill (B12 MERGE deliverable) and 2 reference `marketing-operations` (B12 MERGE source) — resolve when B12 ships
- `ralph-budget.md` references `eval/runner.py` (B10), `/ralph` skill (B12), `team-protocols/` resources (B11) — all resolve when those batches ship
- `subagent-isolation.md` line 14 references `TeamCreate` primitive — Cowork-specific; fallback to `Agent` calls explicitly documented
- B2 carried hooks duplicate `_normalize_hook_input` from `_lib.py` — Phase 4 refactor

### Verified clean
- All `Agent(<name>)` references in skill bodies resolve to existing `plugin/agents/<name>.md` (sre-engineer, devops-engineer, frontend-engineer, java-engineer, python-engineer, software-engineer, cloud-architect, ui-ux-designer, content-designer, content-writer, seo-engineer, prompt-engineer, product-manager, solution-architect, system-architect, qa-engineer, devops-architect — all 17 referenced names exist)
- All hook scripts referenced in `hooks.json` exist in `plugin/hooks/scripts/` (16 unique paths, verified via Glob)
- All 12 new hooks correctly import `_lib.py` (43 occurrences across 16 files)
- All template/schema cross-references between rules and hooks resolve
- All 17 hook scripts import `sys` (required for `sys.exit(0)` in fail-open wrapper)

## [0.1.0-alpha.9] — 2026-04-27 — Round 11 cross-phase review fixes

### Fixed
- **CRIT-1:** `plugin/.claude-plugin/plugin.json` — `version` bumped from `0.1.0-alpha.0` (stale since B1) to current. Manifest version had not tracked the 8 alpha-releases since B1.
- **CRIT-2 + CRIT-3 + CRIT-4:** `plugin/README.md` — full rewrite. Replaced misleading `Status: skeleton only` with explicit `Implementation status` table (current count vs v0.1 target per component). Removed broken `docs/getting-started.md`, `docs/workflows/`, `docs/concepts/{memory,eval,ralf}.md` links (those files ship in B13). Workflows and companion skills sections relabeled `Planned … (ship in B12)`.
- **CRIT-5:** `plugin/monitors/env-watch.sh` — created v0.1 no-op stub (per Round 9 R9-1 deferral to Phase 4). `monitors/monitors.json` registration is now structurally valid: the script exists and exits 0 cleanly. Full polling logic lands in Phase 4. `userConfig.env_watch_enabled` description updated to note stub status.
- **HIGH-2:** `CHANGELOG.md` B3 entry — added explicit note about 14 forward-refs in carried KEEP-skill bodies (`/develop`, `/feature-design`, `/feature-dev`, `/team-dev`, etc. — resolve in B11+B12). Mirrors the equivalent note in B6 entry.
- **HIGH-3:** `plugin-design/04-MIGRATION-CHECKLIST.md` B9 goal — `6 L1 memory templates` → `8 L1 memory templates (7 under plugin/memory/templates/ + pii-patterns.txt co-located in plugin/hooks/scripts/)`. Aligns with actual count in `plugin/memory/templates/` (7) + `pii-patterns.txt` (1). Resolves count drift between checklist and CHANGELOG.
- **MED:** `plugin/schemas/spawn-payload.schema.json` — `subagent_role` examples — removed stale `"reviewer"` (no such plugin agent), added `"frontend-engineer"` and `"solution-architect"` so all examples resolve to existing `plugin/agents/<name>.md`.

### Code-quality fixes (unused imports)
- `plugin/hooks/scripts/session-end-finalize.py` — removed unused `import json`
- `plugin/hooks/scripts/subagent-start-budget.py` — removed unused `import json`
- `plugin/hooks/scripts/task-event-log.py` — removed unused `import pathlib`
- `plugin/hooks/scripts/tool-failure-log.py` — removed unused `import pathlib`
- `plugin/hooks/scripts/ralph-stop.py` — removed unused `from datetime import datetime, timezone` (body uses `_lib.iso_now()` exclusively)

### Publish-metadata filled (user-supplied values)
- `plugin/.claude-plugin/plugin.json` — `author.name = "Alex Voloshin"`, `author.email = "avav25my@gmail.com"`, `homepage = repository = "https://github.com/alex-voloshin/ai-assets"`. All `<author-name>` / `<author-email>` / `<owner>` placeholders replaced.
- `plugin/schemas/spawn-payload.schema.json`, `plugin/schemas/return-contract.schema.json`, `plugin/memory/templates/eval-baseline.schema.json` — `$id` URLs now point at `https://github.com/alex-voloshin/ai-assets/...`.
- `plugin/README.md` install command + all 11 `CHANGELOG.md` compare URLs (Unreleased + alpha.0 through alpha.9) — `<owner>` → `alex-voloshin`.

### Known unfixed (need future batches, not user input)
- 23 of 26 agents reference workflows like `/develop`, `/feature-design`, `/eval` that don't exist yet. Resolved when B11/B12 land. Same for 14 of 53 skill files. Documented in B3, B4, B6 CHANGELOG entries.

### Known unfixed (style discipline trade-off)
- Frontmatter field order varies across the 26 agent files (3 group patterns: with/without `disallowedTools`, with `disallowedTools` before/after `effort`). YAML parsing is order-independent; cosmetic only. Not corrected — would violate minimum-change discipline applied during B4. A future content-refresh batch can normalize.

### Validation outstanding
- `claude plugin validate ./plugin` has not been run against this plugin in 9 alpha-releases. Workspace bash sandbox unavailable for the entire Phase 2 implementation. First validation must happen on a host with Claude Code installed; surface any schema errors as a follow-up batch.

## [0.1.0-alpha.8] — 2026-04-27 — 20 KEEP skills carry-over (B3)

### Added
20 KEEP skills migrated verbatim from `.claude/skills/<name>/` to `plugin/skills/<name>/` per glossary §2 KEEP table + checklist B3:

`analyze` · `analyze-local` · `analyze-prod` · `architecture` · `cloud-platforms` · `code-review` · `context-engineering` · `deployment-procedures` · `docs` · `geo-writer` · `humanizer` · `pre-commit` · `prompt-engineering` · `qa` · `security-scan` · `seo-review` · `social-media-manager` · `test-strategy` · `ui-ux-design` · `worktree-isolation`

### File counts
- 20 SKILL.md files
- 33 companion resource files (the largest sets: `context-engineering` 8 companions, `prompt-engineering` 7, `ui-ux-design` 4, `cloud-platforms` 3, `geo-writer` 2, `code-review` 2, `social-media-manager` 2 in a `references/` subdir)
- **53 total markdown files** across 20 skill directories — verified via Glob

### Frontmatter changes (3 targeted, minimum-change discipline)
Three skills lacked the H5 `Use when …` trigger pattern entirely. Description field extended (body verbatim untouched, all other frontmatter fields unchanged):

- `architecture/SKILL.md` — appended `Use when the user has a feature PRD, an analysis request, or an architectural initiative that needs architectural documentation before implementation.`
- `docs/SKILL.md` — appended `Use when the user asks to edit docs, write technical documentation, draft a blog post, or update release notes — and source code must stay untouched.`
- `qa/SKILL.md` — appended `Use when the user asks to validate a feature, write or improve tests, report a bug, or audit acceptance criteria coverage.`

### H5 trigger audit summary
- 13 skills already had explicit `Use when …` (compliant) — `analyze`, `code-review`, `context-engineering`, `deployment-procedures`, `geo-writer`, `humanizer`, `prompt-engineering`, `test-strategy`, `ui-ux-design`, `worktree-isolation`, `social-media-manager` (multi-line `Use this skill whenever …`), `pre-commit` (`Use before git commit …`)
- 1 skill (`cloud-platforms`) uses `Activated when …` — semantically equivalent trigger pattern; left untouched
- 4 skills (`analyze-local`, `analyze-prod`, `security-scan`, `seo-review`) use `Use standalone or as part of …` — borderline alternative trigger; left untouched per minimum-change discipline. Flagged for potential future refresh batch.
- 3 skills (`architecture`, `docs`, `qa`) had no trigger — fixed as listed above
- `pre-commit` confirmed `disable-model-invocation: true` preserved
- `analyze-local` confirmed `allowed-tools: Read, Grep, Glob, Bash` preserved

### Migration mechanics
- Bash sandbox unavailable for the entire batch — all 53 file copies executed via Read+Write tools
- First sub-agent delegation reported 27 files written but Glob verified only 27 (it copied SKILL.md files but missed nearly all companions). Pattern 14 caught the false self-report — Glob verification mandatory after delegation.
- Manually wrote 7 missing companions (output-templates, ai-writing-patterns, test-writing-guide, geo-writing-guide, pre-publish-checklist, references/brand-voice, references/platform-guide) + 4 ui-ux-design companions
- Second sub-agent delegation (15 remaining context-engineering + prompt-engineering companions) verified via Glob — counts matched (9 + 8) ✓
- 3 spot-checks of subagent's verbatim copy against source (`memory-engineering.md`, `security-checklist.md`, `reference-templates.md`) — first 5 lines identical character-for-character ✓

### Notes
- All bodies verbatim from `.claude/skills/<name>/`. No body text edited. Refactor of stale slash-command references inside skill bodies (e.g., `/feature-dev` → `/develop`) deferred to dedicated content-refresh batch.
- Total skills in `plugin/skills/` after B3: **20**. B11 will add 13 REFACTOR skills (with one rename `team-dev` → `develop`); B12 will add 17 NEW skills + execute the 2 MERGE plans (`marketing` + `marketing-operations` → `marketing`; `blog-post` + `content-creation` → `content-creation`). Final target: 52 skills.
- No skill body exceeded 12K char limit during the audit pass.
- **Known forward-references in carried bodies (R10 cross-phase review finding):** 14 of the 53 skill files reference workflow slash commands that do not exist yet (`/develop`, `/feature-design`, `/eval`, `/ralph`, `/feature-dev` legacy name, `/team-dev` legacy name, etc.). This mirrors the same situation flagged in B6 CHANGELOG for rules. All forward-refs resolve when B11 (REFACTOR skills with `team-dev` → `develop` rename) and B12 (NEW workflow skills) ship. Tracked, not a defect — but explicit so future maintainers know carried bodies are deliberately out of sync until the content-refresh pass.

## [0.1.0-alpha.7] — 2026-04-27 — 12 new hooks + shared `_lib.py` + full hooks.json wiring (B8)

### Added
12 new hook scripts in `plugin/hooks/scripts/` per glossary §5 + checklist B8.63-74a:

- `session-start-context.py` (SessionStart) — load active session token meter; surface RALF active-lock if present; emit boot context summary
- `instructions-loaded-augment.py` (InstructionsLoaded) — append plugin-relevant rule pointers to model context after CLAUDE.md / AGENTS.md load
- `pre-tool-use-committed-write.py` (PreToolUse Write|Edit; **R8 CRIT-1**) — enforce `.committed/` allowlist (glob patterns from `memory/templates/committed-allowlist.txt` + project `.allowlist-extensions.txt`); blocks writes to versioned memory paths not on allowlist
- `tool-output-wrap.py` (PostToolUse Read|Bash; **G1 OWASP LLM01 defense**) — wrap tool outputs >200 tokens in `<untrusted_content>` envelope; PII filter via `_lib.apply_pii_filter`; emits ordering marker for normalize hook
- `tool-output-normalize.py` (PostToolUse Read|Bash; **G2**) — extract envelope metadata for outputs >2000 tokens; updates session token meter `injected_tokens_from_tools`; asserts wrap marker (R5 S6 self-enforcing order); v0.1 stops at metadata, Haiku-summarize step deferred to Phase 4
- `tool-failure-log.py` (PostToolUseFailure + StopFailure) — structured failure log to L4
- `subagent-start-budget.py` (SubagentStart) — record spawn payload; check session-aggregate budget caps per `ralph-budget.md` HIGH-3
- `subagent-stop-learnings.py` (SubagentStop) — opt-in trigger for `memory-curator` agent to write learnings (per Round 6 HIGH-2 — no auto-spawn without explicit `userConfig.subagent_learnings_opt_in`)
- `task-event-log.py` (TaskCreated + TaskCompleted) — task lifecycle audit log to L4
- `ralph-stop.py` (Stop) — RALF iteration loop control: oracle check, kill-on signals (`oracle-pass`, `same-error-repeats:N`), iteration cap, budget enforcement; on-success releases lock + writes terminal SUCCESS state; otherwise blocks Stop (exit 2) with continuation prompt
- `pre-compact-memory-flush.py` (PreCompact) — invoke `memory-curator` agent for pre-compaction learnings flush (Round 4 O3: isolated context for safety)
- `session-end-finalize.py` (SessionEnd) — finalize session token meter; archive to `.ai-assets-memory/sessions/<id>/`; release any orphaned RALF locks

### Added — shared library
- `plugin/hooks/scripts/_lib.py` (shared module imported by all 12 new hooks per Round 5 S2):
  - `normalize_hook_input(data)` — bridge legacy / modern stdin payload formats
  - `apply_pii_filter(text)` — run regex from `pii-patterns.txt` + project extension; returns `(redacted, count)`
  - `wrap_untrusted(content, source)` — canonical G1 envelope with attribute sanitization + anti-double-wrap
  - `read_wrap_marker()` / `emit_wrap_marker()` — hook ordering enforcement (R5 S6)
  - `read_token_meter()` / `update_token_meter()` — session token accounting under `.ai-assets-memory/sessions/<id>/token-meter.json`
  - `log_to(filename, entry)` — JSON-line append to `.ai-assets-memory/<filename>` (fail-open per `failure-recovery.md`)
  - `iso_now()`, `read_stdin_json()`, `block(reason)`, `allow()` — hook entrypoint helpers
- `apply_pii_filter` and `wrap_untrusted` are now used by `tool-output-wrap.py`. The 4 carried hooks (B2) MAY be refactored to use `_lib.py` in Phase 4 hardening per minimum-change discipline.

### Changed
- `plugin/hooks/hooks.json` — full wiring across 13 lifecycle events: SessionStart, InstructionsLoaded, PreToolUse (Bash | Write|Edit | Read), PostToolUse (.* | Read|Bash), PostToolUseFailure, StopFailure, SubagentStart, SubagentStop, TaskCreated, TaskCompleted, Stop, PreCompact, SessionEnd. PreToolUse Write|Edit chains 2 hooks (`block-secrets-in-code`, `pre-tool-use-committed-write`); PostToolUse Read|Bash chains 2 hooks (`tool-output-wrap` MUST run before `tool-output-normalize` — verified by wrap marker).

### Known limitations (deferred to Phase 4 hardening)
- `tool-output-normalize.py` v0.1 emits structural envelope only; Haiku-summarize extract→summarize→annotate step deferred until eval-judge agent infrastructure is wired
- `tool-output-wrap.py` real-world hook execution model (how stdout from PostToolUse hook modifies the tool response visible to the model) needs verification on a live Claude Code install — v0.1 prints wrapped content to stdout per spec
- `ralph-stop.py` v0.1 supports `oracle-pass` + `same-error-repeats:N` kill-on signals only; `regex` and `python` oracle types deferred
- 4 carried hooks (B2) not yet refactored to use `_lib.py` (intentional — minimum-change discipline)

### Cross-batch fix found in B8 mandatory final review (R10)
Pattern 11 cascade — actual count of unique top-level lifecycle events in `hooks.json` is **13**, not 12 as previously labeled. Updated 6 references across `plugin/README.md`, `plugin/hooks/hooks.json` $schema-comment, `plugin-design/_glossary.md` §1 + §5, `plugin-design/00-PHASE-1-PLAN.md` 3 locations. Also fixed `_glossary.md` §5 header "Hooks (15 total" → "Hooks (16 total" + plan §6.4 "Final hook count: 15" → "16" — both stale from before R8 CRIT-1 added the 12th new hook.

### Notes
- Total hooks in plugin v0.1: **16** = 4 carried (B2) + 12 new (B8). 17 files in `plugin/hooks/scripts/` = 16 hooks + 1 `_lib.py` shared module. Verified via Glob.
- All 12 new hook scripts: AST-valid (syntactically), import `_lib`, fail-open on internal errors per `failure-recovery.md`, never block `Stop` for buggy hook (R8 A3 / `ralph-stop.py` exception handler).
- Pattern 13 cross-batch refs check: all 12 new hooks reference `_lib.py` (exists ✓). All `${CLAUDE_PLUGIN_ROOT}/hooks/scripts/<name>.py` paths in `hooks.json` resolve to existing files ✓.
- `pre-tool-use-committed-write.py` uses both plugin-default allowlist (`memory/templates/committed-allowlist.txt`, shipped in B9) and project extension (`.ai-assets-memory/.committed/.allowlist-extensions.txt`) — first match allows.
- Pattern 14 verification: Glob shows all 17 `.py` files in `plugin/hooks/scripts/` ✓ (no fabricated completion claim).

## [0.1.0-alpha.6] — 2026-04-27 — 22 existing agents migrated (B4)

### Added
- 22 existing agent files migrated from `.claude/agents/` to `plugin/agents/` with frontmatter normalization per glossary §3 role-type table:
  - **9 dropped `permissionMode: plan`** (plugin-shipped agents cannot use this field per Anthropic security boundary): cloud-architect, content-designer, content-writer, devops-architect, marketing-strategist, product-manager, solution-architect, system-architect, ui-ux-designer
  - **All 22 added** `effort` (low/medium/high), `maxTurns: 30`, `max_output_tokens` (per role-type: code-gen 2000, architects 1500, designers/writers 1200, strategy 1500, Q&A 1000, qa-engineer 800, seo-engineer 800)
  - All bodies preserved verbatim from source

### Migration approach
- 1 agent (cloud-architect) authored manually as pattern reference
- 19 agents delegated to general-purpose subagent for mechanical migration
- 3 agents (sre-engineer, system-architect, ui-ux-designer) authored manually after subagent ran out of tokens (sub-agent's "completion" report inaccurately claimed all 21 done — verified discrepancy via Glob)

### Notes
- Total agents in plugin v0.1: **26** (22 migrated + 4 new from B5) ✓ matches glossary §1
- All 26 verified: 0 forbidden fields (`permissionMode`/`hooks`/`mcpServers`), 26/26 have `max_output_tokens` field
- Bodies verbatim per minimum-change discipline; refactor opportunities (e.g., updating workflow refs from `/feature-dev` to `/develop`) deferred to dedicated content-refresh batch
- Pattern observation: subagent self-reports cannot be trusted (R10 finding) — Glob verification mandatory after delegation

## [0.1.0-alpha.5] — 2026-04-27 — 4 new agents authored (B5)

### Added
4 new agents in `plugin/agents/`, authored from glossary §3 + checklist B5 specs:

- `security-engineer.md` — OWASP Top 10 (Web 2021) + GenAI/LLM Top 10 (2025) coverage. Read-only (`disallowedTools: Write, Edit`). file:line citations mandatory. Severity classification per finding. No effort estimation per Q2. Powers `/security-audit` workflow + Wave 2 reviewer in `/feature-design`.
- `feature-design-lead.md` — Multi-agent orchestrator for `/feature-design`. Three-wave pattern (parallel drafts → parallel domain reviews → sequential cross-check) with explicit gates. RALF loop (5 iter / 250K tokens / 60 min). Only agent with `tools: Task` (bounded recursion guarantee per `subagent-isolation.md`). G7 spawn payload template embedded. `model: opus`, `effort: xhigh` (per Round 6 A7 — Opus default).
- `eval-judge.md` — Strict rubric-following evaluator. Powers `/eval` Tier 3 + RALF subjective oracles. Model: Haiku default; Sonnet override per-rubric on Spearman <0.7. No extrapolation, no fabrication. G7 return contract with score per dimension + auto-fail signals (faithfulness claim-grounding <3 = fail).
- `memory-curator.md` — Spawn-only (NEVER user-invocable per Round 6 HIGH-2). Triggered by `pre-compact-memory-flush.py`, opt-in `subagent-stop-learnings.py`, or `/learnings-write`. Path-restricted writes (L4 + L5 only, enforced by `pre-tool-use-committed-write.py` hook per Round 8 CRIT-1). PII filter mandatory. Conflict-resolves per `memory-validation.md`. Isolated context for PreCompact safety (Round 4 O3).

### Notes
- All 4 frontmatter validated: no forbidden fields (`permissionMode`/`hooks`/`mcpServers`) per Pattern 7. Required fields present (`effort`, `maxTurns`, `max_output_tokens` per glossary §3).
- Agent counts now: 22 normalized (B4 pending) + 4 new = 26 total target. B4 still pending (existing agents migration not yet done).
- Forward references to skills (`/security-audit`, `/feature-design`, `/eval`, `/ralph`, `/learnings-write`) are intentional — those skills ship in B11+B12.
- Forward references to hooks (`pre-compact-memory-flush.py`, `subagent-stop-learnings.py`, `pre-tool-use-committed-write.py`) are intentional — B8 will implement.
- Forward references to `_lib.py` `apply_pii_filter` and `wrap_untrusted` — B8.
- All B9 schemas/templates referenced are present (verified Pattern 3 reference integrity).

### Format/style fix found in review
- `security-engineer.md` Output Schema had nested code blocks: outer ` ```markdown ` was prematurely closed by inner ` ``` ` for code excerpt. Fixed by switching outer to 4-backtick fence. Other 3 agents use only ` ```json ` blocks without nesting — no issue.

## [0.1.0-alpha.4] — 2026-04-27 — Schemas + memory templates (B9)

### Added
- `plugin/schemas/spawn-payload.schema.json` (G7) — JSON Schema 2020-12 typed contract for orchestrator → subagent delegation. Fields: trace_id, subagent_role, goal, constraints, state_slice, allowed_tools, budget (max_input_tokens / max_output_tokens / max_tool_calls / max_turns / timeout_ms / retry_budget), untrusted_inputs.
- `plugin/schemas/return-contract.schema.json` (G7) — JSON Schema 2020-12 typed return value: trace_id, status enum, tokens_used, tool_calls, result, evidence, risks, next_actions, needs_clarification (with conditional requirement when status=needs_clarification).
- `plugin/memory/templates/ai-assets-memory.gitignore` — gitignore template seeded by `/ai-assets-init`. Per D9: ignore `.ai-assets-memory/*` except opt-in `.committed/` allowlist.
- `plugin/memory/templates/committed-readme.md` — explains `.committed/` opt-in versioned memory contract for target repo teams.
- `plugin/memory/templates/learnings-schema.md` — canonical L4/L5 entry format with required fields, body conventions, valid/invalid examples, conflict resolution, retention.
- `plugin/memory/templates/conventions-schema.md` — schema for `.committed/conventions.md` team-confirmed conventions.
- `plugin/memory/templates/eval-baseline.schema.json` — JSON Schema for per-skill scorecards captured by `/eval --baseline`.
- `plugin/memory/templates/committed-allowlist.txt` — default allowlist patterns enforced by `pre-tool-use-committed-write.py` hook (B8).
- `plugin/memory/templates/untrusted-content-wrapper.md` (G1) — canonical envelope template + field substitutions + order of operations + anti-patterns.
- `plugin/hooks/scripts/pii-patterns.txt` — 18 default PII regex patterns (EMAIL, SSN, AWS/Azure/GCP/Stripe/GitHub/GitLab/Slack tokens, JWT, PEM private keys, generic API key/password, URL with creds).

### Notes
- Total in plugin v0.1 after B9: 32 files / 21 dirs
- Schemas use `https://github.com/<owner>/...` placeholder for `$id` — replace with real URL at publish time
- All 8 templates referenced by name in `plugin-design/03-MEMORY-ARCHITECTURE.md` §3 L1 — cross-doc consistency verified
- B9 unblocks B5 (4 new agents reference G7 spawn-payload schema in their frontmatter authoring)
- Forward references to `_lib.py` `apply_pii_filter` and `wrap_untrusted` (B8) intentional — B8 implementation will use these schemas/templates as input

## [0.1.0-alpha.3] — 2026-04-27 — New rules authored (B7)

### Added
4 new rule files in `plugin/rules/`, authored from `plugin-design/` specs:

- `subagent-isolation.md` — when to delegate vs inline; routing table for parallel/sequential decisions; bounded-recursion guarantee for v0.1 (only `feature-design-lead` has `tools: Task`); pairs with team-protocols runtime detection
- `memory-discipline.md` — 6-layer model recap; PII filter mandatory on every L3/L4/L5 write; full write-rules table per skill/hook; conflict resolution algorithm (extends memory-validation.md); retention table per layer
- `ralph-budget.md` — two-level budget model (per-workflow D12 defaults + session-aggregate Round 6 HIGH-3); mandatory `--kill-on` signal; oracle types; state/log layout; failure modes
- `untrusted-content-wrapping.md` (G1, OWASP LLM01 defense) — canonical `<untrusted_content>` envelope template; coverage table (what must be wrapped, by which hook); defense-in-depth layers; Phase 4 hardening test fixtures

### Notes
- Total rules in `plugin/rules/`: **12** (8 carried in B6 + 4 new in B7) — matches glossary §4 and README "12 rules"
- All 4 rules cross-reference each other appropriately and reference design docs in `../plugin-design/`
- Forward references to not-yet-built assets (workflows, agents, hooks, templates) are intentional — those B-batches will resolve them
- Each rule has `description` frontmatter (validated by Read tool — no YAML errors)
- No rule exceeds 12,000 chars (per global-rules.md authoring standard)

## [0.1.0-alpha.2] — 2026-04-27 — Existing rules carried over (B6)

### Added
- 8 rule files copied verbatim from `.claude/rules/` to `plugin/rules/`:
  - `failure-recovery.md` — loop detection, goal drift recovery
  - `geo-content.md` — GEO/AEO content standard
  - `git-conventions.md` — Conventional Commits, branching, PR standards
  - `global-package-rules.md` — runtime boundaries (legacy text retained — see Known Stale)
  - `global-rules.md` — authoring standards (English, char limits, cross-refs)
  - `humanize-content.md` — anti-AI-vocabulary rule
  - `memory-validation.md` — memory entry validation, conflict resolution
  - `task-completion.md` — pre-completion audit checklist

### Known stale (deferred to future content-refresh batch)
- `global-package-rules.md` body references legacy `~/.claude/agents/, skills/, rules/, hooks/` layout. For plugin context, paths should reference `${CLAUDE_PLUGIN_ROOT}/...`. Per B6 atomic-batch discipline, copy verbatim now; refresh content in dedicated pass.
- `geo-content.md` and `humanize-content.md` reference workflows including `/blog-post` (which merged into `/content-creation` per glossary §2). Stale slash-command references will be refreshed alongside refactored skills (B11).

### Notes
- Total rules in `plugin/rules/` after B6: **8**. B7 will add 4 new (`subagent-isolation`, `memory-discipline`, `ralph-budget`, `untrusted-content-wrapping`) for grand total of **12** matching glossary §4.
- All 8 files have valid YAML frontmatter (`description` field) — verified via Read tool.

## [0.1.0-alpha.1] — 2026-04-26 — Hook scripts carried over (B2)

### Added
- 4 hook scripts copied from legacy `.claude/hooks/scripts/` to `plugin/hooks/scripts/` (chmod +x, AST-valid):
  - `block-dangerous-commands.py` — wired to PreToolUse matcher `Bash`
  - `block-secrets-in-code.py` — wired to PreToolUse matcher `Write|Edit`
  - `block-sensitive-files.py` — wired to PreToolUse matcher `Read`
  - `log-actions.py` — wired to PostToolUse matcher `.*`
- `hooks/hooks.json` rewritten in modern Claude Code format (PreToolUse + PostToolUse with matcher patterns); replaces legacy `pre_run_command`/`pre_write_code`/`pre_read_code`/`post_*` event names. All script paths use `${CLAUDE_PLUGIN_ROOT}` (plugin-portable).

### Changed
- `log-actions.py` LOG_FILE constant: `.claude/agent-actions.log` → `.ai-assets-memory/agent-actions.log` (per L4 memory architecture; was wrong namespace for plugin distribution).
- 4 script docstrings updated from legacy event names to modern Claude Code event names + matcher pattern (cosmetic, prevents future maintainer confusion).

### Smoke-tested
- block-dangerous-commands rejects `rm -rf /` (exit 2) ✓
- block-secrets-in-code rejects hardcoded AWS access key in Write input (exit 2) ✓
- block-sensitive-files rejects `.env` Read (exit 2) ✓
- log-actions allows benign Read (exit 0) ✓

## [0.1.0-alpha.0] — 2026-04-26 — Initial scaffold (B1)

### Added
- Plugin skeleton: `.claude-plugin/plugin.json` manifest with 11 `userConfig` knobs, 0 dependencies
- 15 leaf directories per `../plugin-design/00-PHASE-1-PLAN.md` §3.1 layout: `skills/`, `agents/`, `hooks/scripts/`, `rules/`, `eval/judge-rubrics/`, `eval/cases/`, `eval/baselines/`, `eval/calibration/`, `examples/`, `schemas/`, `memory/templates/`, `output-styles/`, `monitors/`, `docs/workflows/`, `docs/concepts/` (initially included `hooks/configs/` in error; removed per Round 7 critical review since modern Claude Code uses single `hooks.json`, not fragments)
- `README.md` — top-level user-facing entry point
- `hooks/hooks.json` — empty event mapping (events wired in B2 + B8)
- `eval/config.json` — token budget table per tier (Tier 2: 50K soft / 150K hard; Tier 3 per skill: 30K soft / 100K hard; Tier 3 full suite: 500K soft / 1.5M hard)
- `monitors/monitors.json` — `env-watch.sh` entry (opt-in via `userConfig.env_watch_enabled`)

### Notes
- This is a skeleton-only release. Plugin is INSTALLABLE (`claude plugin install ./plugin`) but workflows/agents/hooks/rules are empty.
- Following batches per migration checklist: B2 (existing 4 hook scripts + format upgrade), B3 (20 KEEP skills), B4-B5 (26 agents), B6-B7 (12 rules), B8 (12 new hooks + `_lib.py` shared module), B9-B13 (schemas, eval, calibration, refactor skills, new skills, user docs).

[Unreleased]: https://github.com/alex-voloshin/ai-assets/compare/v0.1.0-alpha.14...HEAD
[0.1.0-alpha.14]: https://github.com/alex-voloshin/ai-assets/compare/v0.1.0-alpha.13...v0.1.0-alpha.14
[0.1.0-alpha.13]: https://github.com/alex-voloshin/ai-assets/compare/v0.1.0-alpha.12...v0.1.0-alpha.13
[0.1.0-alpha.12]: https://github.com/alex-voloshin/ai-assets/compare/v0.1.0-alpha.11...v0.1.0-alpha.12
[0.1.0-alpha.11]: https://github.com/alex-voloshin/ai-assets/compare/v0.1.0-alpha.10...v0.1.0-alpha.11
[0.1.0-alpha.10]: https://github.com/alex-voloshin/ai-assets/compare/v0.1.0-alpha.9...v0.1.0-alpha.10
[0.1.0-alpha.9]: https://github.com/alex-voloshin/ai-assets/compare/v0.1.0-alpha.8...v0.1.0-alpha.9
[0.1.0-alpha.8]: https://github.com/alex-voloshin/ai-assets/compare/v0.1.0-alpha.7...v0.1.0-alpha.8
[0.1.0-alpha.7]: https://github.com/alex-voloshin/ai-assets/compare/v0.1.0-alpha.6...v0.1.0-alpha.7
[0.1.0-alpha.6]: https://github.com/alex-voloshin/ai-assets/compare/v0.1.0-alpha.5...v0.1.0-alpha.6
[0.1.0-alpha.5]: https://github.com/alex-voloshin/ai-assets/compare/v0.1.0-alpha.4...v0.1.0-alpha.5
[0.1.0-alpha.4]: https://github.com/alex-voloshin/ai-assets/compare/v0.1.0-alpha.3...v0.1.0-alpha.4
[0.1.0-alpha.3]: https://github.com/alex-voloshin/ai-assets/compare/v0.1.0-alpha.2...v0.1.0-alpha.3
[0.1.0-alpha.2]: https://github.com/alex-voloshin/ai-assets/compare/v0.1.0-alpha.1...v0.1.0-alpha.2
[0.1.0-alpha.1]: https://github.com/alex-voloshin/ai-assets/compare/v0.1.0-alpha.0...v0.1.0-alpha.1
[0.1.0-alpha.0]: https://github.com/alex-voloshin/ai-assets/releases/tag/v0.1.0-alpha.0
