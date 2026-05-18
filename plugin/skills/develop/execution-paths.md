# Develop — Execution Paths & Spawn Mechanics

Detailed mechanics for the `develop` multi-agent pipeline. The Lead **MUST
read this file before issuing the first spawn or driving any WP** — it carries
the G7 spawn worked example, the full Path B / Path A step sequences, and the
per-task hard-locked QA mode. `SKILL.md` keeps the orchestration overview and
the binding Gate Rules; this file keeps the executable detail. Behavior is
identical to the prior single-file form — nothing here is optional.

## G7 spawn payload — worked example

Every `Agent({...})` `prompt` MUST embed a JSON payload with all six G7
fields. The `subagent-start-budget.py` hook tolerates two warnings per
session, then **blocks** the third spawn with a diagnostic until the payload
is corrected. Free-form prose prompts are protocol violations —
`prompt: "Implement WP-3"` is rejected.

Worked example (paste into the `prompt` argument verbatim, then continue with
the role brief):

```text
Agent({
  description: "WP-3 implementation (java-engineer)",
  subagent_type: "ai-skills:java-engineer",
  isolation: "worktree",
  prompt: `You are the Developer subagent for WP-3. Read \`plugin/skills/team-protocols/role-cards/developer-card.md\` first (slim card; do NOT read lead-protocol.md or path-selection-rules.md).

G7 spawn payload:
{
  "trace_id": "wf-20260513-develop-wp03-spawn-001",
  "subagent_role": "java-engineer",
  "goal": "Implement WP-3 (preserve visibility_score on optimistic-lock retry) per design.md §3a verbatim.",
  "constraints": [
    "envelope_dir: /absolute/path/.ai-skills-memory/sessions/<sid>/team-envelopes",
    "<VERBATIM source-section block from design.md §3a>"
  ],
  "state_slice": {
    "active_files": ["src/main/java/com/f4ai/report/service/ReportService.java"],
    "related_artefacts": ["docs/features/visibility-score/design.md"]
  },
  "allowed_tools": ["Read", "Grep", "Glob", "Bash", "Write", "Edit"],
  "budget": {
    "max_input_tokens": 50000, "max_output_tokens": 2000,
    "max_tool_calls": 30, "max_turns": 10,
    "timeout_ms": 600000, "retry_budget": 1
  }
}

When done, return a G7 envelope per \`plugin/schemas/return-contract.schema.json\` AND atomic-write the same JSON to \${envelope_dir}/G7-developer-WP-3.json.`
})
```

All six required spawn-payload fields: `trace_id`, `subagent_role`, `goal`,
`constraints`, `allowed_tools`, `budget`. See
`@team-protocols/spawn-pattern.md` for the full schema and per-role
variations.

## Path B — Agent Teams (MANDATORY default — try this FIRST)

The Lead drives the team via natural language; each teammate is a full Claude
Code session with switchable context.

### Step 1 — create the team (natural-language prompt to self)

```text
Create an agent team named "<feature-slug>-team" with these teammates, all using subagent definitions from the ai-skills plugin so they inherit the right tools and model:

- "developer" (ai-skills:<java-engineer | python-engineer | frontend-engineer | ...>) — implements work packages, follows team-protocols/developer-protocol.md, isolation: worktree
- "reviewer" (ai-skills:software-engineer) — read-only review (disallow Write/Edit), follows reviewer-protocol.md
- "qa" (ai-skills:qa-engineer) — higher-level tests + SRE smoke checks, follows the QA section of develop/SKILL.md

Do NOT require plan approval from the developer (the Lead already resolved the plan — execution starts immediately). Use the shared task list with three tasks per WP (DEV, REVIEW, QA) linked via `dependsOn` so REVIEW unblocks when DEV completes and QA unblocks when REVIEW completes with verdict 'approved'.

Use teammate-mode `in-process` by default. Pick `tmux` split-pane mode ONLY if the user has explicitly indicated tmux/iTerm2 is available.

