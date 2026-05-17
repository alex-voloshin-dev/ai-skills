# Path Selection Rules (team-protocols)

Detailed Path A (Subagents) and Path B (Agent Teams) bodies, plus the hard anti-rationalization rules so the Lead does not silently downgrade Path B → Path A for invalid reasons. Loaded from `SKILL.md` when authoring or auditing a workflow that supports both paths.

**Bottom line up front: Path B is the MANDATORY default. Path A is selected ONLY when Path B Step 1 returns a hard technical block. There is no silent fallback for non-technical reasons.** All "Path B is preferred" / "Path A is canonical" wording elsewhere in this document is shorthand for the same rule — read it as MUST.

## Path A — Subagents (technical-block fallback only, sequential)

Fallback path used only on hard technical block of Path B. Per role:

```text
Agent({
  description: "<short label>",
  subagent_type: "ai-skills:<role>",
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
Create an agent team named "<feature-slug>-team" with the following teammates, all using subagent definitions from the ai-skills plugin so they inherit the right tools and model:

- "developer" (ai-skills:<java-engineer | python-engineer | frontend-engineer | ...>) — implements work packages, follows the developer protocol from plugin/skills/team-protocols/developer-protocol.md
- "reviewer" (ai-skills:software-engineer) — independent code review, read-only (no Write/Edit), follows reviewer-protocol.md
- "qa" (ai-skills:qa-engineer) — higher-level tests + SRE smoke, follows the QA section of the develop skill

Require plan approval for the developer teammate before they make any changes. Use the shared task list to coordinate work packages — one task per WP, with `dependsOn` linking review/QA tasks to their developer task.
```

