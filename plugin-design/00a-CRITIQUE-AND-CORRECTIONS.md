# Phase 1 Plan — Self-Critique and Corrections

> **Purpose:** Adversarial review of `00-PHASE-1-PLAN.md`. For every issue: question → answer → implication → fix.
> **Output:** structured patch list applied to the main plan in this same commit.
> **Date:** 2026-04-26

---

## A. Internal contradictions

### A1. D6 says "no pre-canned single orchestrator agent" — but Section 4.1 ships `feature-design-lead` as exactly that.
**Q:** Did I betray my own decision in the same document?
**A:** Yes — partially. D6 was answered to mean "don't make EVERY workflow go through one universal orchestrator" — not "no orchestrator agents at all." The user explicitly opted out of the option labelled "Long workflows через orchestrator-agent + plan files" because that suggested one fat orchestrator gating all workflows. Per-workflow specialist orchestrators (feature-design-lead is one of them) are different and still valid — they're the team-lead pattern Anthropic ships in Agent Teams.
**Implication:** D6 wording is misleading.
**Fix:** Rewrite D6 to "long workflows are slash-commands that spawn workflow-specific orchestrators or coordinate subagents inline; there is no single universal orchestrator." Add a clarifier in Section 3.7.

### A2. Memory layer count: Section 1.4 lists 5 layers, Section 3.4 has 4.
**Q:** Why the mismatch?
**A:** Section 1.4 includes "Plugin-state (read-only)" but Section 3.4 only counts active/writable layers. Plus Cowork mode itself ships an auto-memory at `~/...spaces/<id>/memory/` that I did not even acknowledge.
**Implication:** Reader cannot tell what counts. Cowork auto-memory will collide with our writes if we ignore it.
**Fix:** Reconcile to 5 layers, add a sixth "Cowork host memory (out of plugin scope, acknowledge only)" with explicit non-interference contract.

### A3. Section 3.7 says "sequential pipeline always for any code-touching workflow" but `/feature-design` Wave 1 spawns 3 agents in parallel.
**Q:** Is feature-design code-touching?
**A:** No — feature-design produces docs, not code. `/develop` is code-touching and IS sequential. So the rule is fine but wording in 3.7 is sloppy ("always") and gives no clear boundary.
**Fix:** Rewrite the rule as "code-modifying stages are sequential per file; analysis and document-production stages may be parallel."

### A4. Section 4.2 introduces a new pipeline stage `SRE-smoke` after QA, but `team-protocols` describes the pipeline as DEVELOP → REVIEW → QA only.
**Q:** Is SRE-smoke optional or mandatory? Where does it live in the gate model?
**A:** Originally I treated it as "new" without explaining how the gate behaviour scales. Adding a stage means adding a gate rule; I never specified one.
**Fix:** Either (a) demote SRE-smoke to "post-QA verification, not a gate" or (b) explicitly add it as a gated stage with rules. Recommend (a) — keep the 3-stage gate model intact, list SRE-smoke as a verification step inside QA. Update 4.2 accordingly.

---

## B. Math and counting errors

### B1. Skill count is wrong.
**Plan says:** 41 skills.
**Reality:** 42 skills (verified by `ls -d .claude/skills/*/ | wc -l`).
**Fix:** Update Section 2 header and disposition arithmetic.

### B2. Disposition table doesn't add up.
**Plan says:** ~20 KEEP + ~12 REFACTOR + 4 MERGE + 12 NEW + 5 ARCHIVE = ~53.
**Reality:** Should equal 42 EXISTING items + the 12 NEW items added on top = 54. The "~20 KEEP + ~12 REFACTOR + 4 MERGE + 5 ARCHIVE" should sum to 42 (the existing skill count) — currently 41. Off by one and uses tilde-numbers throughout.
**Fix:** Replace with concrete enumerated lists per disposition, no tildes. Each existing skill assigned exactly one disposition.

### B3. Eval Tier 2 token budget is unworkable.
**Plan says:** Tier 2 smoke = 50K soft / 150K hard for entire suite. Section 3.6 says "feed 50 prompts, confirm correct skills activate."
**Reality:** With 42 skills × 50 prompts × ~300 tokens-per-prompt-roundtrip = ~600K tokens minimum. Plus activation requires running the model. Budget is wrong by an order of magnitude.
**Fix:** Either (a) run activation eval on a small sampled subset (e.g., 10 skills × 20 prompts per release = ~60K tokens, fits 150K) or (b) raise Tier 2 hard cap to 1M tokens. Recommend (a) — sample-based smoke is the standard pattern.

### B4. Tier 3 full-suite math is also tight.
**Plan says:** 30K per skill × ~32 skills (after merge) ≈ 960K, ceiling 1.5M.
**Reality:** Math actually checks out for 32 skills. But plan never states "32 skills after migration" — that number isn't anchored. Also assumes Haiku for judge; if any skill needs Sonnet judge the math breaks.
**Fix:** Anchor "after migration: ~32 skills (8 archived/merged from 42 + 12 new − 18 unchanged accounting overlap)." Add a "Sonnet judge override" exception that triggers a higher per-skill budget (say 60K).

