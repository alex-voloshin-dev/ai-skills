---
name: team-protocols
description: Shared protocols for multi-agent team coordination — execution model, named subagent spawning via the Agent tool, file conflict prevention, developer/reviewer/lead protocols, role selection table, G7 spawn payload + return contract schemas. Referenced by multi-agent workflow skills (`/develop`, `/team-bugfix`, `/feature-design`). Not directly user-invoked. Use when authoring or auditing a multi-agent skill that spawns named subagents.
---

# Multi-Agent Orchestration

Base protocols for coordinating a team of named subagents in Claude Code. This skill is not invoked directly — it is referenced by workflow skills via `@team-protocols`.

## CRITICAL — orchestration skills MUST NOT use `context: fork`

Per Anthropic Claude Code docs:

> "Subagents cannot spawn other subagents."

When a workflow skill has `context: fork` in its frontmatter, Claude Code runs the entire skill body inside a **forked subagent** (typically `general-purpose`). Inside that subagent, the `Agent` tool is unavailable — and the orchestration pipeline this protocol defines cannot execute. The skill will detect the missing primitive and either HALT or fall back to inline single-agent work, leaving the user wondering why the multi-agent pipeline never ran.

**Rule**: any skill that follows this protocol (spawns Developer / Reviewer / QA via the `Agent` tool) MUST NOT have `context: fork` in its frontmatter. The skill must run in the main conversation thread to retain access to the `Agent` tool.

Confirmed alpha.25 failure mode: `develop` / `team-bugfix` / `feature-design` initially shipped with `context: fork` (intent: isolate skill body from main context). User ran `/ai-assets:develop`, Claude Code forked into a `general-purpose` subagent, the subagent had no `Agent` tool, the skill correctly identified this and refused to do the work inline. Fix: removed `context: fork` from all three orchestration skills. They now run in the main thread where `Agent` is available.

`feature-dev` (single-agent fallback that does the work itself, no spawning) keeps `context: fork` — that's correct, it doesn't need to orchestrate.

## Execution Model