Per Anthropic docs, this prompt makes Claude:
- Create a team with the named teammates
- Spawn each teammate using the listed `ai-skills:<role>` subagent definitions (the definition's tools + model + body apply, augmented with team coordination tools)
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

- **alpha.31 — `in-process` teammate-idle flake (any role, including Developer)**: in `teammate-mode in-process`, any teammate (Reviewer, QA, **and Developer**) can silently stop after claiming a task — no transcript activity, no file reads, no return. For the Developer this manifests in two sub-shapes: (i) classic idle (no edits on disk) and (ii) "silent-but-complete" — real edits land on disk, acceptance criteria appear met, but the G7 return envelope never arrives, blocking the schema-validated handoff to the Reviewer. **Secondary symptom (v0.3.9)**: a downstream task may continue to display `blockedBy: [<upstream-id>]` even after the upstream task transitions to `completed`. This is a state-display flake, not real blocking — but a teammate that reads the panel as authoritative may decline to self-claim. Treat persistent `blockedBy` on a `completed` upstream as a strong alpha.31 indicator and apply the stale-`blockedBy` recovery in `lead-protocol.md` "Path B Liveness". This is a known flake of the alpha Agent Teams API and is **NOT** a valid reason to downgrade the whole session to Path A. Mitigation lives in `lead-protocol.md` "Path B Liveness — Explicit Hand-off + Watchdog": the Lead pushes an explicit hand-off message at every stage transition (including Developer hand-off, contrary to the v0.3.5 wording that exempted it), runs a ~90s watchdog with up to 2 retry nudges, performs a read-only disk-state reconciliation when the silent role is the Developer, and escalates to the user after 3 nudges with a role-specific menu. A per-task Agent fallback (this WP only, remainder stays in Path B) is permitted **only** when the user explicitly picks that option from the escalation prompt — never as a silent automatic downgrade. The Lead MUST NEVER synthesize a G7 envelope on the Developer's behalf, even when disk state proves the work is done — re-spawn or per-task fallback is the only legitimate recovery.

- **alpha.33 — team-wide silent idle (v0.3.9, observed in field feedback)**: in `teammate-mode in-process`, two or more teammates can be simultaneously silent past the first 90-s watchdog window — typically Developer ran but Reviewer + QA never engaged at all (no transcript, no file reads, no task transitions). This is distinct from alpha.31 (one role) and from the "Agent Teams not enabled" hard block (team-create succeeded; the team is alive but the roles never auto-claim). Most common root cause: `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` is unset OR the runtime equivalent of team-runtime auto-claim is disabled, but `TeamCreate` itself returned success. Mitigation: when ≥ 2 teammates fail the first 90-s watchdog window, the Lead skips the second nudge cycle and surfaces a whole-team escalation prompt — options (1) wait, (2) `TeamDelete` + re-`TeamCreate`, (3) per-task Path A fallback for every silent role this WP (remainder stays in Path B), (4) abort WP. Serial 3 × 4.5 min watchdog cycles waste 13+ min before a decision point — alpha.33 short-circuits that. Fast-fail escape valve below (v0.3.9) catches the most common variant earlier.

- **alpha.33-fast-fail (v0.3.9) — zero-activity escape valve**: if EVERY teammate produces no activity (no transcripts, no file reads, no task transitions on any task) within the first 90 seconds after `TeamCreate` + initial `TaskCreate` round, this is a hard technical block in spirit — the team failed to engage at all. The Lead MUST surface the alpha.33 whole-team escalation prompt immediately, with option (3) "Path A per-task fallback for the entire current wave" expanded to "Path A for the remainder of the workflow" as an additional choice. This is NOT a rationalised downgrade per alpha.26/27 — total team silence is a documented Path B failure, not a path-selection preference. Document the chosen path in `REVIEW-LOG.md` "Liveness events" with the timestamps so future runs can detect a runtime-config drift.

- **alpha.34 — `shutdown_request` non-response + `TeamDelete`-on-active recovery (v0.3.10, observed in field feedback)**: in `teammate-mode in-process`, a teammate that is already silent-idle (alpha.31 / alpha.33) cannot acknowledge a `shutdown_request` either, because the team-runtime augmentation that adds `SendMessage` / `TaskUpdate` / `shutdown_response` is the same surface that has stalled. Symptom: the Lead issues `shutdown_request` after the WP completes, gets no acknowledgement from the silent role(s), and the documented "clean shutdown then `TeamDelete`" sequence stalls. Recovery: `TeamDelete` while teammates are still active is the documented recovery, NOT a leak — the runtime tears down the panel and frees the slots. The "TeamDelete fails on active teammates" warning in pre-v0.3.10 docs is wrong for the silent-idle path; it only applies when teammates are responsive and actively writing. After `TeamDelete`, the panel may continue to emit a tail of `idle_notification` JSON messages for several seconds from the torn-down teammates — these are runtime artefacts on a closed bus and the Lead MUST ignore them (do not parse, do not react). Record one line in `REVIEW-LOG.md` "Liveness events": `alpha.34: silent-idle <N>/<M> teammates; TeamDelete-on-active used to recover; <K> tail idle_notifications ignored`. Stranded `~/.claude/teams/<team-name>/` directories from `TeamDelete`-on-active are an alpha runtime artefact — the cleanup cron sweeps them; do not block the workflow on this.

- **alpha.35 — Reviewer team-bus tool gap (silent findings, v0.3.10, observed in field feedback)**: in `teammate-mode in-process`, a Path B Reviewer spawned as `ai-skills:software-engineer` can complete its read-only review work but be unable to deliver its verdict to the team bus because the runtime augmentation for `TaskUpdate` / `SendMessage` did not attach to the Reviewer's tool surface. Symptom: Reviewer transcript (visible via **Shift+↓**) shows complete findings and an explicit `verdict: changes_requested` (or `approved`), often ending with prose like "please relay these envelopes to the lead" or "grant access to TaskUpdate / SendMessage so I can complete the protocol end-to-end" — but the Reviewer's task stays `in_progress` and no G7 envelope arrives at the Lead. Distinct from alpha.31 (silent because never engaged): here the Reviewer engaged, produced output, and even named the delivery gap, but cannot push the envelope itself. Distinct from alpha.32 (tool-capability mismatch at the agent-definition level): the Reviewer's read-only `Write`/`Edit` constraint is correct and intended; what is missing is the team-runtime augmentation that gives any teammate the bus surface. Disk reconciliation does NOT apply (Reviewer is read-only; clean disk is the expected steady state, not a flake signal).

  Detection: a stale `in_progress` Reviewer task whose transcript (Shift+↓) shows substantive review content and an explicit verdict. Strong signal: Reviewer transcript ends with prose asking the Lead to "relay envelopes", "update tasks on my behalf", or "grant access to TaskUpdate / SendMessage". This is the Reviewer correctly recognising the gap and asking for the verdict-in-response fallback.

  Recovery: the Lead pushes one targeted `SendMessage(<reviewer-id>, "deliver findings now — return verdict (approved | changes_requested) and per-file finding list in your next response; do not attempt TaskUpdate")`. The Reviewer's reply via the conversation bus is the canonical delivery channel when the task-update channel is broken. The Lead reads that reply, writes the G7-equivalent envelope into `REVIEW-LOG.md` itself (same pattern as `eval-judge` verdict-in-response), and closes the Reviewer task with the verdict in the task summary. If `verdict: changes_requested`, the Lead then applies the standard fix-round handling (insert developer follow-up task, re-point review/QA `dependsOn` graph per Step 3 above). Record one line in `REVIEW-LOG.md` "Liveness events": `alpha.35: reviewer <name> findings delivered via SendMessage conversation reply; verdict <approved|changes_requested>; task <id> closed by Lead`.

  Prevention: at team-create time, the Lead SHOULD include in the Reviewer teammate's prompt the clause: `"If your TaskUpdate or SendMessage tools are unavailable when you complete review, deliver your verdict + per-file findings in your next conversation turn — the Lead will pick them up from the transcript and write the G7 envelope on your behalf."` This makes the verdict-in-response fallback explicit instead of relying on the Reviewer to self-discover it.

  Hard rule: the Lead MUST NOT grant `TaskUpdate` / `TaskList` to the Reviewer as an "obvious fix" for alpha.35. Read-only role isolation includes the task-list write surface — a Reviewer that can self-close its own task can also self-approve, defeating the gate. The verdict-in-response fallback is the correct recovery; expanding the Reviewer's write surface is a protocol violation, not a workaround.

- **alpha.36 — team-coordination augmentation gap (v0.3.11, observed in v22 field feedback)**: Anthropic Agent Teams docs state that `SendMessage` + task-management tools (`TaskUpdate`, `TaskList`, `TaskGet`) are *always available to a teammate even when `tools` restricts other tools*. In field practice (in-process display mode, alpha runtime), this augmentation does not always attach to every teammate's tool surface. Symptoms vary by role: Developer cannot mark `TaskUpdate(completed)`, Reviewer cannot deliver verdict (alpha.35 sub-case), QA never engages at all. Distinct from alpha.31 (silent because never engaged) and alpha.35 (Reviewer-only verdict gap): alpha.36 is the broader **lead-bound bus drop** class — teammates' `SendMessage` returns to the lead are not surfaced into the Lead's context even when the teammate clearly produced output (visible via Shift+↓ transcript).
  
  Detection: two consecutive `TaskCompleted` events for which the corresponding G7 envelope did not arrive in the Lead's context within 60 s. Strong signal: the `team-gate-reconciliation.py` hook's file-channel envelope is present and shows correct `disk_state.changed_files` while the bus envelope is missing. Disk evidence ✓, bus evidence ✗.
  
  Recovery: switch to file-channel-exclusive transport per `lead-protocol.md` "File-channel transport — first-class, not fallback". Lead pushes `SendMessage(<teammate>, "deliver findings now — write G7 envelope to .ai-skills-memory/sessions/<sid>/team-envelopes/G7-<role>-<wp>.json then return verdict in your next response")`. Teammate writes the G7 envelope via `Bash` + `mv` to the file-channel and ALSO posts the verdict in its next conversation turn. Lead reads both, validates the file-channel G7 against `return-contract.schema.json`, proceeds.
  
  Prevention: at team-create time, every Developer / Reviewer / QA teammate's spawn prompt includes the standard file-channel envelope clause from `developer-protocol.md` / `reviewer-protocol.md` "File-channel envelopes". This makes the file-channel backstop part of the contract, not a recovery procedure invented mid-session.
  
  Hard rule: do NOT downgrade to Path A on alpha.36. The team is alive and producing work; only the `teammate → lead` bus direction is broken. File-channel transport keeps the pipeline in Path B with negligible overhead. Record one line in `REVIEW-LOG.md` "Liveness events": `alpha.36: lead-bound bus dropped <N> consecutive G7 envelopes; switched to file-channel exclusively; <M> envelopes recovered from disk`.

- **alpha.32 — tool-capability mismatch (read-only teammate, write workflow)**: a teammate spawned with a subagent definition whose `tools:` list lacks `Write` / `Edit` cannot produce a file output on its own. In Path B, the teammate's `dependsOn` task auto-claim succeeds, but the workflow body it was given (e.g. "write PRD.md") is physically un-executable — the teammate silently idles or returns prose to the Lead that the Lead must then write itself. **As of plugin v0.3.8, this class is largely closed**: ten producer agents (`product-manager`, `marketing-strategist`, `ui-ux-designer`, `system-architect`, `solution-architect`, `cloud-architect`, `devops-architect`, `security-engineer`, `content-writer`, `content-designer`) now ship with `Write` / `Edit` and an explicit "Write scope (docs/design artifacts only)" hard rule that forbids touching application/infrastructure code. The remaining intentionally read-only roles are `eval-judge` (verdict-in-response — Lead writes `REVIEW-LOG.md` from the judge's structured return), `memory-curator` (already has its own minimal `Write`), and any reviewer roles spawned with explicit `disallowedTools: ["Write","Edit"]` at spawn time (e.g. `software-engineer` as Path B Reviewer per `developer-protocol.md`). For those: the Lead writes the file from the teammate's fenced-block return. Continuing into a Path B team with predictable tool-capability mismatch on the writable producers is now a stale-cache / outdated-prompt issue, not an alpha flake — re-read the role-capability cache below before declaring alpha.32.

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

