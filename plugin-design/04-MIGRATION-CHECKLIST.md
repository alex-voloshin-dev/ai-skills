# Phase 2 Migration Checklist — `.claude/` → `plugin/`

> **Purpose:** Mechanically-followable, dry-run-validated plan for migrating every asset from the legacy `.claude/` tree into the new `plugin/` tree per Phase 1 design.
> **Scope:** This document is a checklist, not new design. All design decisions live in `00-PHASE-1-PLAN.md` and follow-ups; this doc just operationalises them.
> **Date:** 2026-04-26
> **Pre-requisites:** Phase 1 design complete (00-PHASE-1-PLAN.md, 01-WORKFLOW-SPECS.md, 02-EVAL-FRAMEWORK.md, 03-MEMORY-ARCHITECTURE.md, 05-CONTEXT-ENGINEERING-GAP-ANALYSIS.md). Legacy `.claude/` continues to function untouched throughout migration (per D4).

---

## How to Use This Checklist

1. Read each section in order.
2. Each numbered item is one atomic change to one file or one small group of files.
3. After each batch (B1-B12 below), run the validation commands listed at end of the batch.
4. Track progress: copy this checklist into `.ai-assets-memory/.committed/migration-progress.md` once `/ai-assets-init` exists; until then, track in a personal scratchpad.
5. On any validation failure: STOP, fix, re-validate, continue. Do not skip ahead.
6. The legacy `.claude/`, `.codex/`, `.windsurf/`, `.agents/` directories MUST remain untouched throughout Phase 2 — they continue serving the user's existing workflows in parallel.

---

## Pre-Migration Prerequisites

Before any file write:

- [ ] **PR0.** Confirm working directory is `C:\Users\avav2\dev\code\ai-assets\` (the same repo as legacy assets).
- [ ] **PR1.** Confirm `plugin/` directory does NOT yet exist (idempotency check). If it does, abort and ask user.
- [ ] **PR2.** Confirm Phase 1 design docs exist and are unchanged (compare `00-PHASE-1-PLAN.md` mtime against your last review checkpoint).
- [ ] **PR3.** Create empty `.ai-assets-memory/` in the workspace root for plugin self-eval (NOT the user's target repo's memory; this is for testing the plugin against itself). Add to `.gitignore`.
- [ ] **PR4.** Verify `python3` available in shell (hooks need it) and `claude` CLI is installed (for `plugin validate`).

---

## Batch B1 — Plugin Skeleton + Manifest

**Goal:** Create directory structure + `plugin.json` + `README.md`. After this batch, `claude plugin install ./plugin` should succeed (with empty plugin) and `/plugin-doctor` (once written) can run.

### Files to create

1. **B1.1.** `plugin/` (root directory)
2. **B1.2.** `plugin/.claude-plugin/plugin.json` — copy verbatim from `00-PHASE-1-PLAN.md` §3.2 (the full `userConfig` block, `outputStyles`, `monitors`, `dependencies: []`, `keywords`, etc.). Replace `<author-name>`, `<author-email>`, `<owner>` with the actual values the user provides at publish time (leave placeholders for now).
3. **B1.3.** Create empty directories matching `00-PHASE-1-PLAN.md` §3.1 layout:
   ```
   plugin/skills/
   plugin/agents/
   plugin/hooks/scripts/
   plugin/rules/
   plugin/eval/judge-rubrics/
   plugin/eval/cases/
   plugin/eval/baselines/
   plugin/eval/calibration/
   plugin/examples/
   plugin/schemas/
   plugin/memory/templates/
   plugin/output-styles/
   plugin/monitors/
   plugin/docs/workflows/
   plugin/docs/concepts/
   ```
4. **B1.4.** `plugin/README.md` — short top-level README. Sections: What this plugin does (1 paragraph), Install (one-liner `claude plugin install <git-url>`), First run (`/ai-assets-init` then any workflow), Where to learn more (link to `plugin/docs/getting-started.md`).
5. **B1.5.** `plugin/CHANGELOG.md` — Keep a Changelog format. Initial entry: `## [0.1.0-alpha] — 2026-04-26 — Initial scaffold`.
6. **B1.6.** `plugin/hooks/hooks.json` — empty event mapping `{ "hooks": {} }` (events filled in B6).
7. **B1.7.** `plugin/eval/config.json` — token-budget table from `02-EVAL-FRAMEWORK.md` §9 + Q4 decision.
8. **B1.8.** `plugin/monitors/monitors.json` — single entry `env-watch.sh` per `00-PHASE-1-PLAN.md` §1.8; opt-in via `userConfig.env_watch_enabled`.

### Validation B1

