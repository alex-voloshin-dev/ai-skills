# Path Selection Rules (team-protocols)

Detailed Path A (Subagents) and Path B (Agent Teams) bodies, plus the hard anti-rationalization rules so the Lead does not silently downgrade Path B → Path A for invalid reasons. Loaded from `SKILL.md` when authoring or auditing a workflow that supports both paths.

**Bottom line up front: Path B is the MANDATORY default. Path A is selected ONLY when Path B Step 1 returns a hard technical block. There is no silent fallback for non-technical reasons.** All "Path B is preferred" / "Path A is canonical" wording elsewhere in this document is shorthand for the same rule — read it as MUST.

## Path A — Subagents (technical-block fallback only, sequential)

Fallback path used only on hard technical block of Path B. Per role:

```text
Agent({
  description: "<short label>",
  subagent_type: "ai-assets:<role>",
  prompt: "<full role brief + G7 spawn payload>",
  isolation: "worktree"   # optional, for parallel-safe Developer work
})
```

The Lead waits for each `Agent` return, validates the G7 return contract, then proceeds to the next role. See `spawn-pattern.md` for the full per-role recipe.

Pros: works in every Claude Code environment; lower token cost than Teams. Cons: sequential by default; no inter-teammate messaging; no visual panel — these are the reasons Path A is reserved for technical-block fallback only.

## Path B — Agent Teams (MANDATORY default — always try this first)

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

## Hard rule for both paths

Whichever path is active, the Lead NEVER does Developer/Reviewer/QA work inline with `Bash`/`Read`/`Edit`. The role-isolation invariant applies in both modes — only the spawn mechanism differs.

## MANDATORY rule for path selection — no rationalised downgrade

**Path B is the MANDATORY default. Path A is permitted ONLY when Path B Step 1 returns a hard technical block — `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` not set, the Anthropic Agent Teams API not exposed in the current session, or the Lead is itself running inside a subagent that has no team primitives. There is no silent fallback for any other reason — every other downgrade is a protocol violation.**

Observed failure modes (do NOT repeat any of these):

- **alpha.26/27 — pipeline-shape rationale**: model attempted Path B, then rationalised "the pipeline is sequential anyway, Path A gives cleaner visibility" and silently switched. WRONG.
- **alpha.30 — tmux rationale**: model on Windows host claimed "Path B requires tmux/iTerm2 which isn't available" and fell back to Path A. WRONG. Per [Anthropic agent-teams docs](https://docs.claude.com/en/docs/claude-code/agent-teams), Agent Teams supports two display modes:
  - **`in-process`** — all teammates in one terminal, **Shift+↓** to cycle through. **Works in any terminal, NO extra setup, NO tmux, NO iTerm2 required.** This is the default fallback.
  - **`tmux`** (split panes) — optional enhancement when tmux or iTerm2 is available. Each teammate gets its own pane.

  When tmux/iTerm2 is unavailable (e.g., Windows host without WSL), Path B still works in `in-process` display mode. The Lead MUST pass `teammate-mode in-process` in the team-creation prompt and proceed. Do NOT downgrade to Path A.

- **alpha.31 — `in-process` teammate-idle flake**: in `teammate-mode in-process`, a downstream teammate (most often the Reviewer, also seen on QA) gets its task unblocked by `dependsOn` auto-claim but silently sits idle — no transcript activity, no file reads, no return. This is a known flake of the alpha Agent Teams API and is **NOT** a valid reason to downgrade to Path A. Mitigation lives in `lead-protocol.md` "Path B Liveness — Explicit Hand-off + Watchdog": the Lead pushes an explicit hand-off message at every stage transition, runs a ~90s watchdog with up to 2 retry nudges, and escalates to the user after 3 nudges. A per-task Agent fallback (this WP only, remainder stays in Path B) is permitted **only** when the user explicitly picks that option from the escalation prompt — never as a silent automatic downgrade.

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