Valid Path A triggers (hard technical blocks detected at or before Path B Step 1):

1. Team-create natural language returns "Agent Teams not enabled" / "experimental flag not set" / equivalent — typically because `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` env var is unset.
2. The Lead is itself running inside a subagent that has no team primitives.
3. **Pre-spawn tool-capability check (alpha.32) fails for the whole team** — every candidate `subagent_type` for a writing role lacks `Write` / `Edit` AND the workflow cannot be restructured to write in the Lead's main thread. In this case the team cannot fulfil its workflow contract, so Path B is not actionable for this run. Partial mismatches (only some roles read-only) are handled per role per the alpha.32 entry above, not by a whole-session downgrade.
4. **alpha.33-fast-fail — total-team zero-activity within 90 s of team-create + first TaskCreate**. `TeamCreate` succeeded but no teammate emitted any activity. This is observable, not theoretical — see the alpha.33 entry above. Per-role nudge cycles cannot recover total-team silence, so a user-approved whole-workflow Path A fallback is legitimate here. Document the trigger in `REVIEW-LOG.md` "Liveness events" with timestamps.
5. **Dead team bus — coordination augmentation absent for the whole team (P0-1, alpha.31/34/36).** The post-create coordination-tool probe (Pre-spawn Procedure step 7) shows NO teammate has working `TaskUpdate` + `SendMessage`. Per field observation this is frequently the alpha default, not a rare flake. This is a SANCTIONED Path A trigger applied **once per run for the entire workflow** — distinct from the per-wave alpha.31 / alpha.33 liveness events (those are recoverable single-wave flakes handled by the watchdog; this is a whole-run bus failure decided exactly once). Decide it at the first probe and stay on Path A for the rest of the run; do NOT rediscover it wave-by-wave or re-enter Path B on a later wave. Document in `REVIEW-LOG.md` "Liveness events" with the probe timestamp.