- [ ] `claude plugin validate ./plugin` succeeds (or warns only about empty `skills/`/`agents/` — that's expected pre-B2).
- [ ] `cat plugin/.claude-plugin/plugin.json | jq .name` returns `"ai-assets"`.
- [ ] All 15 leaf directories exist (was 16 before removing unused `hooks/configs/` per Round 7 Issue C).

---

## Batch B2 — Existing Hook Scripts (Carry-over, Format Update)

**Goal:** Move 4 existing hook scripts from `.claude/hooks/scripts/` to `plugin/hooks/scripts/` and **update the hook config format** from the legacy event names (`post_write_code`, `post_run_command`, `post_read_code`, `post_mcp_tool_use`) to modern Claude Code event names (`PostToolUse`, `PreToolUse`, etc.).

> **Critical observation:** the legacy `.claude/hooks/configs/*.json` use old event names that will not fire on modern Claude Code. The Python scripts themselves are fine — only the configs need rewriting.

### Files to copy (no content change)

9. **B2.1.** Copy `.claude/hooks/scripts/block-dangerous-commands.py` → `plugin/hooks/scripts/block-dangerous-commands.py`.
10. **B2.2.** Copy `.claude/hooks/scripts/block-secrets-in-code.py` → `plugin/hooks/scripts/block-secrets-in-code.py`.
11. **B2.3.** Copy `.claude/hooks/scripts/block-sensitive-files.py` → `plugin/hooks/scripts/block-sensitive-files.py`.
12. **B2.4.** Copy `.claude/hooks/scripts/log-actions.py` → `plugin/hooks/scripts/log-actions.py`.
13. **B2.5.** `chmod +x` on all 4 (will be enforced by `/plugin-doctor` later).

### Hook wiring in `plugin/hooks/hooks.json`

14. **B2.6.** Add wiring (replaces legacy format):
   ```json
   {
     "hooks": {
       "PreToolUse": [
         {"matcher": "Bash",        "hooks": [{"type": "command", "command": "${CLAUDE_PLUGIN_ROOT}/hooks/scripts/block-dangerous-commands.py"}]},
         {"matcher": "Write|Edit",  "hooks": [{"type": "command", "command": "${CLAUDE_PLUGIN_ROOT}/hooks/scripts/block-secrets-in-code.py"}]},
         {"matcher": "Read",        "hooks": [{"type": "command", "command": "${CLAUDE_PLUGIN_ROOT}/hooks/scripts/block-sensitive-files.py"}]}
       ],
       "PostToolUse": [
         {"matcher": ".*",          "hooks": [{"type": "command", "command": "${CLAUDE_PLUGIN_ROOT}/hooks/scripts/log-actions.py"}]}
       ]
     }
   }
   ```

### Validation B2

- [ ] `python3 -c "import ast; ast.parse(open('plugin/hooks/scripts/block-dangerous-commands.py').read())"` succeeds (and same for the other 3 scripts).
- [ ] `cat plugin/hooks/hooks.json | jq '.hooks | keys'` returns `["PostToolUse", "PreToolUse"]`.
- [ ] Smoke test: `echo '{"tool_name":"Bash","tool_input":{"command":"rm -rf /"}}' | python3 plugin/hooks/scripts/block-dangerous-commands.py` exits 2 with reason on stdout.

---

## Batch B3 — KEEP Skills (20 skills, file copy + frontmatter normalize)

**Goal:** Copy each KEEP skill verbatim, then audit frontmatter for the H5 contract (`Use when …, or when user mentions "<keyword>"`).

### Skills list (per `00-PHASE-1-PLAN.md` §2.1)

Per skill, the action is the same: copy directory, normalize frontmatter, no body changes.

| # | Skill | Source | Destination | Frontmatter changes |
|---|---|---|---|---|
| 15 | humanizer | `.claude/skills/humanizer/` | `plugin/skills/humanizer/` | None (description already follows H5) |
| 16 | geo-writer | `.claude/skills/geo-writer/` | `plugin/skills/geo-writer/` | None |
| 17 | code-review | `.claude/skills/code-review/` | `plugin/skills/code-review/` | Add explicit `Use when` triggers if missing |
| 18 | docs | `.claude/skills/docs/` | `plugin/skills/docs/` | Audit for H5 |
| 19 | pre-commit | `.claude/skills/pre-commit/` | `plugin/skills/pre-commit/` | Confirm `disable-model-invocation: true` preserved |
| 20 | architecture | `.claude/skills/architecture/` | `plugin/skills/architecture/` | Audit for H5 |
| 21 | prompt-engineering | `.claude/skills/prompt-engineering/` | `plugin/skills/prompt-engineering/` | Audit for H5 |
| 22 | context-engineering | `.claude/skills/context-engineering/` | `plugin/skills/context-engineering/` | Confirm extensive description preserved |
| 23 | qa | `.claude/skills/qa/` | `plugin/skills/qa/` | Audit for H5 |
| 24 | seo-review | `.claude/skills/seo-review/` | `plugin/skills/seo-review/` | Audit for H5 |
| 25 | security-scan | `.claude/skills/security-scan/` | `plugin/skills/security-scan/` | Audit for H5 + add OWASP reference per G3 |
| 26 | analyze-local | `.claude/skills/analyze-local/` | `plugin/skills/analyze-local/` | Audit for H5; preserve `allowed-tools` field |
| 27 | analyze-prod | `.claude/skills/analyze-prod/` | `plugin/skills/analyze-prod/` | Audit for H5 |
| 28 | analyze | `.claude/skills/analyze/` | `plugin/skills/analyze/` | Audit for H5 |
| 29 | cloud-platforms | `.claude/skills/cloud-platforms/` | `plugin/skills/cloud-platforms/` | Audit for H5 (knowledge skill) |
| 30 | deployment-procedures | `.claude/skills/deployment-procedures/` | `plugin/skills/deployment-procedures/` | Audit for H5 |
| 31 | social-media-manager | `.claude/skills/social-media-manager/` | `plugin/skills/social-media-manager/` | Confirm `marketing/MARKETING.md` runtime-read pattern preserved (operations/data split per D2) |
| 32 | worktree-isolation | `.claude/skills/worktree-isolation/` | `plugin/skills/worktree-isolation/` | Audit for H5 |
| 33 | test-strategy | `.claude/skills/test-strategy/` | `plugin/skills/test-strategy/` | Audit for H5 |
| 34 | ui-ux-design | `.claude/skills/ui-ux-design/` | `plugin/skills/ui-ux-design/` | Audit for H5 |

### Per-skill audit template

For each skill, after copy, verify SKILL.md frontmatter:

- `name` — present, lowercase + hyphens, ≤64 chars
- `description` — present, ≤1024 chars, third person, contains "Use when …" trigger pattern (H5)
- If user-invocable: `user-invocable: true` OR `context: fork`
- If non-invocable utility: `disable-model-invocation: true` (e.g., `pre-commit`)
- Char limit on body: ≤12K chars (per project rule); if over, move depth to companion `.md` files in same dir

### Validation B3

- [ ] `ls plugin/skills/ | wc -l` returns 20.
- [ ] For each skill: `head -10 plugin/skills/<name>/SKILL.md` shows valid frontmatter ending with `---`.
- [ ] Pick one skill at random, run `claude plugin validate ./plugin` — should pass.

---

## Batch B4 — Existing Agents (22, frontmatter normalize)

**Goal:** Copy 22 agents, drop forbidden `permissionMode` from 9, add `effort` + `maxTurns` + `max_output_tokens` everywhere.

### Drop `permissionMode` from these 9 agents

For each, edit frontmatter: remove the line `permissionMode: plan`. The intent (read-only) is preserved by existing `disallowedTools: Write, Edit` (or stricter where present).

| # | Agent | Source | Existing `disallowedTools` | Action |
|---|---|---|---|---|
| 35 | cloud-architect | `.claude/agents/cloud-architect.md` | `Write, Edit` | Remove `permissionMode: plan`, copy to `plugin/agents/` |
| 36 | content-designer | `.claude/agents/content-designer.md` | `Bash, Write, Edit` | Same |
| 37 | content-writer | `.claude/agents/content-writer.md` | (verify) | Same; if missing `disallowedTools: Write, Edit`, ADD it before removing `permissionMode` |
| 38 | devops-architect | `.claude/agents/devops-architect.md` | (verify) | Same |
| 39 | marketing-strategist | `.claude/agents/marketing-strategist.md` | (verify) | Same |
| 40 | product-manager | `.claude/agents/product-manager.md` | (verify) | Same |
| 41 | solution-architect | `.claude/agents/solution-architect.md` | (verify) | Same |
| 42 | system-architect | `.claude/agents/system-architect.md` | (verify) | Same |
| 43 | ui-ux-designer | `.claude/agents/ui-ux-designer.md` | `Bash, Write, Edit` | Same |

### Before / after example (ui-ux-designer.md)

Before:
```yaml
---
name: ui-ux-designer
description: UI/UX Design — user research, personas, …
tools: Read, Grep, Glob
model: inherit
disallowedTools: Bash, Write, Edit
permissionMode: plan
skills:
  - ui-ux-design
  - content-creation
---
```

After:
```yaml
---
name: ui-ux-designer
description: UI/UX Design — user research, personas, …
tools: Read, Grep, Glob
model: inherit
effort: medium
maxTurns: 30
max_output_tokens: 1500
disallowedTools: Bash, Write, Edit
skills:
  - ui-ux-design
  - content-creation
---
```

### Carry over the other 13 agents unchanged (just add 3 fields)

For each of: `data-engineer`, `db-engineer`, `devops-engineer`, `frontend-engineer`, `java-engineer`, `ml-engineer`, `mobile-engineer`, `prompt-engineer`, `python-engineer`, `qa-engineer`, `seo-engineer`, `software-engineer`, `sre-engineer`:

| # | Action |
|---|---|
| 44 | Copy file from `.claude/agents/<name>.md` to `plugin/agents/<name>.md`. |
| 45 | Add `effort: medium` (or `high` for code-gen roles like java-engineer/python-engineer/frontend-engineer; `low` for review-only roles). |
| 46 | Add `maxTurns: 30`. |
| 47 | Add `max_output_tokens` per the role-type table in `00-PHASE-1-PLAN.md` §2.2 (1500-2500 for code-gen engineers; 800-1500 for solution-architect; 500-1000 for prompt-engineer). |

### `max_output_tokens` per role (authoritative)

| Role | `max_output_tokens` |
|---|---|
| Code-generation (java-engineer, python-engineer, frontend-engineer, mobile-engineer, db-engineer, ml-engineer, data-engineer, devops-engineer, sre-engineer) | 2000 |
| Architects (cloud-architect, devops-architect, solution-architect, system-architect) | 1500 |
| Designers + writers (ui-ux-designer, content-designer, content-writer) | 1200 |
| Reviewers (qa-engineer, seo-engineer) | 800 |
| Strategy (product-manager, marketing-strategist) | 1500 |
| Knowledge / Q&A (prompt-engineer, software-engineer general) | 1000 |

### Validation B4

- [ ] `grep -l "permissionMode" plugin/agents/*.md` returns NOTHING (verifies all 9 cleaned).
- [ ] `grep -l "max_output_tokens" plugin/agents/*.md | wc -l` returns 22.
- [ ] `claude plugin validate ./plugin` passes (no agent frontmatter errors).

---

## Batch B5 — New Agents (4)

**Goal:** Author 4 new agents per `00-PHASE-1-PLAN.md` §2.2 spec. Each is a fresh file.

48. **B5.1.** `plugin/agents/security-engineer.md`
    - Description: per §2.2 "Threat modelling, dependency CVE checks, secret-handling, authn/authz patterns, OWASP GenAI/LLM Top 10 (2025) baseline … OWASP Web Top 10 for code-level review" + H5 trigger pattern
    - `model: sonnet`, `effort: high`, `maxTurns: 30`, `max_output_tokens: 1500`
    - `tools: Read, Grep, Glob, Bash`, `disallowedTools: Write, Edit`
    - Body: persona, hard rules (apply OWASP checklists, no fabrication, file-line citations for every finding), output schema (severity table per finding)

49. **B5.2.** `plugin/agents/feature-design-lead.md`
    - Per §2.2 "Orchestrates multi-role design pack assembly … Spawns 6-10 subagents in waves"
    - `model: opus`, `effort: high`, `maxTurns: 50`, `max_output_tokens: 1200` (lead writes briefs, not code)
    - `tools: Task` (spawn-only; no direct write/edit), `disallowedTools: Write, Edit, Bash`
    - Body: orchestration protocol (Wave 1/2/3 from `01-WORKFLOW-SPECS.md` `/feature-design`), structured spawn payload (G7), eval-judge integration

50. **B5.3.** `plugin/agents/eval-judge.md`
    - Per §2.2 "Grades skill/agent outputs against rubrics …"
    - `model: haiku` (Sonnet override per-rubric per `02-EVAL-FRAMEWORK.md` §4)
    - `effort: medium`, `maxTurns: 5`, `max_output_tokens: 600`
    - `tools: Read, Grep, Glob`, `disallowedTools: Write, Edit, Bash`
    - Body: rubric-following protocol, structured score output, no extrapolation beyond rubric

51. **B5.4.** `plugin/agents/memory-curator.md`
    - Per §2.2 "Reviews session output (when triggered) and writes durable learnings to .ai-assets-memory/learnings.md …"
    - `model: haiku`, `effort: low`, `maxTurns: 10`, `max_output_tokens: 800`
    - `tools: Read, Write` — write paths constrained at runtime by hook guard (NOT by frontmatter, since plugin agents can't have permissionMode). The constraint: `pre-tool-use-committed-write.py` (PreToolUse on Write|Edit) checks if writes target outside `.ai-assets-memory/*`; if yes, blocks with exit 2.
    - **Operational contract (Round 6 HIGH-2):** memory-curator is **spawn-only**, NEVER user-invocable (no `user-invocable` frontmatter). Spawn payload constructed by `pre-compact-memory-flush.py` and `subagent-stop-learnings.py` with explicit fields:
      - `goal`: "extract durable learnings from session" or "review subagent output for patterns"
      - `state_slice`: `.ai-assets-memory/sessions/<id>/` files (read-only)
      - `allowed_tools`: ["Read", "Write"] with implicit hook-enforced path restriction
      - `budget`: `{max_input_tokens: 5000, max_output_tokens: 800, max_tool_calls: 10}`
    - Rule references: must follow `memory-discipline.md` (G1 via untrusted-content-wrapping when reading session state; PII filter on every write)
    - Body: dedup protocol, schema for learnings entry (per `03-MEMORY-ARCHITECTURE.md` §3.4 L4 schema), structured return contract per G7

### Validation B5

- [ ] `ls plugin/agents/*.md | wc -l` returns 26.
- [ ] All 4 new agents have valid frontmatter (no forbidden fields per `00-PHASE-1-PLAN.md` §1.1).

---

## Batch B6 — Existing Rules (8, file copy)

**Goal:** Carry over all 8 existing rules unchanged.

| # | Rule | Source | Destination |
|---|---|---|---|
| 52 | failure-recovery.md | `.claude/rules/failure-recovery.md` | `plugin/rules/failure-recovery.md` |
| 53 | geo-content.md | `.claude/rules/geo-content.md` | `plugin/rules/geo-content.md` |
| 54 | git-conventions.md | `.claude/rules/git-conventions.md` | `plugin/rules/git-conventions.md` |
| 55 | global-package-rules.md | `.claude/rules/global-package-rules.md` | `plugin/rules/global-package-rules.md` (rename to `global-rules.md` if needed for plugin context) |
| 56 | global-rules.md | `.claude/rules/global-rules.md` | `plugin/rules/global-rules.md` (merge with above if both exist) |
| 57 | humanize-content.md | `.claude/rules/humanize-content.md` | `plugin/rules/humanize-content.md` |
| 58 | memory-validation.md | `.claude/rules/memory-validation.md` | `plugin/rules/memory-validation.md` |
| 59 | task-completion.md | `.claude/rules/task-completion.md` | `plugin/rules/task-completion.md` |

### Validation B6

- [ ] `ls plugin/rules/*.md | wc -l` returns 8 (or 7 if global-package-rules.md and global-rules.md were merged).
- [ ] Each file has plain Markdown content, no frontmatter required (per existing convention).

---

## Batch B7 — New Rules (4)

**Goal:** Author 4 new rules per `00-PHASE-1-PLAN.md` §2.3.

60. **B7.1.** `plugin/rules/subagent-isolation.md` — per `00-PHASE-1-PLAN.md` §3.7 routing rules + when to delegate vs. inline + parallel-vs-sequential rule.
61. **B7.2.** `plugin/rules/memory-discipline.md` — per `00-PHASE-1-PLAN.md` §3.4 + `03-MEMORY-ARCHITECTURE.md` §4 (which skill writes to which layer); centralized review through memory-curator; PII filter mandatory.
62. **B7.3.** `plugin/rules/ralph-budget.md` — per D12: 10 iter / 200K tokens / 2 h defaults; mandatory `--kill-on`; per-workflow overrides; budget enforcement by `ralph-stop.py`.
63. **B7.4.** `plugin/rules/untrusted-content-wrapping.md` (G1) — per `00-PHASE-1-PLAN.md` §2.3 + `03-MEMORY-ARCHITECTURE.md` §3 L2 read section; canonical `<untrusted_content>` wrapper template; defends OWASP LLM01.

### Validation B7

- [ ] `ls plugin/rules/*.md | wc -l` returns 12.
- [ ] No rule file exceeds 12,000 chars (per project rule).

---

## Batch B8 — New Hooks (11 scripts)

**Goal:** Author 11 new hook scripts + extend `plugin/hooks/hooks.json` wiring per `00-PHASE-1-PLAN.md` §2.4.

### Shared helper module (per Round 5 S2)

64a. **B8.0.** `plugin/hooks/scripts/_lib.py` — shared module with helpers used by all hook scripts. Functions:
- `normalize_hook_input()` — bridges legacy / modern stdin payload formats
- `apply_pii_filter(text)` — runs PII regex filter from `pii-patterns.txt`; returns redacted text + count
- `wrap_untrusted(content, source, ts)` — produces canonical `<untrusted_content>` envelope (G1 wrapper template)
- `read_wrap_marker()` — reads marker emitted by tool-output-wrap.py for ordering enforcement (S6)
- `emit_wrap_marker()` — emits marker for downstream hooks to assert
- `read_token_meter()` / `update_token_meter()` — increment session token counter
- `log_to(filename, entry)` — append JSON line to a `.ai-assets-memory/` log file

All 11 new hook scripts import from this module. Existing 4 hook scripts (carried from B2) optionally refactored to use it (out-of-scope for B2 minimum migration; can be done in Phase 4 hardening).

### Hooks in dependency order (write upstream-needed scripts first)

| # | Script | Event | Notes |
|---|---|---|---|
| 64 | `session-start-context.py` | `SessionStart` | Reads ≤8KB of CLAUDE.md/AGENTS.md/ARCHITECTURE.md, applies PII filter, applies G1 untrusted wrap, initializes session token meter at `.ai-assets-memory/sessions/<id>/token-meter.json`, detects locale |
| 65 | `instructions-loaded-augment.py` | `InstructionsLoaded` | When CLAUDE.md or rule loads, supplements with `.ai-assets-memory/.committed/conventions.md` excerpt (G1 wrapped) |
| 66 | `pre-compact-memory-flush.py` | `PreCompact` | **CRITICAL** — invokes memory-curator agent (Haiku, ≤5K tokens) to extract durable learnings to L4 BEFORE compaction destroys context |
| 67 | `session-end-finalize.py` | `SessionEnd` | Summarizes runs.jsonl, archives sessions/<id>/, releases dangling RALF locks, updates eval baselines if a `/eval --baseline` ran |
| 68 | `subagent-start-budget.py` | `SubagentStart` | Validates G7 spawn payload schema; checks session token meter against soft/hard caps; rejects spawn if cap exceeded |
| 69 | `subagent-stop-learnings.py` | `SubagentStop` | Validates G7 return contract; if `userConfig.subagent_learnings_enabled`, captures non-trivial outputs for memory-curator. **Validation error path (Round 6 HIGH-4):** if return JSON malformed / missing required fields / unexpected status → log to `.ai-assets-memory/errors.log` (severity ERROR + trace_id + missing field name + expected schema), emit `validation_failed: true` event, fail-open (allow workflow to continue per §1.9), surface diagnostic to orchestrator via stderr. Orchestrator decides retry vs escalate. NEVER block parent workflow on validation failure |
| 70 | `task-event-log.py` | `TaskCreated`, `TaskCompleted` | Writes structured TodoList events to `.ai-assets-memory/sessions/<id>/runs.jsonl` |
| 71 | `tool-failure-log.py` | `PostToolUseFailure`, `StopFailure` | Logs to `.ai-assets-memory/errors.log`; separates failure path from success log |
| 72 | `ralph-stop.py` | `Stop` | If `.ai-assets-memory/ralph/<run-id>/active.lock` exists: run oracle, check kill-on signal, check budgets, re-inject continuation prompt OR allow Stop |
| 73 | `tool-output-wrap.py` (G1) | `PostToolUse` matcher `Read|Bash` for memory dirs and project files | Wraps outputs >200 tokens in `<untrusted_content>` envelope |
| 74 | `tool-output-normalize.py` (G2) | `PostToolUse` matcher same as wrap, fires AFTER | Outputs >2000 tokens: extract → Haiku-summarize → annotate envelope; tracks `injected_tokens` against meter. **Self-enforcing order (Round 5 S6):** asserts wrap marker from previous hook via `_lib.read_wrap_marker()`; aborts with clear error if absent — protects against future hooks.json reorderings |
| 74a | `pre-tool-use-committed-write.py` (Round 8 CRIT-1 — was missing from B8) | `PreToolUse` matcher `Write|Edit` | Validates writes targeting `.ai-assets-memory/.committed/*` against allowlist patterns from `${CLAUDE_PLUGIN_ROOT}/memory/templates/committed-allowlist.txt` + project extension `.ai-assets-memory/.committed/.allowlist-extensions.txt`. Blocks with exit 2 if write path doesn't match allowlist. Referenced by `03-MEMORY-ARCHITECTURE.md` §8 + `plugin/rules/memory-discipline.md` rule 6 |

### `plugin/hooks/hooks.json` extension

75. **B8.12.** Extend `plugin/hooks/hooks.json` with new event mappings. The 12 new hooks (11 original + `pre-tool-use-committed-write` per Round 8 CRIT-1) join the 4 existing in B2.6. Order matters for hooks on the same event: `tool-output-wrap.py` MUST fire before `tool-output-normalize.py` on `PostToolUse`. Documented in the JSON via array order + comments.

76. **B8.13.** Make all 11 new scripts executable: `chmod +x plugin/hooks/scripts/*.py`.

### Hook implementation rules (per `00-PHASE-1-PLAN.md` §1.9)

- All scripts use `${CLAUDE_PLUGIN_ROOT}` for paths, never absolute, never relative-to-cwd
- Read JSON from stdin
- Exit 2 = block with reason on stdout; exit 0 = allow
- Fail open on internal errors (per `00-PHASE-1-PLAN.md` §3.8 failure modes) — log to `.ai-assets-memory/hook-errors.log`, never block all tool use because of a buggy hook
- Use the shared `_normalize_hook_input()` helper from existing scripts (carry pattern over)

### Validation B8

- [ ] `ls plugin/hooks/scripts/*.py | wc -l` returns 16 (4 existing + 12 new including pre-tool-use-committed-write per Round 8 CRIT-1).
- [ ] `for f in plugin/hooks/scripts/*.py; do python3 -c "import ast; ast.parse(open('$f').read())"; done` succeeds for all.
- [ ] `cat plugin/hooks/hooks.json | jq '.hooks | keys'` returns 11+ event names.
- [ ] `claude plugin validate ./plugin` passes hook validation.

---

## Batch B9 — JSON Schemas (G7) + Memory Templates (L1)

**Goal:** Create the 2 JSON schemas and the 8 L1 memory templates (7 under `plugin/memory/templates/` + `pii-patterns.txt` co-located in `plugin/hooks/scripts/` for proximity to consumers).

### Schemas

77. **B9.1.** `plugin/schemas/spawn-payload.schema.json` — JSON Schema (draft-07 or draft-2020-12) matching the spawn payload structure in `01-WORKFLOW-SPECS.md` §G7. Required fields: `trace_id`, `subagent_role`, `goal`, `constraints`, `state_slice`, `allowed_tools`, `budget`. `budget` itself a typed sub-object with `max_input_tokens`, `max_output_tokens`, `max_tool_calls`, `max_turns`, `timeout_ms`, `retry_budget`.
78. **B9.2.** `plugin/schemas/return-contract.schema.json` — JSON Schema for return contract. Required: `trace_id`, `status` (enum), `tokens_used`, `result`. Optional: `evidence`, `risks`, `next_actions`, `needs_clarification`.

### Memory templates (L1, read-only)

Per `03-MEMORY-ARCHITECTURE.md` §3 L1:

79. **B9.3.** `plugin/memory/templates/ai-assets-memory.gitignore` — gitignore template that `/ai-assets-init` copies into target repo.
80. **B9.4.** `plugin/memory/templates/committed-readme.md` — explains the `.committed/` contract.
81. **B9.5.** `plugin/memory/templates/learnings-schema.md` — Markdown schema for learnings entries (entity-keyed, with provenance).
82. **B9.6.** `plugin/memory/templates/conventions-schema.md` — Markdown schema for `.committed/conventions.md`.
83. **B9.7.** `plugin/memory/templates/eval-baseline.schema.json` — JSON Schema for baselines.
84. **B9.8.** `plugin/hooks/scripts/pii-patterns.txt` — default PII regex patterns per `03-MEMORY-ARCHITECTURE.md` §7 (EMAIL, SSN, AWS_KEY, AZURE_CONN, GCP_SERVICE_ACCOUNT, STRIPE_KEY, GITHUB_PAT, JWT_SHAPE, GENERIC_API_KEY).
85. **B9.9.** `plugin/memory/templates/committed-allowlist.txt` — patterns permitted in `.committed/`.
86. **B9.10.** `plugin/memory/templates/untrusted-content-wrapper.md` — canonical `<untrusted_content>` wrapper template referenced by the rule (B7.4).

### Validation B9

- [ ] `cat plugin/schemas/spawn-payload.schema.json | jq .` succeeds (valid JSON).
- [ ] All 8 template files exist in `plugin/memory/templates/` + `plugin/hooks/scripts/pii-patterns.txt`.

---

## Batch B10 — Output Styles + Eval Skeletons

**Goal:** 2 output styles + Tier 1 linter scaffold + 17 rubric skeleton files.

### Output styles

87. **B10.1.** `plugin/output-styles/concise-pr.md` — terse, change-focused output style for `/develop` PR descriptions.
88. **B10.2.** `plugin/output-styles/design-pack.md` — structured Markdown with consistent heading hierarchy for `/feature-design` artefacts.

### Tier 1 linter scaffold

89. **B10.3.** `plugin/eval/runner.py` — entrypoint with `--tier {1,2,3}`, `--skill`, `--all`, `--resume`, `--baseline` flags per `02-EVAL-FRAMEWORK.md` §11. v0.1: only Tier 1 implementation (linters: frontmatter, references, char-limit, AST, JSON schema, forbidden-field check on agents).

> **Note (Round 4 N4):** `plugin/eval/config.json` is created in B1.7, not here. Earlier draft of this batch duplicated it; removed.

### Rubric skeletons (17)

Author skeleton-only versions (full rubric content in Phase 3). Each rubric file is ~30-50 lines: dimensions table + pass threshold + judge model assignment + anti-pattern list. Full prose can wait.

| # | Rubric file (per-workflow, 10) |
|---|---|
| 91 | `plugin/eval/judge-rubrics/feature-design.md` (full per `00-PHASE-1-PLAN.md` §3.6 skeleton; the only fully-authored rubric in B10) |
| 92 | `plugin/eval/judge-rubrics/develop.md` (skeleton) |
| 93 | `plugin/eval/judge-rubrics/bugfix.md` (skeleton) |
| 94 | `plugin/eval/judge-rubrics/refactor.md` (skeleton) |
| 95 | `plugin/eval/judge-rubrics/migrate.md` (skeleton) |
| 96 | `plugin/eval/judge-rubrics/spike.md` (skeleton) |
| 97 | `plugin/eval/judge-rubrics/security-audit.md` (skeleton with OWASP coverage dim per G3) |
| 98 | `plugin/eval/judge-rubrics/docs-pack.md` (skeleton) |
| 99 | `plugin/eval/judge-rubrics/env-analyze.md` (skeleton) |
| 100 | `plugin/eval/judge-rubrics/ai-assets-init.md` (skeleton) |

| # | Rubric file (cross-cutting, 7) |
|---|---|
| 101 | `plugin/eval/judge-rubrics/humanizer-compliance.md` |
| 102 | `plugin/eval/judge-rubrics/code-quality.md` |
| 103 | `plugin/eval/judge-rubrics/security-soundness.md` |
| 104 | `plugin/eval/judge-rubrics/geo-readiness.md` |
| 105 | `plugin/eval/judge-rubrics/subagent-handoff-quality.md` |
| 106 | `plugin/eval/judge-rubrics/memory-write-discipline.md` |
| 107 | `plugin/eval/judge-rubrics/faithfulness.md` (G5; full per `02-EVAL-FRAMEWORK.md` §4 dimensions) |

### Validation B10

- [ ] `python3 plugin/eval/runner.py --tier 1` runs without crashing (will report errors against currently-incomplete plugin, that's expected — exit code reflects findings).
- [ ] `ls plugin/eval/judge-rubrics/*.md | wc -l` returns 17.
- [ ] `ls plugin/output-styles/*.md | wc -l` returns 2.
- [ ] `eval/config.json` exists (created in B1.7, not duplicated here).

---

## Batch B10a — Calibration Samples (NEW per Round 4 N5)

**Goal:** Ship 3-5 reference outputs per rubric (good and bad) so `/plugin-doctor --calibrate-judge` has data to compute Spearman correlation without requiring user authoring on first install.

> Without this batch, `/plugin-doctor --calibrate-judge` cannot run on a fresh install. v0.1 ships a minimal seed; v0.2+ user can extend `plugin/eval/calibration/<rubric>/{good,bad}/` with their own samples.

### Per rubric (17 rubrics total)

For each rubric in `plugin/eval/judge-rubrics/`, author 3 known-good and 3 known-bad reference outputs at `plugin/eval/calibration/<rubric-name>/good/` and `plugin/eval/calibration/<rubric-name>/bad/`. Each sample is a 50-200 line Markdown or JSON file with a ground-truth score in the filename suffix (e.g., `cache-invalidation-design.score-4.6.md`).

| # | Rubric | Sample count |
|---|---|---|
| 108a | feature-design | 3 good + 3 bad |
| 108b | develop | 3 good + 3 bad |
| 108c | bugfix | 3 good + 3 bad |
| 108d | refactor | 3 good + 3 bad |
| 108e | migrate | 3 good + 3 bad |
| 108f | spike | 3 good + 3 bad |
| 108g | security-audit | 3 good + 3 bad |
| 108h | docs-pack | 3 good + 3 bad |
| 108i | env-analyze | 3 good + 3 bad |
| 108j | ai-assets-init | 3 good + 3 bad |
| 108k | humanizer-compliance | 3 good + 3 bad |
| 108l | code-quality | 3 good + 3 bad |
| 108m | security-soundness | 3 good + 3 bad |
| 108n | geo-readiness | 3 good + 3 bad |
| 108o | subagent-handoff-quality | 3 good + 3 bad |
| 108p | memory-write-discipline | 3 good + 3 bad |
| 108q | faithfulness | 3 good + 3 bad |

Total: 17 × 6 = 102 sample files.

### Sample sourcing

- For **good samples** (score 4-5): synthesise small but realistic outputs that pass the rubric (e.g., a 15-line PRD excerpt that meets all dimensions). Author or borrow from public-domain examples (no project-specific or proprietary content per D2 — keep samples generic).
- For **bad samples** (score 1-2): violate specific dimensions explicitly (e.g., PRD with no acceptance criteria, missing risk section, AI-vocabulary inflation).
- **Document the ground-truth score** in the filename or front-matter; `/plugin-doctor` reads this for Spearman calibration.

### Validation B10a

- [ ] `find plugin/eval/calibration -type f | wc -l` returns 102 (or close — minor variance acceptable).
- [ ] Each sample filename contains a `score-<N>.<extension>` pattern.
- [ ] `/plugin-doctor --calibrate-judge` runs without "no calibration data" error.

> **DECISION (Round 6 HIGH-1):** v0.1 ships **34 minimal samples** (1 good + 1 bad per rubric × 17 rubrics). Phase 3 expands to **102 samples** (3 good + 3 bad per rubric). v0.1 calibration is informational-only (Spearman from N=2 is noisy); Phase 3 calibration is gate-blocking. The "or" hedge in earlier draft is removed.

---

## Batch B11 — REFACTOR Skills (13)

**Goal:** Refactor 13 existing skills against new patterns (subagent-aware, memory-aware, eval-ready, G1 wrapping, G7 spawn payloads, G10 RALF continuation prompts where applicable).

> This batch is the most editorial — each skill needs a real rewrite, not a copy. Some can be done mechanically; some need design judgement.

### Refactor approach per skill

For each, the changes follow a common template:

1. **Carry over** the original SKILL.md as a starting point
2. **Update frontmatter** to H5 trigger pattern
3. **Add memory write points** per `03-MEMORY-ARCHITECTURE.md` §4 table
4. **Add subagent spawn payload** (G7) format where the skill spawns subagents
5. **Add RALF wiring** per `01-WORKFLOW-SPECS.md` workflow spec where applicable
6. **Add untrusted-wrapping** instruction per G1 for any read of project files
7. **Add observability** event names per §3.9
8. **Add eval rubric pointer** per workflow spec

### Skills list

Each entry includes the workflow-spec section that authoritatively describes it.

| # | Skill | Workflow spec ref | Refactor focus |
|---|---|---|---|
| 108 | feature-dev | `01-WORKFLOW-SPECS.md` `/develop` | Hand-off to team-dev for multi-stack; G1 wrap on docs read; eval gate |
| 109 | bugfix | `01-WORKFLOW-SPECS.md` `/bugfix` | Extract env-analyzer to standalone (B12.2); RALF on reproduction test |
| 110 | team-dev → **RENAME to `develop`** | `01-WORKFLOW-SPECS.md` `/develop` | **REFACTOR-RENAME** (per Round 4 N2): rename dir from `team-dev/` to `develop/`, content gets full refactor: sequential code-mod gate (per §3.7); SRE-smoke INSIDE QA (per P20); G7 spawn payloads; RALF on test failures (per workflow spec caps) |
| 111 | team-bugfix | `01-WORKFLOW-SPECS.md` `/bugfix` | Use new env-analyzer skill; G7 payloads |
| 112 | team-protocols | `01-WORKFLOW-SPECS.md` Common Patterns G7 | Add JSON spawn payload + return contract sections; refactor lead-protocol/developer-protocol/reviewer-protocol/role-selection-table.md to use schemas |
| 113 | plan | (existing) | Add output schema (Markdown + JSON sidecar) so /develop can consume; multi-reviewer feedback per existing skill |
| 114 | release | (existing) | Add memory-write step (release notes → L4); changelog generation |
| 115 | create-pr | (existing) | Add G1 wrap on diff content; auto-build PR description from REVIEW-LOG.md |
| 116 | infra-change | (existing) | Add ralph-budget rule reference; propagate G7 |
| 117 | deploy-staging | (existing) | Memory write to L4 (deploy event log) |
| 118 | deploy-production | (existing) | Same as above + stricter gate (user confirmation explicit) |
| 119 | run-tests | (existing) | Output normalization (G2) for test runner stdout |
| 120 | test-local | (existing) | Same as run-tests for local Docker context |

### Validation B11

- [ ] All 13 skill bodies updated; no skill exceeds 12,000 chars
- [ ] `python3 plugin/eval/runner.py --tier 1 --skill <each>` passes for each refactored skill
- [ ] At least one skill passed manual smoke test (invoke and check expected behavior)

---

## Batch B12 — NEW Skills (17, atomic per Round 4 N3)

**Goal:** Author 17 new skills per `01-WORKFLOW-SPECS.md` Parts A and B. Each skill is its own atomic checklist item.

### Workflow skills (8 NEW, fully spec'd in 01-WORKFLOW-SPECS.md Part A)

> Excluded: `/develop` (handled in B11 as REFACTOR-RENAME of team-dev → develop), `/bugfix` (handled in B11 as REFACTOR of existing bugfix). Both already counted under REFACTOR.

| # | Skill | Spec source | Notes |
|---|---|---|---|
| 121 | feature-design | §/feature-design | Multi-agent design pack from idea; uses feature-design-lead orchestrator |
| 122 | env-analyze | §/env-analyze | **Renamed from env-analyzer** to match slash command (Round 4 N2) |
| 123 | refactor | §/refactor | Refactor across N files with safety nets |
| 124 | migrate | §/migrate | Schema/library/version migration with rollback plan |
| 125 | spike | §/spike | Time-boxed exploration; ALWAYS-ASK before write to `.committed/decisions/` per Q4 |
| 126 | security-audit | §/security-audit | OWASP coverage per G3; no effort estimate per Q2 |
| 127 | docs-pack | §/docs-pack | User-facing docs (README, API ref, runbook); distinct from existing `docs` knowledge skill |
| 128 | ai-assets-init | §/ai-assets-init | Bootstrap target repo; seeds `.ai-assets-memory/` from L1 templates |

Author each as a user-invocable skill (`context: fork` or `user-invocable: true`). Body follows the workflow spec template: Purpose / Invocation / Input / Output / Agent roster / Pipeline / Eval rubric pointer / RALF wiring / Memory writes / Failure modes / Observability events.

### Companion skills (9 NEW, spec'd in 01-WORKFLOW-SPECS.md Part B)

| # | Skill | Notes |
|---|---|---|
| 129 | ralph | Standalone RALF entry point; rejects invocation if `--kill-on` missing per D12 |
| 130 | eval | Wraps `eval/runner.py` with slash flags (`--skill`, `--tier`, `--all`, `--resume`, `--baseline`) |
| 131 | plugin-doctor | Self-diagnostic; **`--calibrate-judge` is opt-in** per Round 4 O4 (not in default smoke run) |
| 132 | memory-init | Creates `.ai-assets-memory/` skeleton from L1 templates |
| 133 | memory-recall | Queries L4/L5 for relevant memory by topic |
| 134 | learnings-write | Curated write to L4 (default) or L5 (`--global`); requires `userConfig.user_global_memory_enabled` for L5 |
| 135 | context-load | Returns per-role project context slice (per `00-PHASE-1-PLAN.md` §3.12) |
| 136 | subagent-spawn | Typed delegation helper; constructs G7 spawn payload; enforces role-selection-table.md |
| 137 | plugin-skill-create | Scaffolds new plugin-scoped skill with eval stub pre-wired (narrower than Anthropic's `skill-creator`) |

---

## Batch B13 — User-Facing Documentation (NEW per Round 5 S1)

**Goal:** Author the user-facing docs that Plan §5 Phase 2 promised but were missing from earlier batches: getting-started, per-workflow user docs, concept overviews.

> Without this batch, plugin v0.1 has no entry point for new users beyond the top-level README.

### Files to author

138. **B13.1.** `plugin/docs/getting-started.md` — 30-min tutorial: install, first run, `/ai-assets-init`, run a sample `/feature-design`, observe outputs. ~100-200 lines.

#### Per-workflow user docs (10 files for the 10 workflow slash commands)

| # | File | Source spec |
|---|---|---|
| 139 | `plugin/docs/workflows/feature-design.md` | `01-WORKFLOW-SPECS.md` /feature-design (user-readable adaptation) |
| 140 | `plugin/docs/workflows/develop.md` | /develop |
| 141 | `plugin/docs/workflows/bugfix.md` | /bugfix |
| 142 | `plugin/docs/workflows/env-analyze.md` | /env-analyze |
| 143 | `plugin/docs/workflows/refactor.md` | /refactor |
| 144 | `plugin/docs/workflows/migrate.md` | /migrate |
| 145 | `plugin/docs/workflows/spike.md` | /spike |
| 146 | `plugin/docs/workflows/security-audit.md` | /security-audit |
| 147 | `plugin/docs/workflows/docs-pack.md` | /docs-pack |
| 148 | `plugin/docs/workflows/ai-assets-init.md` | /ai-assets-init |

Each user doc covers: when to use, how to invoke, what you get, common questions, examples. ~80-150 lines per file.

#### Concept docs (3 files for cross-cutting concerns)

| # | File | Source spec |
|---|---|---|
| 149 | `plugin/docs/concepts/memory.md` | `03-MEMORY-ARCHITECTURE.md` (user-readable summary; full doc is internal design) |
| 150 | `plugin/docs/concepts/eval.md` | `02-EVAL-FRAMEWORK.md` (user-readable summary) |
| 151 | `plugin/docs/concepts/ralf.md` | `01-WORKFLOW-SPECS.md` /ralph + Plan §3.5 (user-readable summary) |

### Authoring style

- **Audience:** plugin USERS (not plugin maintainers). Internal design docs in `plugin-design/` are for maintainers.
- **Tone:** practical, example-driven. Show, don't define.
- **Length:** keep each doc scannable. Most users read top + scan headings.
- **Cross-link:** every workflow doc links to the related concept doc(s). Concept docs link to relevant workflow docs.

### Validation B13

- [ ] `ls plugin/docs/getting-started.md plugin/docs/workflows/*.md plugin/docs/concepts/*.md | wc -l` returns 14.
- [ ] Every user doc has at least one example invocation.
- [ ] Every concept doc links to at least 2 workflow docs.

### Validation B12

- [ ] `ls plugin/skills/ | wc -l` returns 52 (20 KEEP + 13 REFACTOR + 2 MERGE-output + 17 NEW = 52)
- [ ] **Use-when trigger check (Round 5 S9 fix):** for each user-invocable skill (`grep -l "user-invocable: true\|context: fork" plugin/skills/*/SKILL.md`), verify its description contains "Use when". Knowledge-only skills (e.g., context-engineering, prompt-engineering) are exempt — they don't need slash-command activation triggers
- [ ] `python3 plugin/eval/runner.py --tier 1 --all` reports 0 critical errors
- [ ] `claude plugin validate ./plugin` passes
- [ ] `/plugin-doctor` runs end-to-end without crash (does NOT need `--calibrate-judge` to pass per Round 4 O4)

---

## Merge Plans (executed during B11 or B3 — not separate batches)

### Merge M1: `marketing` + `marketing-operations` → single `marketing`

- Read both source SKILL.md files
- Identify overlap (high — marketing-operations is mostly a sub-workflow within marketing scope)
- Author single `plugin/skills/marketing/SKILL.md` consolidating both
- Body: explicitly read `marketing/MARKETING.md` from target repo at runtime (operations/data split per D2). Never hardcode brand/ICP/terminology.
- Drop `marketing-operations` (do NOT copy to plugin/)

### Merge M2: `blog-post` + `content-creation` → single `content-creation`

- Read both source SKILL.md files
- `blog-post` is a specialised template within `content-creation` scope
- Author single `plugin/skills/content-creation/SKILL.md` with blog-post pattern as a section
- Move `blog-post` resources into `plugin/skills/content-creation/blog-post-template.md` (companion file)
- Drop `blog-post` (do NOT copy as standalone)

---

## Archive Decisions (no action — leave in legacy `.claude/`)

These 5 skills do NOT migrate. They remain in `.claude/skills/<name>/` for legacy use until Phase 5 sunset (per `00-PHASE-1-PLAN.md` §5 Phase 5).

| Skill | Reason |
|---|---|
| ai-assets | Replaced by `plugin-doctor`. Content overlaps; new skill is plugin-aware. |
| asset-validation | Replaced by `plugin-doctor` (validation portion). |
| ml-pipeline | Highly project-specific (ML/data pipeline patterns); revisit in v0.3 if generalisable. |
| product | Overlaps with `product-manager` agent capabilities; agent does the work directly. |
| project-init | Replaced by `ai-assets-init` (broader scope: bootstrap a target repo to be ai-assets-aware, not just project init). |

---

## Final Validation (after ALL batches complete)

- [ ] **V1.** `claude plugin validate ./plugin` passes with no errors or warnings.
- [ ] **V2.** `/plugin-doctor` end-to-end (default mode, no `--calibrate-judge`): skill load, hook executable, runs jsonl parseable. **Calibration check is opt-in per Round 4 O4** — if user runs `/plugin-doctor --calibrate-judge` in Phase 4 hardening, target Spearman ≥0.7 on at least 3 rubrics with v0.1 minimal samples (more rigorous after Phase 3 expansion to 102 samples). Round 6 MED-2 fix: V2 no longer requires calibration to pass for Phase 2 completion.
- [ ] **V3.** `python3 plugin/eval/runner.py --tier 1 --all` exit code 0.
- [ ] **V4.** Asset counts:
  - `ls plugin/skills/ | wc -l` → **52** (Round 4 N1 fix)
  - `ls plugin/agents/*.md | wc -l` → 26
  - `ls plugin/rules/*.md | wc -l` → 12
  - `ls plugin/hooks/scripts/*.py | wc -l` → 16 (4 existing + 12 new per Round 8 CRIT-1)
  - `ls plugin/eval/judge-rubrics/*.md | wc -l` → 17
  - `ls plugin/schemas/*.json | wc -l` → 2
  - `ls plugin/output-styles/*.md | wc -l` → 2
  - `find plugin/eval/calibration -type f | wc -l` → 34 (minimal v0.1 seed) or 102 (full)
  - `ls plugin/memory/templates/*.md plugin/memory/templates/*.json plugin/memory/templates/*.txt 2>/dev/null | wc -l` → 7 (Round 5 S10 fix; pii-patterns.txt lives separately in hooks/scripts/)
  - `ls plugin/docs/getting-started.md plugin/docs/workflows/*.md plugin/docs/concepts/*.md | wc -l` → 14 (Round 5 S1 fix)
- [ ] **V5.** No friendly4ai or owner-personal info anywhere: `grep -rE "friendly4|f4ai|@gmail|avav" plugin/` returns nothing.
- [ ] **V6.** Manual smoke test: install plugin in a sample target repo (e.g., a small Python project), run `/ai-assets-init`, then `/feature-design "small example"`, observe waves spawn correctly and a design pack lands in `docs/features/`.
- [ ] **V7.** Tag plugin v0.1.0-alpha in git; write `CHANGELOG.md` entry.

---

## Rollback Plan

If a batch fails or the resulting plugin misbehaves:

1. **Within a batch:** revert the specific files via git; re-run validation.
2. **Whole batch failure:** `rm -rf plugin/<subdir>` for the affected component, restart the batch from item 1.
3. **Catastrophic failure (e.g., installer breaks Claude Code):** `claude plugin uninstall ai-assets`, `rm -rf plugin/`, fall back to the legacy `.claude/` setup which has been untouched throughout.
4. **Legacy still works.** Per D4, `.claude/`, `.codex/`, `.windsurf/`, `.agents/` are NEVER modified during Phase 2. The user's existing workflow stays available for the entire migration.

---

## Estimated Effort

| Batch | Complexity | Estimated session count |
|---|---|---|
| B1 skeleton + manifest | Low (mostly file creation) | 1 session |
| B2 existing hooks + format update | Low (4 file copies + 1 JSON write) | 0.5 session |
| B3 KEEP skills (20) | Low-medium (mostly copy + audit) | 1 session |
| B4 existing agents (22) | Medium (frontmatter edits) | 1 session |
| B5 new agents (4) | Medium (authoring) | 1 session |
| B6 existing rules (8) | Low | 0.5 session |
| B7 new rules (4) | Medium (authoring) | 1 session |
| B8 new hooks (11) | High (Python script authoring + testing) | 2-3 sessions |
| B9 schemas + memory templates (10) | Medium | 1 session |
| B10 output styles + eval scaffold + rubric skeletons (21) | Medium | 1.5 sessions |
| B11 REFACTOR skills (13) | High (editorial rewrites) | 2-3 sessions |
| B12 NEW skills (12) | High (substantial authoring) | 3-4 sessions |
| Final validation (V1-V7) | Medium | 1 session |
| **TOTAL** | | **~17-19 sessions** |

This effort can be parallelized across multiple Claude Code sessions or distributed across the migration plan's Phase 1-2 weeks (per `00-PHASE-1-PLAN.md` §5).

---

## What's Next After This Checklist

After all 132 items + V1-V7 complete: enter migration plan Phase 3 (Eval Tier 2+3 — author 5-10 eval cases per workflow skill, capture baselines), then Phase 4 (Hardening — caching verification, indirect-injection test fixtures, dogfood on 3 diverse target repos), then Phase 5 (Sunset legacy when v0.2.0 stable).

For Phase 2 itself: this checklist replaces ad-hoc "what should I build next?" decisions with a deterministic order. Each batch is independently mergeable and validatable.