Standard clauses to include in every teammate's spawn prompt (v0.3.11):
- "File-channel backstop: after self-verification and before returning your G7 envelope via the bus, also write it to .ai-skills-memory/sessions/<sid>/team-envelopes/G7-<role>-<wp>.json via Bash + atomic mv. The Lead's Monitor reads this directory; if SendMessage/TaskUpdate augmentation is intermittent on your tool surface (alpha.31 / alpha.35 / alpha.36) this is the liveness backstop. See developer-protocol.md / reviewer-protocol.md 'File-channel envelopes' for the exact pattern."
- "Verdict-in-response fallback (Reviewer / QA): if your TaskUpdate or SendMessage tools fail at the gate, deliver your verdict in your next conversation turn — the Lead is monitoring your transcript via Shift+↓ and will write the G7 envelope on your behalf."
```

After issuing team-create, the Lead immediately starts a `Monitor` on the
team-envelopes directory:

```text
Monitor({
  scope: ".ai-skills-memory/sessions/<sid>/team-envelopes/",
  pattern: "*.json",
  on_event: "lead-handle-team-envelope"
})
```

This `Monitor` is the canonical liveness signal — the
`team-gate-reconciliation.py` hook fires on every `TaskCompleted` and
`TeammateIdle` and the Lead processes envelopes in order. The hook attaches
automatically on plugin install; no Lead-side wiring needed.

### Step 2 — populate the shared task list

For each WP from the resolved plan, create three tasks with the dependency
graph:

```text
Task: "WP-N DEV — <description>"  → assigned to developer teammate, no dependencies (or depends on prior WP's QA)
Task: "WP-N REVIEW"                → assigned to reviewer teammate, depends on "WP-N DEV"
Task: "WP-N QA"                    → assigned to qa teammate, depends on "WP-N REVIEW"
```

### Step 3 — drive and monitor

Teammates self-claim their next unblocked task — the Lead does NOT manually
assign; the dependency graph + claiming protocol handles it. The user uses
**Shift+↓** to cycle to any teammate, **Enter** to read transcripts or send
direct messages, **Ctrl+T** for the shared task list. If reviewer returns
`verdict: changes_requested` (or QA returns `qa_verdict: fail`), insert a
follow-up DEV task ("WP-N DEV r2 — fix issues") and re-point REVIEW + QA
dependencies to it. Loop until both gates pass. Surface progress to the user
after each WP clears the pipeline.

### Step 4 — handoff to Final Verification

After all WPs clear the pipeline, hand off to "Final Verification" in
`SKILL.md` (run in the main thread, not a teammate task), then ask for
cleanup: "Clean up the team."

## Path A — Subagents fallback (only if Path B Step 1 returned a technical error)

For each work package, the Lead executes the three-step `Agent({...})` spawn
loop defined in `@team-protocols/spawn-pattern.md`:

1. **DEVELOP** — `subagent_type: "ai-skills:<engineer-role>"` (java-engineer,
   python-engineer, frontend-engineer, etc., picked via
   `role-selection-table.md`), `isolation: "worktree"`. Prompt instructs the
   Developer to read `developer-protocol.md` first, carries the full G7 spawn
   payload, and demands a G7 return contract. Wait for return; validate;
   extract `files_changed` and `summary`.
2. **REVIEW** — `subagent_type: "ai-skills:software-engineer"`,
   `disallowedTools: ["Write", "Edit"]`. Prompt instructs the Reviewer to read
   `reviewer-protocol.md` + `code-review/SKILL.md`, lists files from the
   Developer return, asks for a G7 contract with `result.verdict ∈ {approved,
   changes_requested}`. If `changes_requested`, loop back to Step 1 with the
   issues attached.
3. **QA** — `subagent_type: "ai-skills:qa-engineer"`. Prompt scopes
   higher-level tests (smoke / API / integration / E2E — NOT unit tests; those
   belong to the Developer), lists files changed and acceptance criteria,
   demands SRE smoke checks (health endpoint, error rate, basic SLI sanity),
   and asks for a G7 contract with `result.qa_verdict ∈ {pass, fail}`. If
   `fail`, loop back to Step 1 with QA's issues attached.

**Only after all three stages return successfully does the work package count
as DONE.** The Lead moves to the next WP.

## Per-task Agent — hard-locked QA (first-class mode)

A documented first-class execution mode, NOT an ad-hoc fallback: when the bus
is dead, on >4-wave runs, or when team-per-wave cost is unjustified, spawn QA
per task via `Agent({subagent_type:"ai-skills:qa-engineer",
disallowedTools:["Write","Edit"]})`. Reusable hard-lock brief (fully
read-only, single GO'd WP only, `result.files_changed`=`[]`, no
aggregate/multi-WP envelopes): `@team-protocols/role-cards/qa-card.md`
"Hard-locked QA mode (P0-2)". >4-wave → per-task-Agent cost rationale:
`@team-protocols/path-selection-rules.md` "File-channel-exclusive shutdown &
multi-wave cost (P2-11)".