In cases (1) and (2), fall back silently and continue. Case (5) is decided once at the post-create probe and applies to the entire run (documented, no per-wave re-entry into Path B). Cases (3) and (4) surface user-facing escalation prompts before falling back. All other downgrade rationales remain invalid.

Display-mode unavailability is NEVER a valid Path A trigger. Always default to `teammate-mode in-process` if tmux/iTerm2 is uncertain.

## File-channel-exclusive shutdown & multi-wave cost (P2-11)

When the team runs file-channel-exclusively (alpha.36 recovery active), teammate shutdown semantics differ from the responsive path — this extends the alpha.34 shutdown entry above, it does not replace it:

- A file-channel-exclusive teammate acknowledges `shutdown_request` via an `idle_notification` on the panel, NOT a `shutdown_response`. Absence of `shutdown_response` here is expected — do NOT treat it as a hang or escalate.
- `TeamDelete` will refuse roughly 3× in a row while a read-only Reviewer drains its final file-channel write. This is expected back-pressure, not a leak: retry with backoff (e.g. 2 s / 4 s / 8 s) and do NOT block the workflow on it — proceed once it succeeds.
- The stranded `~/.claude/teams/<team-name>/` directory and the consumed terminal pane are REAL costs that accumulate per team lifecycle on a multi-wave run (the cleanup cron eventually sweeps the dir; the pane is gone for the session).

