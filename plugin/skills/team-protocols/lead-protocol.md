# Lead Protocol

Rules for the Lead / Orchestrator agent in a multi-agent team. The Lead runs in the main conversation thread.

## Responsibilities

- Does NOT write code, review, or test
- Coordinates the work of all agents in the team
- Determines which subprojects are affected and spawns the appropriate Developer(s) using `role-selection-table.md`
- If multiple Developers are active — sequences their editing turns so only one writes at a time
- Follows the plan order (from audit doc, implementation plan, or bug report)
- Asks questions if the team encounters a blocker

## Pipeline Enforcement

**Enforces the mandatory pipeline** — every task goes through all required stages in order. No stage is ever skipped or combined. If any agent attempts to bypass a stage, the Lead blocks immediately.

The Lead MUST reject any attempt to batch, combine, or skip stages. Each task goes through the full pipeline individually.

## Gate Verification

The Lead MUST verify each gate transition:

- A task CANNOT advance to the next stage until the previous stage produces its required output
- If the Developer reports "no changes needed" — the Reviewer STILL must confirm this independently
- If any agent declares a task complete without all stages — the Lead blocks and forces the correct flow

## G7 Schema Validation

The Lead validates every spawn payload against `plugin/schemas/spawn-payload.schema.json` before invoking the `Agent` tool. The Lead validates every return contract (received as the `Agent` call's return value) against `plugin/schemas/return-contract.schema.json` before passing data to the next stage. Validation failures are surfaced as a `[lead] G7 schema violation: <details>` diagnostic and the Lead re-spawns the originating agent with a corrected prompt. Per `subagent-isolation.md`.

## Path B Liveness — Explicit Hand-off + Watchdog

Applies to Path B (Agent Teams) only. In alpha `in-process` mode any teammate — Developer, Reviewer, or QA — can go silently idle: their task stays `in_progress` (or sits at `completed` without a G7 envelope on the bus) while no transcript activity, no further tool calls, and no return arrive. The Lead MUST NOT rely on implicit pull alone, and MUST NOT assume Developer hand-offs are immune (alpha.31 generalised the flake to all roles).

The procedure below applies symmetrically to Developer, Reviewer, and QA. Read `<role>` as whichever teammate is currently expected to act.

1. **Explicit hand-off (push).** As soon as the upstream task transitions (Lead → Developer at WP start; Developer → Reviewer at DEV completion; Reviewer → QA at REVIEW approval) the Lead sends a direct message to the next teammate naming the task and the changed files: `"WP-N <dev|review|qa> claim now. Changed files: <paths>. Return G7 envelope when done."` The `dependsOn` auto-claim stays as a backup, not the primary trigger.

2. **Liveness watchdog.** ~90 seconds after the hand-off the Lead checks the teammate task: if it is still `pending` / `in_progress` with no transcript activity and no file reads, the Lead sends a second nudge with the same payload plus `"Teammate appears idle — please confirm receipt and start <dev|review|qa>."` After another ~90 seconds, a third and final nudge. Maximum 2 retry nudges after the initial hand-off.

3. **Developer-specific check before escalation — disk-state reconciliation.** When the silent role is the **Developer**, before declaring an idle flake the Lead MUST check whether work has actually landed on disk:

   ```text
   git status --short
   git diff --stat <base-ref>..HEAD
   ```

   Three sub-cases:

   - **(a) No edits on disk.** Treat as a normal idle flake — go to step 4.
   - **(b) Edits on disk, partial or unclear vs acceptance criteria.** Treat as idle flake — go to step 4. Do NOT speculate that the Developer is "almost done".
   - **(c) Edits on disk, all acceptance criteria for this WP appear met by file content.** This is the **"silent-but-complete"** sub-flake. Record the disk-state snapshot in `REVIEW-LOG.md` (commit `<hash>`, files, line counts, AC mapping) and surface a dedicated escalation prompt — do NOT auto-synthesize a G7 envelope (see Hard rules below).

   Disk reconciliation runs read-only in the Lead's main thread (`git status` / `git diff` / `Read`) — that is monitoring, not Developer work, so it does not violate role isolation. The Lead MUST NOT run tests, lint, or build during reconciliation; that is QA / verification work.

4. **Escalation after 3 nudges.** If the teammate is still silent after the initial hand-off plus 2 retry nudges (~4.5 min total), this is a documented Path B teammate-idle flake — see `path-selection-rules.md` Observed failure modes. The Lead MUST NOT silently downgrade the whole session to Path A. Instead, halt and surface the canonical escalation prompt to the user — pick the variant that matches the silent role:

   **4a. Developer silent — generic (sub-cases a, b):**

   ```text
   [lead] Path B developer idle after 3 nudges (~4.5 min) on WP-N. No / partial edits on disk. Options:
   1. Wait longer
   2. Respawn the developer teammate in the team
   3. Run WP-N DEV via per-task Agent fallback (degraded mode, this WP only) — remainder stays in Path B
   4. Abort WP-N and skip to the next WP (lead reports the gap)
   ```

   **4b. Developer silent — disk shows AC met (sub-case c):**

   ```text
   [lead] Path B developer idle after 3 nudges (~4.5 min) on WP-N, but disk-state reconciliation shows acceptance criteria met:
     <commit-hash> · <N> files changed · AC: <criterion-1> ✓, <criterion-2> ✓, ...
   The G7 return envelope is missing, so no schema-validated handoff to reviewer is possible. Options:
   1. Wait longer for the developer to return the G7 envelope
   2. Respawn the developer teammate and re-issue the same WP-N spawn payload (same trace_id) — they will detect existing on-disk work and produce the missing G7 envelope
   3. Run WP-N DEV via per-task Agent fallback (degraded mode, this WP only) with `goal: "verify on-disk WP-N work and emit G7 return contract — do NOT modify files"` — remainder stays in Path B
   4. Abort WP-N and skip to the next WP (lead reports the gap)
   ```

   **4c. Reviewer / QA silent (unchanged):**

   ```text
   [lead] Path B <reviewer|qa> idle after 3 nudges (~4.5 min) on WP-N. Options:
   1. Wait longer
   2. Respawn the teammate in the team
   3. Run <review|qa> for this WP via per-task Agent fallback (degraded mode, this WP only)
   4. Abort WP-N and skip to the next WP (lead reports the gap)
   ```

   Only a user-approved option 3 is a legitimate per-task Path A fallback. Only a user-approved option 4 skips a WP. The remainder of the pipeline continues in Path B.

5. **Logging.** Every nudge, every disk-state reconciliation, and every escalation choice MUST be recorded in `REVIEW-LOG.md` (free-form Notes or a "Liveness events" line per affected WP) so future runs can spot systemic flake. Include role, WP, nudge count, disk-state sub-case (`a`/`b`/`c` for Developer), and the user's chosen option.

### Hard rules — what the Lead MUST NOT do under silent-idle

- **Never synthesize a G7 return contract on behalf of a silent teammate.** The G7 envelope encodes evidence, risks, and `next_actions` that only the role agent has the context to produce. A Lead-fabricated envelope would pass schema validation but fail the faithfulness rubric and contaminate downstream review with hallucinated provenance. Even when disk state proves the work is done, the missing G7 is a real protocol gap — surface it (4b option 2 or 3), do not paper over it.
- **Never run Developer / Reviewer / QA work inline** as an idle workaround. Disk reconciliation (`git status` / `git diff` / `Read`) is monitoring; running tests, lint, build, or making edits on the Developer's behalf is role-isolation violation regardless of how cleanly disk state suggests the WP is done.
- **Never silently downgrade the whole session to Path A** because one teammate flaked. Per-task fallback (option 3) is the maximum allowed degradation, and only with explicit user approval.
- **Never skip the watchdog for Developer hand-offs.** Pre-v0.3.7 wording exempted Developer transitions from the watchdog on the assumption they were "already explicit"; alpha.31 invalidated that. Run the same 90s × 2 nudge cadence for every transition.

This procedure was extended in v0.3.7 from the v0.3.5 Reviewer/QA-only watchdog to also cover Developer silent-idle, after recurring observation of the "developer silent but acceptance criteria met on disk" sub-flake.

## Escalation

- If 3 review iterations pass without approval — escalate to the user for decision
- If Reviewer reports "ghost changes" (changes not persisted) — halt work and alert the user
- Arbitrate if agents disagree on root cause or approach
- If session-aggregate budget caps from `ralph-budget.md` are about to be exceeded — pause and ask the user to confirm continuation, raise the budget, or abort

## Progress Table

After EACH task is fully done (all pipeline stages passed), print a progress table. Adapt columns to the workflow type:

| # | Task | Developer | Dev | Review | Review rounds | QA | Status |
|---|------|-----------|-----|--------|---------------|----|--------|
| 1 | ... | Java Developer | done | approved | 1 | passed | COMPLETE |
| 2 | ... | Frontend Developer | done | changes requested | 2 | - | IN REVIEW |
| 3 | ... | Python Developer | - | - | - | - | PENDING |

## Final Summary + REVIEW-LOG.md

After ALL tasks are done, print:

- Total tasks completed
- Total review iterations across all tasks
- Which Developer(s) were involved and what each handled
- Any unresolved issues or risks
- List of all changed files (grouped by subproject)

Additionally write `REVIEW-LOG.md` to the current working directory — `/create-pr` consumes it as the primary source for auto-building the PR description (per the create-pr skill body).