You are the Lead. You run in the main conversation thread and coordinate the team by spawning named subagents via the **`Agent` tool** (Claude Code's canonical primitive for delegating work to an isolated context).

**Hard invariant**: every agent role MUST run as a NAMED subagent spawned via `Agent`, with its own isolated context. The Lead (main thread) NEVER executes Developer / Reviewer / QA work inline with `Bash`/`Read`/`Edit`. If you skip the spawn and do the work directly in the main thread, you have violated this protocol — the user loses the ability to inspect each role independently and the pipeline gates collapse to procedural-only enforcement.

> **Common failure mode (observed alpha.23):** the skill body describes roles ("Agent 1 — Developer", "Agent 2 — Reviewer") but never issues a literal `Agent(...)` call. The model treats the description as documentation and proceeds inline with `Bash`/`Read`/`Edit`. The fix: every role-spawn step in this protocol contains an explicit `Agent({...})` invocation example that the workflow MUST execute, not paraphrase.

## The Agent Tool — Canonical Primitive

Per [Claude Code docs](https://docs.claude.com/en/docs/claude-code/sub-agents), subagents are spawned via the `Agent` tool. The Lead invokes it directly:

```text
Agent({
  description: "<short label shown in transcript>",
  subagent_type: "<plugin-name>:<agent-name>"  OR  "<built-in-name>",
  prompt: "<full role brief, including the G7 spawn payload as JSON>"
})
```

### How `subagent_type` resolves

- **Plugin agents** (the 26 specialized agents this plugin ships) — use the scoped form: `ai-assets:java-engineer`, `ai-assets:frontend-engineer`, `ai-assets:qa-engineer`, etc. The `<plugin-name>` prefix is the `name` field from `plugin/.claude-plugin/plugin.json` (`ai-assets`); the `<agent-name>` is the `name` frontmatter from `plugin/agents/<file>.md`.
- **Built-in subagents** — `general-purpose`, `Explore`, `Plan`, `statusline-setup`. Use `general-purpose` as the universal fallback when a more specific role is unavailable.

### Hard constraints (per Anthropic docs)

1. **Subagents cannot spawn other subagents.** All orchestration MUST happen in the Lead (main thread). The Developer / Reviewer / QA subagents you spawn cannot themselves spawn more agents.
2. **Each `Agent` call creates fresh context.** No conversation history is shared with the spawned subagent unless you put it in the `prompt`. Pass everything the role needs to know.
3. **Spawn results return to the Lead, not to other subagents.** The Lead is the message bus.

## Two Paths — Subagents OR Agent Teams

Two execution paths are supported. Both preserve the DEV → REVIEW → QA gate semantics — only the execution mechanism differs.

**Default preference: Path B (Agent Teams).** It gives the user a visual team panel, Shift+↓ to switch context into any teammate, dedicated transcript per role, and a shared task list with `dependsOn`. Use Path B unless a hard technical block prevents it.

**Hard technical block** = the natural-language team creation in Path B Step 1 actually fails (Anthropic Agent Teams API not exposed in the current Claude Code session, typically because `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` is not set). In that case, silently fall back to Path A and continue without re-asking the user.

**Detection is implicit, not explicit.** Do NOT run an explicit env-var check (no `echo $CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` Bash call) — that triggers a tool-permission prompt for the user without adding value. Just attempt Path B Step 1 directly. If it succeeds you're in Teams mode. If it returns "Agent Teams not enabled" or similar, fall back to Path A immediately and proceed.

### Path A — Subagents (always available, sequential)

This is the canonical path. Per role:

```text
Agent({
  description: "<short label>",
  subagent_type: "ai-assets:<role>",
  prompt: "<full role brief + G7 spawn payload>",
  isolation: "worktree"   # optional, for parallel-safe Developer work
})
```

The Lead waits for each `Agent` return, validates the G7 return contract, then proceeds to the next role. See **Spawn Pattern (concrete, executable)** below for the full per-role recipe.

Pros: works in every Claude Code environment; lower token cost than Teams. Cons: sequential by default; no inter-teammate messaging; no visual panel.

### Path B — Agent Teams (experimental, when flag is on)

Per [Anthropic Agent Teams docs](https://docs.claude.com/en/docs/claude-code/agent-teams), the Lead drives the team via natural language. Each teammate is a full Claude Code session with its own context, and the user can switch between teammates with **Shift+↓**, view their transcripts with **Enter**, and toggle the shared task list with **Ctrl+T**.

**Step 1 — create the team** (natural language to self):

```text
Create an agent team named "<feature-slug>-team" with the following teammates, all using subagent definitions from the ai-assets plugin so they inherit the right tools and model:

- "developer" (ai-assets:<java-engineer | python-engineer | frontend-engineer | ...>) — implements work packages, follows the developer protocol from plugin/skills/team-protocols/developer-protocol.md
- "reviewer" (ai-assets:software-engineer) — independent code review, read-only (no Write/Edit), follows reviewer-protocol.md
- "qa" (ai-assets:qa-engineer) — higher-level tests + SRE smoke, follows the QA section of the develop skill

Require plan approval for the developer teammate before they make any changes. Use the shared task list to coordinate work packages — one task per WP, with `dependsOn` linking review/QA tasks to their developer task.
```

Per Anthropic docs, this prompt makes Claude:
- Create a team with the named teammates
- Spawn each teammate using the listed `ai-assets:<role>` subagent definitions (the definition's tools + model + body apply, augmented with team coordination tools)
- Auto-resolve task dependencies — the QA task unblocks when its developer + review tasks complete

**Step 2 — drive work** by populating the shared task list. One task per work package, with three tasks per WP (DEV, REVIEW, QA) linked via `dependsOn`.

**Step 3 — gate enforcement** — same DEV → REVIEW → QA invariants as Path A, enforced via the task list's dependency graph instead of sequential `Agent` returns. The reviewer's task auto-claims when the developer's task completes; QA's auto-claims when reviewer's completes; if any reviewer rejects (verdict `changes_requested`), the Lead inserts a follow-up developer task and re-points the review/QA dependencies.

**Step 4 — final cleanup** — when all WPs complete the pipeline, ask the lead to "clean up the team" (per Anthropic docs, always done from the lead).

Pros: visual team panel, parallel teammates, switchable contexts, direct messaging. Cons: experimental; higher token cost (each teammate is a full Claude session); requires `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`.

### Hard rule for both paths

Whichever path is active, the Lead NEVER does Developer/Reviewer/QA work inline with `Bash`/`Read`/`Edit`. The role-isolation invariant applies in both modes — only the spawn mechanism differs.

### Hard rule for path selection — no rationalised downgrade

**Path B is the preferred path. Falling back to Path A is acceptable ONLY when Path B technically fails (no silent fallback for any other reason).**

Observed failure modes (do NOT repeat any of these):

- **alpha.26/27 — pipeline-shape rationale**: model attempted Path B, then rationalised "the pipeline is sequential anyway, Path A gives cleaner visibility" and silently switched. WRONG.
- **alpha.30 — tmux rationale**: model on Windows host claimed "Path B requires tmux/iTerm2 which isn't available" and fell back to Path A. WRONG. Per [Anthropic agent-teams docs](https://docs.claude.com/en/docs/claude-code/agent-teams), Agent Teams supports two display modes:
  - **`in-process`** — all teammates in one terminal, **Shift+↓** to cycle through. **Works in any terminal, NO extra setup, NO tmux, NO iTerm2 required.** This is the default fallback.
  - **`tmux`** (split panes) — optional enhancement when tmux or iTerm2 is available. Each teammate gets its own pane.

  When tmux/iTerm2 is unavailable (e.g., Windows host without WSL), Path B still works in `in-process` display mode. The Lead MUST pass `teammate-mode in-process` in the team-creation prompt and proceed. Do NOT downgrade to Path A.

Path B's value is user-facing UX, not parallelism:

- **Visual team panel** in the terminal — user sees all teammates at once (works in in-process mode too — the panel is below the prompt input)
- **Shift+↓ to switch context** into any teammate's transcript (works in in-process mode)
- **Direct messaging** — user can intervene with any teammate via Enter (works in in-process mode)
- **Dedicated transcript per role** — reachable from the panel, not just disk
- **Shared task list** with `dependsOn` graph — pipeline visible as a tracked artifact

These benefits apply EVEN when work is sequential AND when tmux is unavailable. **Invalid reasons to choose Path A** (do NOT use these as fallback rationale):

- "the pipeline is sequential, Path B's parallelism doesn't help" — INVALID, Path B's value is UX
- "Path A gives cleaner visibility" — INVALID, Path B's panel gives strictly more
- "fewer tools to manage" — INVALID
- "tmux/iTerm2 not available on this host" — INVALID, Path B has `in-process` display mode that works on every terminal including Windows without WSL
- "split-pane mode unavailable" — INVALID, that's an optional enhancement; in-process mode always works
- "Windows host" / "no Unix tools" — INVALID, Agent Teams is platform-independent in `in-process` mode

The ONLY valid Path A trigger is a hard technical block detected during Path B Step 1 (team-create natural language returns "Agent Teams not enabled" / "experimental flag not set" / equivalent — typically because `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` env var is unset). In that case, fall back silently and continue — do not re-ask the user.

Display-mode unavailability is NEVER a valid Path A trigger. Always default to `teammate-mode in-process` if tmux/iTerm2 is uncertain.

## Spawn Pattern (concrete, executable)

Every Developer / Reviewer / QA role-step in a workflow follows this exact pattern:

### 1. Build the G7 spawn payload (JSON, conforms to `plugin/schemas/spawn-payload.schema.json`)

```json
{
  "trace_id": "wf-20260429-develop-wp03-spawn-001",
  "subagent_role": "java-engineer",
  "goal": "Implement WP-3 (preserve visibility_score in optimistic-lock retry) per the approved plan section 3a.",
  "constraints": [
    "Follow project conventions in src/main/java/com/f4ai/report/",
    "Use the existing OptimisticLockHandler; do not create a new one",
    "Match the test patterns in src/test/java/com/f4ai/report/repository/"
  ],
  "state_slice": {
    "active_files": [
      "src/main/java/com/f4ai/report/repository/ReportRepository.java",
      "src/main/java/com/f4ai/report/service/ReportService.java"
    ],
    "current_branch": "fix/visibility-score-null"
  },
  "allowed_tools": ["Read", "Grep", "Glob", "Bash", "Write", "Edit"],
  "budget": {
    "max_input_tokens": 50000,
    "max_output_tokens": 2000,
    "max_tool_calls": 30,
    "max_turns": 10,
    "timeout_ms": 600000,
    "retry_budget": 1
  },
  "untrusted_inputs": [
    {"source": "L4:.committed/conventions.md", "wrapped": true}
  ]
}
```

### 2. Invoke the `Agent` tool with the role brief embedding the payload

```text
Agent({
  description: "WP-3 implementation (java-engineer)",
  subagent_type: "ai-assets:java-engineer",
  prompt: "You are the Developer subagent for work package WP-3. Read the developer protocol at plugin/skills/team-protocols/developer-protocol.md before starting. Your G7 spawn payload:\n\n<JSON-from-step-1>\n\nWhen done, return a G7 return contract (per plugin/schemas/return-contract.schema.json) summarizing files changed, tests added, and any risks.",
  isolation: "worktree"   // optional — gives the Developer an isolated git worktree for safer parallel work
})
```

### 3. Wait for the return value, validate it against the return-contract schema

The `subagent-stop-learnings.py` hook validates each return. On schema violation, treat the return as `status: failed` per `failure-recovery.md` and re-spawn with a corrected prompt.

### 4. Pass the relevant slice to the next role

Reviewer gets: list of files changed, the diff (via Read tool in main thread), the work package brief, and the developer's summary. Do NOT pass the developer's entire transcript.

## Role-by-role spawn map

For a typical `/develop` work package:

| Step | Role | `subagent_type` | Notes |
|---|---|---|---|
| 1 | Developer (per stack) | `ai-assets:java-engineer` / `ai-assets:python-engineer` / `ai-assets:frontend-engineer` / etc. — pick from `role-selection-table.md` | One Developer per affected subproject; sequential code-modification gate per `subagent-isolation.md` |
| 2 | Reviewer | `ai-assets:software-engineer` | Read-only via `disallowedTools: ["Write", "Edit"]` in the `Agent` call |
| 3 | QA | `ai-assets:qa-engineer` | Higher-level tests only — Developer owns unit tests |

If a more specific specialized agent is unavailable in this plugin install, fall back to `subagent_type: "general-purpose"` and put the role brief entirely in the prompt.

## Communication Rules

- Every agent reply is the literal return value of an `Agent` tool call. **Never paraphrase or simulate an agent's response.**
- The Lead orchestrates, tracks progress, prints status tables, enforces gates. The Lead does NOT do Developer / Reviewer / QA work itself.
- If a return contract is missing fields required by the next role's protocol — reject it and re-spawn the originating role with a corrected prompt before the next role starts.
- All HANDOFF data flows through the return contract's `result` field as structured JSON, not as free-form prose.

## G7 Spawn Payload + Return Contract (typed contracts)

### Spawn Payload (Lead → Subagent)

Every spawn embeds the JSON payload conforming to `plugin/schemas/spawn-payload.schema.json` (full example above). The `subagent-start-budget.py` hook validates the payload and enforces the budget against the session token meter.

### Return Contract (Subagent → Lead)

Every subagent return embeds a JSON contract conforming to `plugin/schemas/return-contract.schema.json`:

```json
{
  "trace_id": "wf-20260429-develop-wp03-spawn-001",
  "status": "ok",
  "tokens_used": {"input": 38421, "output": 1872},
  "tool_calls": 14,
  "result": {
    "summary": "Implemented optimistic-lock retry preserving visibility_score; 8 unit tests added.",
    "files_changed": [
      "src/main/java/com/f4ai/report/service/ReportService.java",
      "src/test/java/com/f4ai/report/service/ReportServiceTest.java"
    ],
    "diff_size_lines": 142
  },
  "evidence": [
    {"artefact_id": "src/main/java/com/f4ai/report/service/ReportService.java", "quote": "if (existing.getVisibilityScore() != null) { updated.setVisibilityScore(existing.getVisibilityScore()); }", "span": "lines 87-89"}
  ],
  "risks": ["depends_on_concurrent_write_isolation_level_serializable"],
  "next_actions": ["reviewer: confirm visibility_score is also preserved on the upsert path"]
}
```

The `subagent-stop-learnings.py` hook validates this return against the schema. On validation failure, the Lead receives a stderr diagnostic and treats the return as `status: failed`.

### When `status: needs_clarification`

If the subagent halts awaiting user input, the return contract MUST include a `needs_clarification` field with the question. The Lead surfaces it to the user verbatim before re-spawning.

## Agent and File Conflict Prevention

**Single instance per role** — except Developers, where one instance per affected subproject stack is allowed (see `role-selection-table.md`). Do NOT spawn multiple Reviewers or multiple QA agents. Tasks within a role are processed strictly one at a time, sequentially.

**Only ONE agent may edit files at any time.** Agents take turns — never work on files in parallel.

- **Writing agents**: Developer(s) and QA (if the workflow includes higher-level test edits). Reviewer is always read-only (`disallowedTools: ["Write", "Edit"]` in the spawn).
- **If multiple Developers are spawned**: each gets `isolation: "worktree"` so they edit isolated copies and merge serially.
- **Workflow per task is strictly sequential**: Developer works → Developer returns → Reviewer reads → (QA works if applicable) → next task.
- **No overlap**: Developer MUST NOT be re-spawned for the next task while another writing agent is still active on the current task.
- **Lead enforces**: if two writing agents would be concurrent — the Lead waits for the first to return before spawning the second, and reports the queue state to the user.

## Protocols

Apply these protocols to all agents in the team:

- **Developer protocol**: `developer-protocol.md` — task implementation, self-verification, handoff format, review iterations
- **Reviewer protocol**: `reviewer-protocol.md` — independent verification, ghost change detection, issue reporting
- **Lead protocol**: `lead-protocol.md` — orchestration, progress tracking, escalation, final summary
- **Role selection**: `role-selection-table.md` — subproject-to-developer mapping and spawning rules

## Integration

- **Used by**: `/develop`, `/team-bugfix`, `/feature-design` (multi-agent workflows)
- **Schemas**: `plugin/schemas/spawn-payload.schema.json`, `plugin/schemas/return-contract.schema.json` (G7 contracts)
- **Hooks**: `subagent-start-budget.py` (validates spawn payload + enforces budget), `subagent-stop-learnings.py` (validates return contract + opt-in learnings capture)
- **Rules**: `subagent-isolation` (delegation patterns + bounded recursion), `untrusted-content-wrapping` (G1 wrap on subagent returns)
- **Reference**: [Anthropic Claude Code subagents documentation](https://docs.claude.com/en/docs/claude-code/sub-agents)