**Lead-facing note (P2-11):** on a run with **> 4 waves**, prefer **per-task `Agent({...})`** (no team lifecycle, no pane leak, no stranded dir) over **team-per-wave**. Repeated team-create / `TeamDelete` cycles multiply the stranded-dir and consumed-pane costs above; on long multi-wave runs the per-task Agent shape is the lower-cost option versus spinning a fresh team each wave.

## Pre-spawn tool-capability check (alpha.32 mitigation)

Before issuing the Path B team-create prompt, the Lead MUST verify each teammate's `subagent_type` has tools sufficient for the work it will be assigned. As of plugin v0.3.8 most producers ship with `Write` / `Edit` — the check is fast and almost always passes, but is still mandatory to catch (a) stale subagent-type references, (b) the intentional read-only roles (`eval-judge`, Reviewer-lock), (c) edge-case roles with niche tool sets.

Procedure:

1. For each teammate planned in the team-create prompt, identify the produced artefact (PRD.md, ARCHITECTURE.md, REVIEW-LOG.md, …) and the action verb (write / edit / review / score).
2. Read the `tools:` frontmatter of `plugin/agents/<subagent-name>.md` for each role. (Cached map above — refresh from disk if the agent file has changed since the cache annotation date.)
3. Compare required action against tool capability:

   | Action | Required tool | Typical outcome | If missing |
   |---|---|---|---|
   | Write a new file | `Write` | All 10 producer agents have it as of v0.3.8 | (a) pick a different role with `Write`, OR (b) restructure: teammate returns prose to Lead, Lead writes file in main thread, OR (c) per-role Path A fallback |
   | Edit an existing file | `Edit` | Same set has Edit | as above |
   | Run tests, lint, build | `Bash` | Developer roles + architect roles + security have it | pick a role with `Bash` or fall back |
   | Read-only review / score | `Read` | Always present | no action needed |

4. Two roles require explicit prompt clauses even though the cache shows their state correctly:
   - **`eval-judge`** (NO Write by design): team-create prompt MUST say `"judge returns the scored verdict in a fenced JSON block; Lead writes REVIEW-LOG.md from the structured return."` This is the verdict-in-response pattern, not an alpha flake.
   - **`software-engineer` as Path B Reviewer**: team-create prompt MUST add `disallowedTools: ["Write","Edit"]` at spawn time so the Reviewer cannot self-apply fixes.

5. If mitigation is (c) per-role Path A fallback, the team-create prompt omits that teammate and the Lead spawns it via `Agent({...})` for its wave only — the rest of the team stays in Path B.

6. If every writing role would need mitigation (c), the whole team is non-viable in Path B — declare a hard technical block per the third valid Path A trigger above and fall back to Path A for the whole run. With v0.3.8 producer capabilities this should be essentially unreachable for the standard `/feature-design`, `/develop`, `/team-bugfix`, `/refactor`, `/migrate` workflows.