### B5. Agent forbidden-fields count.
**Plan says:** "drop hooks, mcpServers, permissionMode if present."
**Reality:** 9 of 22 agents have `permissionMode: plan`. None have `hooks` or `mcpServers`. The 9 that have it are: cloud-architect, content-designer, content-writer, devops-architect, marketing-strategist, product-manager, solution-architect, system-architect, ui-ux-designer.
**Fix:** Replace "if present" with explicit list. State that these 9 agents need a refactor pass — not just defensive normalization. Decide replacement: either (a) remove the field (subagent inherits parent's permissions) or (b) achieve the same intent via `disallowedTools: Write, Edit` (which is already set on most of them — the field is largely redundant). Recommend (b): drop `permissionMode`, rely on existing `disallowedTools: Write, Edit` to keep agents read-only.

---

## C. Underspecified mechanisms

### C1. Slash commands vs user-invocable skills — which is which?
**Plan says:** Layout has both `commands/` and `skills/`. Component map says "Slash command (entrypoint, thin)."
**Reality:** Per Anthropic docs, `commands/` is the legacy flat-md format; new plugins should use `skills/` with frontmatter. A user-invocable skill (`context: fork` or analogous) IS the slash command. There is no separate "thin entrypoint" file.
**Implication:** Layout is wrong — we should not have both.
**Fix:** Remove `commands/` from layout. Every slash-invokable workflow is a user-invocable skill in `skills/`. Update component map to clarify "slash commands ARE user-invocable skills."

### C2. RALF kill-on signal — what is it concretely?
**Plan says:** D12 makes `--kill-on` mandatory; Section 3.5 says "kill on PATTERN."
**Reality:** Never defined what counts as a signal. Could be: regex on Claude's output, exit-code from oracle, count of repeated identical errors, custom Python predicate.
**Fix:** Specify a typed signal language: `--kill-on '<type>:<value>'` where `<type>` is one of:
- `oracle-pass` — oracle returns 0 (the success case, not really a kill but a "stop happily")
- `same-error-repeats:N` — same error string seen N times in a row
- `regex:PATTERN` — regex matches in the latest model output
- `python:script.py` — custom predicate, exit 0 = continue, exit 2 = kill
- `no-progress:N` — N iterations with no file diff

### C3. Eval blind-comparator — how is the skill "turned off"?
**Plan says:** "blind-comparator runs same prompt without skill loaded."
**Reality:** Claude Code does not expose a "disable single skill for one call" API. The mechanism is unclear.
**Implication:** Whole blind-comparator concept might not work as drawn.
**Fix (Round 1):** Specify the actual mechanism: blind-comparator runs in an isolated subagent (`Agent` call) with `skills: []` in its frontmatter. Verify in Phase 2.
**Round 3 follow-up (2026-04-26):** Verified against Anthropic docs. The `skills:` field is an **auto-load** directive — it pre-loads listed skills into the subagent's context at startup but does NOT restrict which skills the subagent can DISCOVER and INVOKE at runtime via the Skill tool. Only `disable-model-invocation: true` on the SKILL itself (not the agent) excludes it from the discovery list. Therefore `skills: []` does NOT reliably suppress activation.
**Final approach** (now in `02-EVAL-FRAMEWORK.md` §7): instruction-based suppression in an isolated subagent is PRIMARY (parallel-safe, deterministic per-call). Plugin-level disable for a separate session is FALLBACK for high-stakes baselines. File-mutation toggle of `disable-model-invocation` is documented as NOT used (race conditions). Tier 2 smoke includes a "suppression compliance" probe to detect cases where the instruction was ignored, triggering automatic fallback.

### C4. Hook `subagent-stop-learnings.py` "off by default" — toggled how?
**Plan says:** "off by default."
**Reality:** Plugins ship a fixed `hooks/hooks.json`. There's no per-user toggle in the standard plugin model.
**Fix:** Either (a) ship two `hooks.json` variants and document install-time choice, or (b) make the hook itself read a flag from `.ai-assets-memory/config.json` and no-op if not enabled. Recommend (b).

### C5. Eval case format — `eval/cases/<skill>/<case>.json` mentioned, never specified.
**Fix:** Define the JSON schema in Section 3.6. Skeleton:
```json
{
  "id": "feature-design-001",
  "skill": "feature-design",
  "prompt": "Design a feature for...",
  "context_files": [".ai-assets-memory/.committed/sample-CLAUDE.md"],
  "oracle": {
    "type": "judge",
    "rubric": "feature-design-rubric.md",
    "min_score": 4.0
  },
  "expected_artefacts": ["docs/features/*/PRD.md", "docs/features/*/IMPLEMENTATION-PLAN.md"],
  "anti_patterns": ["mentions specific company name", "bullet-only PRD"],
  "max_tokens": 50000,
  "tags": ["workflow", "design", "p0"]
}
```

### C6. feature-design rubric — "6 dimensions × 5 levels" promised, never written.
**Fix:** Add skeleton in main plan: dimensions = `completeness, internal-consistency, traceability, handoff-clarity, risk-coverage, GEO-readiness-if-public`. Levels 1-5 with brief descriptors. Full rubric file lives in `plugin/eval/judge-rubrics/feature-design.md` (to be authored Phase 2).

---

## M. Missing concepts (renamed from "D" in this round to avoid collision with the plan's locked Decisions D1-D13)

### M1. Cowork host auto-memory.
**Reality:** The user runs in Cowork mode which has its own auto-memory at `~/.../spaces/<id>/memory/`. Our plugin memory must not collide or duplicate.
**Fix:** Add to Section 3.4: explicit non-interference contract. Plugin memory NEVER writes to host memory dir. Host memory is opaque to plugin. If they overlap (e.g., user asks for project facts), plugin reads host memory if exposed, but always writes to `.ai-assets-memory/`.

### M2. Multi-language conversation.
**Reality:** User wants Russian conversation, English in files. Skills are English. Subagents should respond in user-prefer-language for non-artefact text. Never specified.
**Fix:** Add a section: "Locale handling — agent system prompts include `RESPOND IN: <user-locale-or-English>` injection at orchestrator level. Artefacts (files) always English per project rule."

### M3. Versioning policy.
**Reality:** Plugin has `version` in `plugin.json`. Skills/agents have no individual versioning. Breaking changes will silently break user workflows.
**Fix:** Add semver discipline: plugin MAJOR bump = breaking skill API change (rename, signature change, hard removal). Add a `CHANGELOG.md` requirement. Add a deprecation policy: removed skills must spend one MINOR version printing deprecation warnings before deletion.

### M4. Distribution and install instructions.
**Reality:** Mentioned `/plugin install <git-url>` in passing. No concrete docs for users.
**Fix:** Add Section 5a covering install methods (git URL, local path, marketplace), uninstall, update, validation (`claude plugin validate`), and how to run the plugin self-test (`/plugin-doctor`).

### M5. Error handling and escalation.
**Reality:** No mention of what happens when subagent fails, hook crashes, oracle errors.
**Fix:** Add Section 3.8 "Failure modes":
- Subagent error → Lead retries once with explicit error context, then escalates to user with full trace
- Hook script crash → fail open with warning (don't block all tool use due to a buggy hook); log to `.ai-assets-memory/hook-errors.log`
- Oracle error in RALF → treat as kill condition; user gets full diagnostic
- Eval runner crash → partial results saved; resume supported

### M6. Observability.
**Reality:** No mention of how the user sees what's happening.
**Fix:** Add: every workflow writes a structured `<run-id>.jsonl` to `.ai-assets-memory/runs/` capturing timestamps, model calls, token counts, subagent spawn/return events. `/plugin-doctor --runs` summarizes.

### M7. Missing security-engineer agent.
**Reality:** Section 4.1 Wave 2 mentions "ui-ux-designer, db-engineer, security review" — no security agent exists. Also no `/security-audit` workflow agent has anyone to lead it.
**Fix:** Add `security-engineer` to the 22 → 23 agents (one new domain agent in addition to the 3 orchestrators). Sketch frontmatter: focuses on threat modelling, dependency CVE checks, secret-handling, authn/authz patterns, OWASP Top 10. Tools: Read, Grep, Glob, Bash; disallowedTools: Write, Edit.

### M8. Anthropic's `skill-creator` plugin already exists.
**Reality:** I proposed a `/skill-create` workflow but Anthropic ships their own `skill-creator` plugin/skill that does exactly this (verified in available_skills: `anthropic-skills:skill-creator`).
**Fix:** Rename our skill to `/plugin-skill-create` and scope it narrowly to creating skills FOR THIS PLUGIN (in `plugin/skills/`), with our eval scaffold pre-wired. Defer general skill creation to Anthropic's existing tool.

### M9. CLAUDE.md / AGENTS.md ingestion details.
**Plan says:** SessionStart hook reads them.
**Reality:** Doesn't specify (a) what if file doesn't exist, (b) what if file is huge (10K+ lines), (c) what if file has secrets/PII.
**Fix:** Specify: hook reads up to 8KB by default, longer files get truncated with a notice; file existence is optional (no error if missing); a PII regex filter runs on the slice before injection. The filter list lives in `plugin/hooks/scripts/pii-patterns.txt`.

### M10. RALF kill-criterion enforcement.
**Plan says (D12):** mandatory kill-criterion.
**Reality:** Never specified WHO enforces. If user runs `/ralph "do X"` without `--kill-on`, what happens?
**Fix:** The `/ralph` skill body validates args before entering the loop and rejects with a clear error if `--kill-on` is missing. The `ralph-stop.py` hook double-checks at runtime. Per-workflow overrides set their own kill-criteria (so `/feature-design` user does not need to think about it).

---

## E. Risk areas not flagged

### E1. Token budget on RALF + nested workflows.
**Risk:** `/feature-design` uses RALF (cap 5 iter × ~50K tokens per iter = 250K) AND `/develop` uses RALF (cap 8 iter × ~80K tokens = 640K). If a user chains `/feature-design` → `/develop` in one session, we burn ~900K tokens easily. With Max plan rate limits this can hit ceilings mid-session.
**Fix:** Add a per-session token meter (`session-start-context.py` initializes a counter, every skill increments). Soft warning at 1M, hard pause at 1.5M asking user to confirm continuation. Numbers configurable in `.ai-assets-memory/config.json`.

### E2. Subagent context contamination.
**Risk:** When the Lead spawns 5 subagents in Wave 2 of `/feature-design`, each gets a full project context payload. 5 × 30K context = 150K tokens just for setup.
**Fix:** Add a "context manifest" per agent — Lead picks a relevant slice (e.g., db-engineer gets only DB-relevant excerpts, not the full ARCHITECTURE.md). The `context-load` skill produces these slices.

### E3. Plugin agents cannot define `permissionMode` — what about our orchestrator agents?
**Risk:** `feature-design-lead` is a plugin-shipped agent. It's intended to coordinate write operations through subagents. Without `permissionMode: plan` we cannot enforce read-only at the agent level.
**Fix:** Use `disallowedTools: Write, Edit, Bash` on the orchestrator. It can only spawn subagents (which DO have write tools). This is actually safer.

### E4. RALF on `/feature-design` rubric: subjective oracle, judge model bias.
**Risk:** Judge is Haiku (per cost decision). Haiku judging Opus output may have systematic bias.
**Fix:** For subjective rubric oracles, add a "judge calibration" check: at install time `/plugin-doctor` runs the judge against 5 known-good and 5 known-bad samples; reports Spearman correlation with expected scores. Flag if < 0.7. Allow user to upgrade judge to Sonnet if calibration weak.

### E5. `.ai-assets-memory/.committed/` is opt-in but easy to misuse.
**Risk:** User accidentally commits ephemeral state by writing to `.committed/` instead of root.
**Fix:** A pre-commit-style hook validates `.committed/` writes against a schema (only files matching allowlist patterns: `conventions.md`, `eval-baseline.json`, `architecture-decisions/*.md`). Warns/blocks unrelated writes. List in `memory-discipline.md`.

---

## F. Documentation strategy gap

**Issue:** Phase 1 produces design docs for *us* — there's no plan for documentation aimed at *plugin users*.
**Fix:** Add to migration plan: Phase 2 must produce
- `plugin/README.md` — install + first-run + workflow tour
- `plugin/docs/getting-started.md` — 30-min tutorial
- `plugin/docs/workflows/<name>.md` — one per workflow, user-facing
- `plugin/docs/concepts/memory.md`, `eval.md`, `ralf.md` — concept overviews

---

## Summary of Patches Applied to `00-PHASE-1-PLAN.md`

| ID | Section | Change |
|---|---|---|
| P1 | D6 | Reword to clarify per-workflow orchestrators are allowed |
| P2 | 1.1 | Add note that plugin-shipped agents cannot use `permissionMode` |
| P3 | 1.4 | Reconcile to 5 layers + Cowork acknowledgement |
| P4 | 2 (header) | Skill count 41 → 42 |
| P5 | 2.1 | Replace tilde-counts with explicit per-skill disposition table |
| P6 | 2.2 | Concrete list of 9 agents with `permissionMode`; specify drop-and-rely-on-disallowedTools strategy |
| P7 | 2.4 | Toggle mechanism for `subagent-stop-learnings.py` (config.json flag) |
| P8 | 3.1 | Remove `commands/` from layout |
| P9 | 3.3 | Clarify slash commands == user-invocable skills |
| P10 | 3.4 | 5 layers + Cowork host memory non-interference contract |
| P11 | 3.5 | Define typed kill-on signal language |
| P12 | 3.6 | Add eval case JSON schema; clarify blind-comparator mechanism; add Sonnet-judge exception; add feature-design rubric skeleton |
| P13 | 3.7 | Tighten parallel-vs-sequential rule (code-modifying = sequential per file) |
| P14 | NEW 3.8 | Failure modes (subagent, hook, oracle, eval) |
| P15 | NEW 3.9 | Observability — `runs/` jsonl |
| P16 | NEW 3.10 | Locale handling |
| P17 | NEW 3.11 | Token meter (per-session) |
| P18 | NEW 3.12 | Context manifest pattern (per-agent slicing) |
| P19 | 4.1 | Clarify Wave coordination, fix security-review (security-engineer agent) |
| P20 | 4.2 | SRE-smoke as verification inside QA, not new gate |
| P21 | 4.5 | Rename `/skill-create` → `/plugin-skill-create`, narrow scope |
| P22 | 5 | Add Phase 2 user-doc deliverables |
| P23 | NEW 5a | Distribution & install section |
| P24 | NEW 6.6 | Versioning + deprecation policy |
| P25 | 7a | Add new agent count: 23 (was 22 + 3) — security-engineer added |

---

## Round 2 — friendly4ai independence + best-practices reverse check (2026-04-26)

### F. friendly4ai-independence sweep (renamed from "G" in this round to avoid collision with Round 3 context-engineering Gaps G1-G10)

**F1. Direct friendly4ai mentions (5 occurrences) — all reworded to generic.**
- D2 wording made fully generic with operations/data split as the explicit contract
- Section 2.2 audit comment generalized to "domain-clean — independent of any specific consumer project"
- Phase 4 dogfooding: "friendly4ai repo" → "three diverse target repos covering different stacks"
- Stable definition: same generalization
- Marketing skill merge note: rewritten to state explicit operations/data split contract

**F2. Personal info in plugin.json example.**
Replaced concrete email / GitHub username with `<author-name>`, `<author-email>`, `<owner>` placeholders. Header "Owner: Alex" line removed. Concrete values fill in at publish time.

**F3. Marketing/content skills (geo-writer, marketing, social-media-manager, etc.).**
Verified by grep: no friendly4ai-specific terms (AI-Readiness, AI-Visibility, GEO Scanner, paid agencies, North Star, hello@/ai@friendly4.ai). All read brand context from target repo's `marketing/MARKETING.md` at runtime — perfect operations/data split. Kept in v0.1 but **explicitly flagged as extended-scope** in Section 8a; may split to sibling plugin in v0.3+.

**F4. Independence statement added** to plan header — load-bearing one-liner that makes the contract explicit at first read.

### H. Best-practices reverse-check — major omissions found

The first draft missed several modern Claude Code plugin features. All added in Round 2:

**H1. `userConfig` declarative configuration.** First draft proposed manual editing of `.ai-assets-memory/config.json` for top-level toggles. Modern best practice is `userConfig` block in `plugin.json` that prompts user at install/configure time. **Replaced** the config.json model for top-level settings; runtime per-session state still uses `.ai-assets-memory/`.

**H2. `outputStyles` and `monitors`.** Not used in first draft.
- Added two output styles (`concise-pr`, `design-pack`) for workflow-specific formatting
- Added one monitor (`env-watch.sh` for Docker compose health) — opt-in via `userConfig.env_watch_enabled`. Solves a real problem (env state drifts during long sessions) elegantly via background notifications.

**H3. Hook event catalogue was incomplete.** First draft listed 4 events; reality is 20+. Added 6 new hooks:
- `instructions-loaded-augment.py` (`InstructionsLoaded`) — better fit than SessionStart for some context loading
- `pre-compact-memory-flush.py` (`PreCompact`) — **CRITICAL** for memory architecture: writes durable learnings to L4 BEFORE compaction destroys session context
- `session-end-finalize.py` (`SessionEnd`) — finalizes run logs, releases dangling RALF locks
- `subagent-start-budget.py` (`SubagentStart`) — pre-spawn token meter check
- `task-event-log.py` (`TaskCreated`/`TaskCompleted`) — TodoList observability
- `tool-failure-log.py` (`PostToolUseFailure`/`StopFailure`) — error path separated from success path

**H4. Hook execution types beyond `command`.** First draft assumed all hooks are shell scripts. Modern types include `prompt` (eval prompt with LLM via `$ARGUMENTS`), `agent` (run agentic verifier), `http`, `mcp_tool`. Added explicit table; flagged plan to migrate eval-judge from custom Python to `prompt:` type in v0.2 (eliminates ~200 lines of LLM-call boilerplate).

**H5. Skill description authoring contract was implicit.** First draft mentioned "third person" once. Added the explicit canonical pattern (verified from official Anthropic docs):
```
<one sentence WHAT, third person, imperative>. Use when <trigger 1>, <trigger 2>, or when user mentions "<keyword 1>", "<keyword 2>". <Optional: when NOT to use>.
```
All NEW and REFACTOR skills must conform.

**H6. Plugin namespacing.** First draft did not address what happens if another installed plugin defines a colliding slash command. Added explicit note: `/feature-design` becomes `/ai-assets:feature-design` on collision.

**H7. Plugin dependencies.** First draft had no `dependencies` field. Added explicit empty array — transparency about being fully standalone in v0.1.

**H8. Out-of-scope features documented.** First draft was silent on what we deliberately don't use. Added Section 8a listing 11 feature categories deferred with rationale (themes, channels, lspServers, MCP servers in v0.1, http hooks, mcp_tool hooks, 10 unused hook events, marketplace publish, etc.).

**H9. Agent frontmatter `memory`, `background`, `isolation` fields.** First draft did not address. Frontmatter list updated in Section 1.1 mentions all three. Specific use:
- `isolation: worktree` — only valid value; useful for `/develop` per-package work isolation. To be specified per-skill in Phase 2.
- `background: true` — for long-running spawn (already used in `team-protocols`)
- `memory` — agent-level memory hint; will be specified per-agent in Phase 2 to point at relevant L4 paths

### I. Net result of Round 2

- **Document length:** main plan grew ~30% (more concrete, fewer hand-waves)
- **friendly4ai independence:** verified clean (grep confirms zero remaining mentions)
- **Best-practices coverage:** plugin features used vs. deferred is now explicit and traceable
- **Open issues from Round 2:** none blocking; agent-level `memory`/`isolation` per-skill specs deferred to Phase 2 as planned

---

## Round 3 — Q1-Q4 user decisions + context-engineering gap analysis (2026-04-26)

### J. Q1-Q4 applied
- Q1: `/env-analyze --auto-fix` scope locked to container-level (no Docker daemon, no TLS, no host-level state). Applied in `01-WORKFLOW-SPECS.md`.
- Q2: `/security-audit` no effort estimates (user/PM owns sizing). Applied.
- Q3: blind-comparator mechanism rewritten — `skills: []` field is for **auto-load**, not filtering; subagents can still discover/invoke skills at runtime. Primary path now instruction-based suppression in isolated subagent (parallel-safe); fallback is plugin-disable for separate session. Applied in `02-EVAL-FRAMEWORK.md`.
- Q4: `/spike` always asks user before writing to `.committed/decisions/` (never auto-create). Applied.

### K. Context-engineering gap analysis (G1-G10)

Section-by-section audit against `context_engineering_guide.md`. Found 10 gaps, no contradictions. User chose to apply ALL G1-G10 immediately (rather than deferring). Applied in 5 dependency-ordered batches:

**Batch 1 — Security baseline (G1+G2+G3) — HIGH priority:**
- **G1 untrusted-content wrapping:** new rule `untrusted-content-wrapping.md`, new hook `tool-output-wrap.py` (PostToolUse), wrapper applied in session-start-context.py and tool-output reads. CLAUDE.md / AGENTS.md / learnings.md / subagent returns / tool outputs >200 tokens MUST be wrapped before injection. Defends against indirect prompt injection (OWASP LLM01).
- **G2 tool output normalization:** new hook `tool-output-normalize.py` (PostToolUse, fires after wrap). Outputs >2000 tokens get extract → summarize (Haiku) → annotate envelope. `injected_tokens` tracked against session token meter.
- **G3 OWASP GenAI Top 10 reference:** explicit references in security-engineer agent description, `/security-audit` rubric (now requires OWASP Web Top 10 + GenAI Top 10 coverage as a rubric dimension).

**Batch 2 — Spawn payload + return contract schemas (G7) — MEDIUM:**
- Defined structured spawn payload (`trace_id`, `subagent_role`, `goal`, `constraints`, `state_slice`, `allowed_tools`, `budget`, `untrusted_inputs`) and return contract (`status`, `tokens_used`, `result`, `evidence`, `risks`, `next_actions`). Schemas live at `plugin/schemas/`. Replaces free-form HANDOFF in Phase 2 team-protocols refactor.

**Batch 3 — G4 + G10:**
- **G4 max_output_tokens:** added to all 22 normalized agents per role type (summarization 300-600 / Q&A 500-1000 / report 800-1500 / code-gen 1500-2500 / orchestrator 800-1500). Lives in spawn payload `budget` field from G7.
- **G10 init vs continuation prompts:** RALF iter 1 uses full init prompt (5-15K tokens); iter ≥ 2 uses continuation prompt (state delta only, 1-3K tokens). ~70% token saving per iteration. Continuation template at `plugin/skills/ralph/templates/continuation-prompt.md`.

**Batch 4 — G5 + G8 + G9:**
- **G5 faithfulness rubric:** added as 7th cross-cutting rubric in `02-EVAL-FRAMEWORK.md`. Distinct from quality and citation correctness — checks claim grounding, no invention, quote fidelity, inference labelling. Sonnet judge by default (Haiku may be too weak); claim-grounding < 3 = auto-fail.
- **G8 context health metrics:** added to `runs.jsonl` event schema — `context_utilization`, `cache_prefix_ratio`, `evidence_density`, `output_to_input_ratio`, `injected_tokens_from_tools`. `/plugin-doctor --health-trends` summarizes.
- **G9 few-shot example library:** convention defined — `plugin/examples/<skill>/<id>.json` with embedding-search at workflow invocation, packed into 0-10% of context budget. Empty library in v0.1; content authored Phase 3.

**Batch 5 — G6 caching:**
- **G6 cache-friendly skill authoring:** new section in skill best practices §1.3 — stable content TOP, dynamic BOTTOM, no interleaving. Phase 4 verification task added to test Claude Code automatic caching behavior + file upstream issue if not auto-cached.
- Phase 4 also adds **G1/G2 attack-surface validation** — 5 indirect-prompt-injection test fixtures.

### L. Net result of Round 3 (before Round 4 amendments)

- **Documents touched:** plan (8 edits), workflow-specs (5 edits), eval-framework (2 edits), memory-architecture (3 edits)
- **New plugin assets defined:** 1 rule (`untrusted-content-wrapping.md`), 2 hooks (`tool-output-wrap.py`, `tool-output-normalize.py`), 2 schemas (`spawn-payload.schema.json`, `return-contract.schema.json`), 1 rubric (`faithfulness.md`), 1 directory convention (`plugin/examples/`)
- **Final counts revised:** 12 rules (was 11; +untrusted-content-wrapping), 11 hooks (was 9; +wrap, +normalize), 17 cross-cutting + per-workflow rubrics (was 16; +faithfulness)
- **Phase 4 hardening expanded:** caching verification + injection attack-surface validation
- **Open items deferred to later phases:** content authoring for few-shot library (Phase 3), team-protocols JSON-contract refactor (Phase 2), upstream cache verification result (Phase 4)
- **Result:** plan now aligns with production context-engineering best practices for the agent-harness scope, with security baseline addressed at design time rather than retrofitted

---

## Round 4 — Deep critical review of all 7 docs (2026-04-26)

### N. Practical / pragmatic issues

#### N1. NEW skills list is INCOMPLETE — missing 5 workflow skills.
**Q:** Plan §2.1 NEW lists 12 skills. Workflow specs Part A defines 10 workflows. Of those 10, only 3 (feature-design, env-analyzer, ai-assets-init) appear in NEW. What about the other 7?
**A:** Mapping audit:
- `/feature-design` → NEW feature-design ✓ in plan
- `/develop` → ambiguous (see N2 below); not in NEW; not explicitly mapped
- `/bugfix` → REFACTOR existing `bugfix` ✓
- `/env-analyze` → NEW (named env-analyzer in plan, but slash command is /env-analyze — see N2)
- `/refactor` → MISSING from NEW; no existing skill of this name
- `/migrate` → MISSING from NEW; no existing skill of this name
- `/spike` → MISSING from NEW; no existing skill of this name
- `/security-audit` → MISSING from NEW; existing `security-scan` is sub-skill, not workflow
- `/docs-pack` → MISSING from NEW; existing `docs` is general docs help, scope differs
- `/ai-assets-init` → NEW ai-assets-init ✓

**Implication:** Five workflow skills (`refactor`, `migrate`, `spike`, `security-audit`, `docs-pack`) are described in 01-WORKFLOW-SPECS.md but missing from plan §2.1 disposition. Migration checklist B12 silently conflates them under item 123. Real skill count is wrong.

**Fix:** Add 5 missing skills to plan §2.1 NEW list. Update count: NEW 12 → 17. Update §7b plugin total: 47 → 52.

#### N2. Slash-command-to-skill-name mapping not documented.
**Q:** When user types `/develop`, which skill activates? Per Anthropic docs, slash commands match skill directory names. So `/develop` requires `plugin/skills/develop/SKILL.md`. But there's no skill called `develop` in either KEEP, REFACTOR, or NEW. Plan §4.2 says "/develop is evolution of existing team-dev" — does team-dev get RENAMED to develop, or is develop a new skill that calls team-dev as a sub-skill?
**A:** Three possible mappings, recommend the explicit one:
- **Option A (recommended): rename during refactor.** Refactor team-dev → develop. The directory is renamed; the skill IS the workflow. Aligns with the "slash command = skill name" pattern. team-dev disappears from plugin/skills/ as a name.
- Option B: keep team-dev, add thin develop skill that calls team-dev. Adds indirection without value.
- Option C: leave team-dev as is, add NEW develop. Confusing duplication.

Same question applies to:
- `/env-analyze` — current plan calls the skill `env-analyzer`. Slash command is `/env-analyze`. **Fix:** rename in NEW list to `env-analyze`.
- `/docs-pack` — should be NEW (existing `docs` keeps general scope as a knowledge skill).

**Fix:** Document the rename decisions in plan §2.1; update REFACTOR list to mark team-dev as "REFACTOR-RENAME → develop"; update NEW list to use `env-analyze`.

#### N3. Migration checklist B12 conflates 6 atomic skills under item 123.
**Q:** B12 lists "121 feature-design, 122 env-analyzer, 123 (also covered: refactor, migrate, spike, security-audit, docs-pack, ai-assets-init …)". Item 123 covers 6 separate skills. Are these one item or six?
**A:** They're six separate file-creation tasks. Conflation is a numbering bug — breaks the "atomic items" contract of the checklist.
**Fix:** Re-enumerate B12 atomically. If NEW=17 (per N1 fix), B12 will have items 121-137 (or however the numbering shakes out after R1).

#### N4. Duplicate item: `eval/config.json` appears in B1.7 (item 7) AND B10.4 (item 90).
**Q:** Same file referenced twice. Which batch creates it?
**A:** Real duplicate. B1.7 creates it as part of skeleton. B10.4 creates it again as part of eval scaffolding. One must go.
**Fix:** Remove B10.4 (item 90 in checklist). Keep B1.7. Renumber B10 items from 89 onwards to close the gap.

#### N5. Calibration sample data NOT included in checklist deliverables.
**Q:** `/plugin-doctor --calibrate-judge` (V2 final validation) requires 5 known-good and 5 known-bad reference outputs per rubric (per `02-EVAL-FRAMEWORK.md` §8). 17 rubrics × 10 samples = 170 calibration files. Where do they come from? The checklist creates `plugin/eval/calibration/` directory (B1.3) but NO items create the actual sample files.
**A:** This is a real gap. Without calibration data, /plugin-doctor cannot run the calibration check. Two options:
- **Option A (recommended):** ship 3-5 minimal samples per rubric (mix of synthetic + author-curated) at v0.1.0-alpha. Author them as part of B10 rubric authoring (each rubric file references a samples folder, and the samples are authored alongside).
- Option B: defer all calibration sampling to Phase 4 hardening; make `/plugin-doctor --calibrate-judge` a no-op in v0.1 with a "needs calibration data" warning.

**Fix (Option A):** add new batch B10a — Calibration Samples (170 files, ~3-5 per rubric). Each sample is a 50-200 line Markdown or JSON file showing expected output for the rubric, with a ground-truth score in the filename or frontmatter.

#### N6. Output directory convention has unexplained outlier.
**Q:** Workflows write outputs to:
- `/feature-design` → `<repo>/docs/features/<feature-id>/` (in target repo's docs/, NOT memory)
- All other workflows → `<repo>/.ai-assets-memory/<workflow-name>/<run-id>/`

Why is `/feature-design` the outlier?
**A:** Intentional: design packs are intended to be VERSIONED IN GIT as project documentation. Other workflows produce ephemeral logs. But this rationale is not documented in 01-WORKFLOW-SPECS.md.
**Fix:** Add a one-paragraph note to /feature-design Output schema explaining the exception. Same convention should apply to /docs-pack output (also user-facing docs).

### O. Architectural issues (deeper concerns)

#### O1. Recursive agent spawning — is it safe?
**Q:** feature-design-lead has `tools: Task` and spawns 6-10 subagents per workflow run. Can spawned agents themselves spawn more subagents? Could this recurse infinitely?
**A:** Audit of agent tools per checklist B5:
- `feature-design-lead` — `tools: Task` only (can spawn, can't do work)
- `security-engineer` — `tools: Read, Grep, Glob, Bash` (no Task → cannot spawn)
- `eval-judge` — `tools: Read, Grep, Glob` (no Task)
- `memory-curator` — `tools: Read, Write` (no Task)
- All 22 existing agents — none have Task in their tools list (verified by grep)

So recursion is bounded: only feature-design-lead spawns subagents, and those subagents (engineers, designers, etc.) cannot spawn further. **No risk in v0.1.**

For v0.2+ if other orchestrators get Task tool: add a max recursion depth guard via a new hook `subagent-depth-guard.py` that tracks depth via the `trace_id` chain in the spawn payload.

**No fix needed for v0.1.** Document the bounded-recursion guarantee in `subagent-isolation.md` rule.

#### O2. Hook type for memory-curator and eval-judge invocation.
**Q:** `pre-compact-memory-flush.py` (PreCompact hook) needs to invoke memory-curator agent synchronously. Same for eval-judge in eval Tier 3. Currently designed as `command` type Python scripts that wrap LLM calls. Modern Claude Code supports `agent` hook type that natively invokes a configured agent. Why use the wrapper?
**A:** Per H4 (round 2): we deferred `prompt`/`agent` hook type adoption to v0.2. Reason: minimize untested dependencies in v0.1. But for memory-curator specifically, `agent:` hook type is the natural fit and would eliminate ~50 lines of Python boilerplate.
**Fix:** Document in the checklist B8 hook table that pre-compact-memory-flush will migrate from `command` type to `agent:memory-curator` type in v0.2. Same for eval-judge invocations. Stay with `command` in v0.1 for risk reduction.

#### O3. PreCompact memory flush itself consumes tokens — does it trigger compaction?
**Q:** PreCompact hook fires when context approaches the window limit. The hook then INVOKES memory-curator (Haiku, ~5K token cap). But the memory-curator's input is the L3 session state (might be large). Could the hook's invocation push us past the limit before compaction can happen?
**A:** Risk is real but bounded:
- memory-curator runs in an ISOLATED subagent (per `Agent` tool semantics) with its own context window
- The 5K token cap is on memory-curator's OUTPUT, not input
- Input to memory-curator is L3 state file (read from disk), not the parent context — so it doesn't push the parent toward the limit
- Failure mode: if memory-curator itself fails (timeout, API error), we fall open per `00-PHASE-1-PLAN.md` §3.8 — log to hook-errors.log, allow compaction to proceed without flush

**No fix needed.** Document the isolation contract in `03-MEMORY-ARCHITECTURE.md` §11 — PreCompact mechanics already explains memory-curator runs synchronously but doesn't explicitly state "in isolated subagent context".

#### O4. /plugin-doctor self-test eval-judge before calibration data exists?
**Q:** First-run UX (per plan §5a): user installs plugin, runs `/plugin-doctor`. /plugin-doctor `--calibrate-judge` requires calibration samples. But on first install, no calibration samples have been verified by the user. Chicken-and-egg.
**A:** Two-step boot:
- `/plugin-doctor` (default, no `--calibrate-judge`): runs lint checks, hook executable check, runs jsonl parse — does NOT run judge calibration. Reports the calibration as "not yet run" with instructions.
- `/plugin-doctor --calibrate-judge`: explicit user command, runs the calibration. If samples exist (shipped per N5 fix), runs Spearman correlation. If not, errors clearly: "No calibration samples found at plugin/eval/calibration/. See <docs link>."

**Fix:** Document this in `01-WORKFLOW-SPECS.md` /plugin-doctor section. Make it explicit that `--calibrate-judge` is opt-in and not part of the default smoke test.

### P. Best-practices alignment recheck

#### P1. Should our eval framework integrate with Anthropic's skill-creator eval mode?
**Q:** Anthropic's `skill-creator` plugin (already exists, available as `anthropic-skills:skill-creator`) ships eval capability natively (Skills 2.0 Create/Eval/Improve/Benchmark modes). We're building our own eval framework. Are we duplicating?
**A:** Different scope:
- Anthropic's skill-creator eval is per-skill description optimization (description tuning, A/B activation tests)
- Our eval framework is workflow-level behavioral testing (executor + judge + blind-comparator + baseline tracking)

These are complementary, not duplicate. Our framework can DELEGATE description-optimization to skill-creator's eval mode where useful. Phase 3+ work.
**Fix:** Add a one-paragraph section to `02-EVAL-FRAMEWORK.md` §12 (Future work) noting: "Description optimization for individual skills will delegate to Anthropic's `skill-creator` plugin's Eval mode. Our eval framework focuses on workflow-level behavior; theirs on skill activation tuning. They are complementary."

#### P2. Skill description third-person verification.
**Q:** Plan §1.3 mandates third-person + "Use when …" pattern. Have we verified all 47 (now 52) plugin skills follow this?
**A:** Spot-checked humanizer, geo-writer, code-review — all conform. But we have not done a 100% audit. KEEP skills inherit from existing files which mostly conform (the skills were authored with this pattern in mind). REFACTOR skills will be rewritten — easy to enforce. NEW skills authored from spec — ditto.
**Fix:** Add to checklist B3 / B11 / B12 validation: explicit grep for `Use when` in every SKILL.md description; flag any missing.

### Q. Round 4 patches applied

| ID | Affected file | Change |
|---|---|---|
| Q1-N1 | 00-PHASE-1-PLAN.md §2.1 | Add 5 missing NEW workflow skills (refactor, migrate, spike, security-audit, docs-pack); rename env-analyzer → env-analyze; total NEW = 17, in-plugin = 52 |
| Q2-N2 | 00-PHASE-1-PLAN.md §2.1 REFACTOR list + 04-MIGRATION-CHECKLIST.md B11 | Mark team-dev as REFACTOR-RENAME → develop; document the rename; update B11 row |
| Q3-N1 | 00-PHASE-1-PLAN.md §7b counts | Update: skills 47 → 52 |
| Q4-N3 | 04-MIGRATION-CHECKLIST.md B12 | Re-enumerate atomically: 17 NEW skill items (was conflated under 121-132) |
| Q5-N4 | 04-MIGRATION-CHECKLIST.md B10 | Remove duplicate `eval/config.json` (B10.4 deleted; renumber B10 to close gap) |
| Q6-N5 | 04-MIGRATION-CHECKLIST.md NEW B10a | Add calibration samples batch — 3-5 samples per rubric × 17 rubrics |
| Q7-N6 | 01-WORKFLOW-SPECS.md /feature-design and /docs-pack Output schema | Add note: design/docs outputs go to `docs/` (versioned), workflow logs go to `.ai-assets-memory/` (gitignored) |
| Q8-O1 | plugin/rules/subagent-isolation.md (Phase 2 authoring spec) | Document the bounded-recursion guarantee for v0.1 |
| Q9-O2 | 04-MIGRATION-CHECKLIST.md B8 table | Add note: pre-compact-memory-flush + eval-judge invocation will migrate to native `agent:` hook type in v0.2 |
| Q10-O3 | 03-MEMORY-ARCHITECTURE.md §11 | Add explicit "memory-curator runs in isolated subagent context" sentence |
| Q11-O4 | 01-WORKFLOW-SPECS.md /plugin-doctor | Document two-step boot: default vs `--calibrate-judge` opt-in |
| Q12-P1 | 02-EVAL-FRAMEWORK.md §12 Future work | Add note: description optimization delegates to Anthropic skill-creator's Eval mode |
| Q13-P2 | 04-MIGRATION-CHECKLIST.md B3, B11, B12 validation | Add explicit "grep for `Use when`" to skill validation checklist |

---

## Round 5 — Deep review with explicit pre-flight checklist applied (2026-04-26)

**Methodology change:** before this round, I committed the recurring-error patterns from Rounds 1-4 to durable memory (`feedback_design_doc_quality.md`). Then ran a 10-item pre-flight checklist against all 7 docs. This is the first round done WITH the systematic checklist.

### S — Substantive issues found in Round 5

#### S1 [HIGH]. User-facing docs missing from migration checklist.
**Q:** Plan §3.1 layout shows `plugin/docs/getting-started.md`, `plugin/docs/workflows/<name>.md`, `plugin/docs/concepts/{memory,eval,ralf}.md`. Plan §5 Phase 2 lists them as deliverables. Are they in the migration checklist?
**A:** NO. Checklist B1.3 creates empty `plugin/docs/workflows/` and `plugin/docs/concepts/` directories. B1.4 creates `plugin/README.md`. But the actual user-facing docs files (getting-started.md, 19 workflow docs, 3 concept docs) are NOT in any batch. Real gap.
**Fix:** Add NEW Batch B13 — User-Facing Documentation. Items for getting-started.md (1 file), per-workflow user docs (19 files for the 19 user-invocable skills), concept docs (memory.md, eval.md, ralf.md = 3 files). Total: 23 new doc files.

#### S2 [MEDIUM]. Hook helper `_normalize_hook_input()` not extracted as a shared module.
**Q:** Checklist B8 says "Use the shared `_normalize_hook_input()` helper from existing scripts (carry pattern over)". Does this mean copy-paste across 15 hook scripts, or extract to a shared module?
**A:** Currently ambiguous. Best practice is extract: `plugin/hooks/scripts/_lib.py` exports `normalize_hook_input()`, and each script imports it. Avoids 15-way duplication.
**Fix:** Add B8.0 (item 64a or insert before B8.1): create `plugin/hooks/scripts/_lib.py` with `normalize_hook_input()` and helpers (PII filter helper, untrusted-content wrapper helper, JSON I/O helper). All hook scripts import from it.

#### S3 [HIGH]. ARCHIVE skills have no Phase 5 sunset plan.
**Q:** 5 ARCHIVE skills stay in legacy `.claude/`. Plan §5 Phase 5 says "Move .claude/, .codex/, .windsurf/, .agents/ to archive/" — but doesn't address what happens to references to those archived skills, nor whether/how users get migration guidance.
**A:** Real gap. When `.claude/` moves to `archive/` in Phase 5, the 5 ARCHIVE skills become orphaned. Users invoking `/ai-assets` (the legacy archived skill) get no clear migration message.
**Fix:** Plan §5 Phase 5 should include: (a) author `archive/MIGRATION.md` documenting "skill X removed → use Y instead" for each of the 5 archived skills; (b) v0.3.0 release note mentions archive migration; (c) optional: add deprecation hooks in v0.2 that warn when legacy skills are invoked (low priority since we control distribution).

#### S4 [MEDIUM]. Plan §5 phase numbering conflicts with user's mental model.
**Q:** User said "переходим к фазе 2" intending Phase 2 = implementation start. Plan §5 calls implementation "Phase 1 — Core scaffolding". User's mental model: Phase 1 = design (00-05 docs), Phase 2 = implementation. Plan §5 model: Phase 0 = Foundations (design), Phase 1 = Core scaffolding, Phase 2 = Workflows.
**A:** These are inconsistent and confused us during the most recent turn.
**Fix:** Reconcile to user's mental model. Update plan §5 phase labels:
- "Phase 1 (DESIGN, complete)" — was Phase 0
- "Phase 2 (Implementation: Core scaffolding)" — was Phase 1; covers checklist B1-B10a
- "Phase 3 (Implementation: Workflows + user docs)" — was Phase 2; covers checklist B11-B13
- "Phase 4 (Hardening + dogfooding)" — was Phase 4 (no change)
- "Phase 5 (Sunset legacy)" — was Phase 5 (no change)
- Original "Phase 3 (Eval Tier 2+3)" merged into Phase 4 hardening

#### S5 [MEDIUM]. Eval framework still references `disallow_skills` field — clarify mechanism vs intent.
**Q:** Round 3 changed blind-comparator from `skills: []` (mechanism) to instruction-based suppression. But `disallow_skills` field in eval case JSON still exists (lines 206, 262, 874, 1054 of 02-EVAL-FRAMEWORK.md). Stale or still meaningful?
**A:** Still meaningful — the FIELD declares INTENT (which skills to suppress for blind-comparator). The MECHANISM that uses the field changed (Round 3 fix). Field stays; we just need to clarify in the field documentation that the suppression is now instruction-based, not via subagent frontmatter.
**Fix:** Add 1-sentence note to `disallow_skills` field documentation in §3.6 of 02-EVAL-FRAMEWORK.md: "Note: as of Round 3, suppression mechanism is instruction-based prompt prefix in an isolated subagent (per §7), not subagent frontmatter `skills: []` (which doesn't reliably suppress activation). The field declares intent; mechanism is owned by the eval runner."

#### S6 [MEDIUM]. Hook ordering not enforced explicitly beyond array order.
**Q:** Checklist B8 says "tool-output-wrap.py MUST fire before tool-output-normalize.py on PostToolUse". Mechanism: array order in hooks.json. But what if a future maintainer reorders without realizing? No assertion at runtime.
**A:** Real risk for v0.2+ when more hooks are added. Cheap fix: add a runtime assert in tool-output-normalize.py — check that previous hook in the chain emitted the wrap envelope marker; abort with clear error if not.
**Fix:** Document in Plan §1.7 hooks reference and Checklist B8 description: tool-output-normalize.py reads `wrap_marker` from previous hook's stdout/env; aborts if missing. This makes ordering self-documenting and self-enforcing.

#### S7 [LOW]. Plugin install path UX has 3 different forms — no canonical guidance.
**Q:** Different docs reference: `claude plugin install ./plugin` (dev), `claude plugin install <git-url>` (README), `claude plugin install ai-assets/ai-assets` (marketplace future). Which is canonical for the user's expected install method?
**A:** All three are valid for different stages. README should make the precedence clear: marketplace (after v0.2 publish) > git URL > local path (dev only).
**Fix:** Update Plan §5a Distribution & Install — explicit precedence + each method's intended audience.

#### S8 [MEDIUM]. `~/.claude/ai-assets/` for L5 — verify no collision with Claude Code internal paths.
**Q:** Claude Code itself manages `~/.claude/`. We're creating `~/.claude/ai-assets/`. Could it collide with future Claude Code internal paths?
**A:** Per current Claude Code docs (verified), Claude Code uses these paths under `~/.claude/`: `agents/`, `skills/`, `plugins/`, `themes/`, `output-styles/`, `settings.json`, `projects/`, `commands/`. Our `ai-assets/` doesn't collide. But it COULD if Claude Code adds a future feature called "ai-assets". Low risk but worth documenting.
**Fix:** Add a note in 03-MEMORY-ARCHITECTURE.md L5 section: "L5 path is `~/.claude/ai-assets/learnings.md`. As of 2026-04-26, no collision with Claude Code-managed paths under `~/.claude/`. If Claude Code future-introduces a managed `ai-assets` directory, migrate L5 to `~/.claude/plugins-data/ai-assets/learnings.md` or similar."

#### S9 [HIGH]. B12 validation skipped: "Use when" grep is for user-invocable skills, but expected count of 19 may be wrong.
**Q:** Round 4 added validation: `grep -l "Use when" plugin/skills/*/SKILL.md | wc -l` → 19. But:
- Some KEEP skills are knowledge-only and don't have "Use when" trigger (e.g., context-engineering, prompt-engineering, cloud-platforms)
- Knowledge skills have descriptions but no slash command, so they don't NEED the trigger pattern
- The "19 user-invocable" number requires identifying which skills are user-invocable
**A:** Validation is wrong as written. `grep "Use when"` will match any skill that uses those words anywhere in description. Some KEEP skills DO use "Use when" in their descriptions (e.g., humanizer, geo-writer per existing audit). So the actual grep count could be higher or lower than 19 depending on KEEP skill descriptions.
**Fix:** Replace the validation with: "Every USER-INVOCABLE skill (`grep -l 'user-invocable: true\|context: fork' plugin/skills/*/SKILL.md`) MUST also contain 'Use when' in description. Pure knowledge skills are exempt."

#### S10 [LOW]. V validation doesn't check L1 templates exist.
**Q:** Final V4 lists asset counts but doesn't verify all 8 L1 memory templates (B9 items 79-86) exist in `plugin/memory/templates/`.
**A:** Real gap. Should add explicit count check.
**Fix:** Add to V4: `ls plugin/memory/templates/ | wc -l` → 7 (since pii-patterns.txt lives in hooks/scripts/, not memory/templates/, only 7 are in memory/templates/).

#### S11 [LOW]. Some checklist validation steps reference future commands that don't exist yet.
**Q:** Checklist V4 says `claude plugin validate ./plugin`. This command exists per Anthropic docs. ✓. But B12 validation says `python3 plugin/eval/runner.py --tier 1 --all` requires runner.py to exist (created in B10.3). Sequence is correct: B10 runs before B12. ✓. So actually no issue.
**A:** Verified OK.
**Fix:** None needed. Just verifying I checked dependency ordering.

### T — Process improvement suggestions

After 5 rounds of self-review, here are concrete process changes that would have prevented most issues:

#### T1. Build a glossary file as single source of truth.
Create `plugin-design/_glossary.md` listing every entity (skill, agent, rule, hook, file path, slash command, version, count) with its canonical name, disposition, and which doc owns its full spec. Every other doc REFERENCES the glossary instead of restating. Updates happen once.

#### T2. Use a critic subagent for adversarial review.
Spawn a subagent (general-purpose or code-reviewer) with a focused brief: "Read all 7 docs in plugin-design/ and find inconsistencies, gaps, contradictions. Report ranked by severity." Different perspective catches things I systematically miss.

#### T3. Apply pre-flight checklist before declaring complete.
The 10-item checklist in `feedback_design_doc_quality.md` (now in memory). Run it BEFORE asking user for review. Several rounds would have surfaced fewer issues if I'd run the checklist first.

#### T4. Re-fetch Anthropic upstream docs at end of each phase.
Anthropic ships features weekly per ai-expert skill. Round 2 found 9 missed plugin features documented at the same Anthropic page I read at start. Re-fetch at phase boundaries to catch new features.

#### T5. Smaller atomic edits with verification gates.
Instead of "apply 25 patches in one batch" (Round 1), do 5 patches + grep verification + read-back, then next 5. Easier to catch breakages mid-way.

#### T6. Build a quality-gate skill that runs all checks programmatically.
A `/plugin-design-doctor` skill (or part of `/plugin-doctor`) that:
- Cross-doc count consistency
- Reference integrity
- Glossary entity match
- Forbidden field check (e.g., `permissionMode` in plugin agents)
- Math sweeps
- Best-practices version check

Run before EVERY commit or PR open.

#### T7. Review with explicit phase-end gates, not ad-hoc.
Define "Phase 1 design complete" with specific criteria (counts, references, validation). Only when all criteria pass, declare complete. Currently we've declared Phase 1 complete 5 times and found new issues each time — clearly the criteria weren't strict enough.

#### T8. Author iteratively with a feedback loop.
Don't author all 7 docs then review. Author one, run pre-flight, then next. Compounding errors are cheaper to catch early.

### U — Round 5 patches applied

| ID | Affected file | Change |
|---|---|---|
| U1-S1 | 04-MIGRATION-CHECKLIST.md NEW B13 | Add User-Facing Documentation batch — getting-started.md + 19 workflow docs + 3 concept docs (23 files) |
| U2-S2 | 04-MIGRATION-CHECKLIST.md B8 | Add `_lib.py` shared module item; all hook scripts import from it |
| U3-S3 | 00-PHASE-1-PLAN.md §5 Phase 5 | ARCHIVE sunset plan: archive/MIGRATION.md guidance per archived skill |
| U4-S4 | 00-PHASE-1-PLAN.md §5 | Reconcile phase numbering to user mental model (Phase 1 = design, Phase 2 = implementation) |
| U5-S5 | 02-EVAL-FRAMEWORK.md §3.6 | Add note clarifying disallow_skills = intent declaration; mechanism is instruction-based suppression |
| U6-S6 | 04-MIGRATION-CHECKLIST.md B8 | Add wrap-marker assertion in tool-output-normalize.py for self-enforcing hook ordering |
| U7-S8 | 03-MEMORY-ARCHITECTURE.md L5 section | Add note about ~/.claude/ paths verified non-collision + future migration path if needed |
| U8-S9 | 04-MIGRATION-CHECKLIST.md B12 validation | Fix "Use when" check: scope to user-invocable skills only |
| U9-S10 | 04-MIGRATION-CHECKLIST.md V4 | Add L1 templates count check |

---

## Round 6 — Process improvements applied + critic-subagent adversarial review (2026-04-26)

### W. T1-T8 process improvements built and operationalized

User accepted Round 5 process recommendations T1-T8 ("делаем полностью все T1-T8"). Built:
- **T1 — `_glossary.md`** (single source of truth for entities, counts, file paths, decisions, ID namespaces). 290+ lines. First entity check it forced: discovered userConfig is 8 knobs, not 7.
- **T6 — `plugin-design-doctor.py`** (programmatic checks: counts, refs, glossary, forbidden fields, namespace, todos, leaks). ~420 lines. Runs via `python3 plugin-design-doctor.py [--strict] [--check NAME]`. Found 1 real error + ~50 informational warnings on first run.
- **T7 — `_phase-gate-criteria.md`** (explicit pass/fail per phase: Phase 1 has 21 criteria across programmatic + manual + critique-trail audit). Replaces "ad-hoc complete" with verifiable gate.
- **T3+T5+T8 — `_process.md`** (consolidated authoring/review process: pre-flight checklist before user review, atomic edits in batches ≤5, iterative authoring per-doc).
- **T4 — Re-fetched Anthropic docs**, captured findings as `05-CONTEXT-ENGINEERING-GAP-ANALYSIS.md` Appendix A (A1-A7). Notable: PostToolUse now provides `duration_ms`, prompt caching has 1-hour and 5-min controls, Opus default effort is now `xhigh` (applied to feature-design-lead).
- **T2 — Critic subagent** spawned with adversarial brief, found 10 NEW issues not in any of Rounds 1-5 self-reviews.

### X. Critic-subagent findings (Round 6)

| ID | Severity | Issue | Status |
|---|---|---|---|
| CRIT-1 | crit | feature-design-lead permission paradox (Task only + disallowedTools Write/Edit/Bash but workflow writes 8+ files) | Resolved by clarifying delegation pattern: orchestrator spawns subagents that DO have write tools |
| HIGH-1 | high | B10a "34 or 102" hedge unresolved — which ships in v0.1? | **APPLIED**: 34 minimal in v0.1, 102 in Phase 3 (deterministic) |
| HIGH-2 | high | Memory-curator missing operational contract (spawn-only? path constraint mechanism? rule references?) | **APPLIED**: full operational contract added in B5.4 |
| HIGH-3 | high | RALF session-aggregate budget undefined (chained workflows can burn 900K+ tokens unchecked) | **APPLIED**: session-level caps 20 iter / 400K tokens / 3h added to plan §3.5 + 3 new userConfig knobs (need to update glossary §7 to 11 knobs total — DEFERRED to glossary-sync step) |
| HIGH-4 | high | Subagent return-contract validation has no error-path spec | **APPLIED**: explicit fail-open spec in B8 hook table for subagent-stop-learnings.py |
| MED-1 | medium | Eval rubric matrix not visualized — reader can't easily map workflows ↔ rubrics | DEFERRED to Phase 2 docs polish |
| MED-2 | medium | V2 final validation requires calibration ≥0.7 but elsewhere `--calibrate-judge` is opt-in | **APPLIED**: V2 reworded to make calibration opt-in (not gate-blocking) |
| MED-3 | medium | B11/B12 ordering — context-load contract referenced by /feature-design (B12.1) before authoring | DEFERRED: minor clarity issue, add forward reference in B11 header in Phase 2 |
| LOW-1 | low | Glossary userConfig count off-by-one (7 vs 8) | **APPLIED**: glossary §1 + §7 + §3.2 updated to 8 |
| LOW-2 | low | plugin-skill-create scope rationale not documented | DEFERRED: Phase 2 doc polish |

### Y. Round 6 net result

- Process scaffolding shipped: glossary, doctor, phase gates, process notes
- Critic-subagent ROI confirmed: found 10 NEW issues (3 crit/high applied immediately, 4 high/med applied, 3 deferred)
- Fixes applied via Round 6: 6 of 10 (calibration count, memory-curator contract, RALF aggregate, return-contract validation, V2 calibration, userConfig count)
- Deferred to Phase 2 polish: 4 (rubric matrix, B11/B12 ordering note, plugin-skill-create rationale, plus glossary §7 needs to reflect 11 userConfig knobs after RALF aggregate addition)
- Process effect: future rounds should find < 5 issues thanks to glossary + doctor + pre-flight discipline
- **Open: glossary count cascade.** HIGH-3 added 3 new userConfig knobs (ralph_session_max_iter, ralph_session_token_budget, ralph_session_time_cap). Glossary §1 + §7 still say 8 knobs; need to update to 11 in next sync. Marked as TODO in critique trail.