7. **Coordination-tool capability probe (P0-1, alpha.31/34/36).** Immediately after `TeamCreate` + the first `TaskCreate` round — before driving any work — the Lead probes that at least one teammate actually has the `TaskUpdate` + `SendMessage` augmentation (push one trivial `SendMessage` and confirm a teammate `TaskUpdate` / ack round-trips, or inspect the first teammate's tool surface). Teammates frequently lack this coordination augmentation despite a successful `TeamCreate` — this is the observed default in the current alpha runtime (alpha.31/34/36), not a rare flake. If NO teammate can `TaskUpdate` + `SendMessage`, the team bus is dead: this is a sanctioned hard technical block — switch to Path A **once, for the whole run** (see Valid Path A trigger 5), not a per-wave liveness event to be rediscovered each wave. Decide it once at this probe; do NOT re-enter Path B on later waves of the same run.

### Role-capability cache (plugin agents, alpha.32 reference)

This table mirrors `plugin/agents/<name>.md` frontmatter as of plugin v0.3.8. Re-read from disk if older than the current plugin version.

| Agent | Tools | Write-capable | Notes |
|---|---|---|---|
| `product-manager` | Read, Grep, Glob, Write, Edit | YES | Writes PRD.md, FEATURES.md, user stories directly (docs scope only per Hard Rule 4) |
| `marketing-strategist` | Read, Grep, Glob, Write, Edit | YES | Writes MARKET-ANALYSIS.md, positioning briefs directly (marketing scope only) |
| `ui-ux-designer` | Read, Grep, Glob, Write, Edit | YES | Writes UX-FLOW.md, wireframes, design-token specs directly (design scope only) |
| `system-architect` | Read, Grep, Glob, Bash, Write, Edit | YES | Writes ARCHITECTURE.md, C4 diagrams directly (architecture scope only) |
| `solution-architect` | Read, Grep, Glob, Bash, Write, Edit | YES | Writes ADRs, OpenAPI specs, threat models directly (design scope only) |
| `cloud-architect` | Read, Grep, Glob, Bash, Write, Edit | YES | Writes cloud-architecture docs, landing-zone blueprints (docs scope only — NOT deployable Terraform/Helm) |
| `devops-architect` | Read, Grep, Glob, Bash, Write, Edit | YES | Writes CI/CD architecture docs, runbooks (docs scope only — NOT shipped `.github/workflows/`) |
| `security-engineer` | Read, Grep, Glob, Bash, Write, Edit | YES | Writes SECURITY-REPORT.md, RISKS.md, threat models directly (security-docs scope only — NOT fixes to app code) |
| `content-writer` | Read, Grep, Glob, Write, Edit | YES | Writes user-facing markdown docs, API reference, release notes |
| `content-designer` | Read, Grep, Glob, Write, Edit | YES | Writes page-content drafts, hero/CTA copy, conversion briefs |
| `db-engineer` | Read, Grep, Glob, Bash, Write, Edit | YES | Writes DATA-MODEL.md and migration code directly |
| `qa-engineer` | Read, Grep, Glob, Bash, Write, Edit | YES | Writes acceptance criteria and test code directly |
| Every `*-engineer` developer (java, python, frontend, mobile, ml, data, devops, sre) | Read, Grep, Glob, Bash, Write, Edit | YES | Writes code directly |
| `seo-engineer`, `software-engineer` | Read, Grep, Glob, Bash, Write, Edit | YES | Writes code and docs directly |
| `eval-judge` | Read, Grep, Glob | NO | INTENTIONALLY read-only — returns scored verdict in response; Lead writes `REVIEW-LOG.md` from the structured return |
| `software-engineer` spawned as Path B Reviewer | (above) + `"do not Write/Edit"` directive in the team-create prose | prose-only at spawn | The team-create natural-language prompt CANNOT pass structured `disallowedTools` — the read-only directive is policy-only. Runtime enforcement is unavailable in current Agent Teams team-create. The Lead MUST verify the Reviewer's G7 return: `result.files_changed` MUST be `[]`; non-empty is a role-isolation violation per `lead-protocol.md` "Gate Verification — Reviewer file-change check" |
| `prompt-engineer` | Read, Grep, Glob, Bash | NO | Advisory role — does not produce files in current workflows |
| `memory-curator` | Read, Write | YES | Tightly scoped to L4/L5 learnings files only |
| `claude-code-guide` | Read, Bash, WebFetch, WebSearch | NO | Read-only knowledge agent |

Two patterns remain alpha.32-relevant:

1. **`eval-judge` and similar verdict-in-response roles**: the team-create prompt MUST include: `"<role> returns the scored verdict in a fenced JSON block in its final message — the Lead writes the log file in the main thread."` This is normal for evaluator roles; not a defect.

2. **Reviewer locks via spawn-time `disallowedTools`**: when spawning `software-engineer` as a Path B Reviewer, the team-create prompt MUST pass `disallowedTools: ["Write","Edit"]` so the Reviewer cannot self-apply fixes. The role-capability cache above shows the spawn-time effective tools, not the agent-definition tools.

For all other producers, write-capability is intrinsic and no fenced-block restructure is needed — the teammate writes its assigned artefact directly. Removing the legacy "Bash heredoc forbidance" clauses from team-create prompts is now safe for these producers.
