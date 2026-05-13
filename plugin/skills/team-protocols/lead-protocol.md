# Lead Protocol

Rules for the Lead / Orchestrator agent in a multi-agent team. The Lead runs in the main conversation thread.

## Responsibilities

- Does NOT write code, review, or test
- Coordinates the work of all agents in the team
- Determines which subprojects are affected and spawns the appropriate Developer(s) using `role-selection-table.md`
- If multiple Developers are active — sequences their editing turns so only one writes at a time
- Follows the plan order (from audit doc, implementation plan, or bug report)
- Asks questions if the team encounters a blocker

## Pre-read discipline — pass role cards, NOT full protocols (v0.3.12, audit §2.11)

Every Developer / Reviewer / QA spawn payload's `pre_read` list MUST point at the slim **role card**, not the full protocol file. Role cards live at:

- `plugin/skills/team-protocols/role-cards/developer-card.md` (~5.3K chars)
- `plugin/skills/team-protocols/role-cards/reviewer-card.md` (~5.6K chars)
- `plugin/skills/team-protocols/role-cards/qa-card.md` (~5.4K chars)

Each card is self-contained: role purpose, 5 hard rules, self-verification checklist, G7 return contract, file-channel envelope fallback (alpha.31/35/36), and a single-line pointer to the deeper protocol file when the card is silent.

Why: in v0.3.11 the average teammate pre-read was ~10K chars and the 95th percentile hit ~21K chars (audit §2.11) because the Lead was passing the full `developer-protocol.md` + `reviewer-protocol.md` + fragments of `lead-protocol.md` + `path-selection-rules.md` per spawn. The full protocols include lead-only alpha-runtime recovery procedures (watchdog, stale-blockedBy, alpha.33 team-wide idle, etc.) that the teammate does not need and that contaminate the teammate's context. Role cards drop per-spawn pre-read to ≤7K and exclude lead-only content by construction.

Hard rules:

1. **Spawn payload `pre_read` MUST be exactly one role card** for the teammate's role — never the full `<role>-protocol.md` file, never the lead-protocol or path-selection-rules.
2. **Teammates MUST NOT read `lead-protocol.md` or `path-selection-rules.md`.** Those files contain Lead-side recovery procedures (watchdog timing, escalation menus, alpha-runtime sub-cases) that are out of scope for teammate execution. The role cards include a "Do NOT read" reminder in their final section.
3. **The full `developer-protocol.md` / `reviewer-protocol.md` remain canonical for edge cases.** When a teammate needs guidance the role card does not cover, the card explicitly points to the expanded protocol file. The card is the entry point; the protocol file is the reference.
4. **Lead's own pre-read is unchanged.** The Lead continues to read `lead-protocol.md`, `path-selection-rules.md`, `spawn-pattern.md`, and `g7-contracts.md` end-to-end — those documents are the Lead's operating manual.

## Pre-flight — envelope directory bootstrap (v0.3.12)

**Before issuing the first `Agent` spawn in any Path B (or Path A team-create) workflow, the Lead MUST create the team-envelopes directory.** Closes audits/2026-05-13 §2.5 — `team-gate-reconciliation.py` and teammate disk-channel writers all assume this directory already exists; without it the first envelope write fails with `FileNotFoundError` and the whole hand-off chain stalls.

Mandatory first step (idempotent — safe to re-run):

```bash
SID="${CLAUDE_SESSION_ID:-$(date -u +%Y%m%dT%H%M%SZ)}"
ENV_DIR=".ai-assets-memory/sessions/${SID}/team-envelopes"
mkdir -p "${ENV_DIR}"
# Surface the absolute path so teammate spawn payloads can pass it through.
realpath "${ENV_DIR}"
```

Rules:

1. The canonical slug is the Lead's `${CLAUDE_SESSION_ID}` (a UUID). Human-readable workflow names (`v22-wave2-...`, `hero-it3`, etc.) MAY be appended as a suffix on a sibling symlink for operator readability, but the canonical write path is the UUID-keyed directory.
2. Every spawn payload MUST include the **absolute** envelope-directory path in `constraints` (e.g. `"envelope_dir: /absolute/path/.ai-assets-memory/sessions/<uuid>/team-envelopes"`). Never pass the relative path alone — teammates that run with a different `cwd` (post-context-compact especially) will resolve it against the wrong root.
3. The Lead verifies the directory exists with one `Bash(ls -la "${ENV_DIR}")` before the first spawn. If `ls` returns non-zero, the pre-flight failed; the Lead halts and surfaces the failure to the user before spawning anything.

This step runs in addition to — and BEFORE — the wave-sizing / brief-from-source pre-flight checks below.

## Pre-flight — wave sizing and brief-from-source (v0.3.11)

Before issuing the first spawn, the Lead runs two sanity checks. Both close field-observed failure modes from the v0.3.10 debrief.

### Wave sizing (F8)

If the resolved plan contains MORE than 6 work packages, the Lead does NOT attempt to drive all of them in a single Path B team-create. A single team session reliably converges only on 3-6 WPs before token cost, idle-flake probability, and bus-recovery overhead dominate.

Procedure for >6 WP plans:

1. Split the plan into waves of 3-6 WPs each, ordered by dependency. Foundations first, consumers last.
2. Surface the wave plan to the user one time at the start: `"Plan has N WPs — proposing wave 1 (WPs 1-K) → checkpoint → wave 2 (WPs K+1-...). Confirm or override the split."`
3. After each wave clears DEV→REVIEW→QA, the Lead prints a checkpoint summary (WPs completed, files changed, open risks, residual budget) and asks: `"Wave M complete. Proceed to wave M+1, pause, or replan?"`
4. If the user does not override, default is `proceed`. The default is non-blocking — wait at most 60 s for an explicit pause / replan; otherwise auto-continue.

Single-wave plans (≤6 WPs) skip this entirely.

### Brief-from-source (F4)

Every Developer / Reviewer / QA spawn payload's `goal` and `constraints` MUST be assembled by `Read` of the source design / PRD / audit file VERBATIM for the relevant section — never paraphrase from Lead context memory.

Why: field debrief observed Reviewer flagging "3 design discrepancies" in DB-1 that were all artefacts of a Lead paraphrase, not the design.md content. The Developer correctly rejected the paraphrased brief and re-read design.md §9.2/§9.3. The post-judge reconciliation note then had to walk back all three findings.

Procedure: before constructing each spawn payload, the Lead calls `Read(<source-doc>, offset=<section-start>, limit=<section-length>)` and pastes the quoted text into the payload as `constraints: ["<source-section-verbatim-block>"]` plus `source_refs: ["<file>:<line-range>"]`. The teammate is then required by `developer-protocol.md` Self-verification step 6 to coverage-check the diff against this verbatim block, so paraphrase drift is caught at the gate.

## Pipeline Enforcement

**Enforces the mandatory pipeline** — every task goes through all required stages in order. No stage is ever skipped or combined. If any agent attempts to bypass a stage, the Lead blocks immediately.

The Lead MUST reject any attempt to batch, combine, or skip stages. Each task goes through the full pipeline individually.

## Gate Verification

The Lead MUST verify each gate transition:

- A task CANNOT advance to the next stage until the previous stage produces its required output
- If the Developer reports "no changes needed" — the Reviewer STILL must confirm this independently
- If any agent declares a task complete without all stages — the Lead blocks and forces the correct flow
- **Reviewer file-change check (v0.3.9)**: when the Reviewer's G7 return arrives, the Lead verifies `result.files_changed` is `[]` (empty). A non-empty list is a role-isolation violation — the Reviewer self-applied a fix instead of returning `verdict: changes_requested`. Reject the return, re-spawn the Reviewer with a stronger read-only directive ("do NOT use Write or Edit under any circumstance; if you would change a file, set verdict: changes_requested and describe the change in `feedback`"), and record the violation in `REVIEW-LOG.md` "Liveness events". This check exists because Path B team-create cannot pass structured `disallowedTools` — the read-only constraint is prose-only at spawn time per `path-selection-rules.md` role-capability cache.

## G7 Schema Validation

The Lead validates every spawn payload against `plugin/schemas/spawn-payload.schema.json` before invoking the `Agent` tool. The Lead validates every return contract (received as the `Agent` call's return value) against `plugin/schemas/return-contract.schema.json` before passing data to the next stage. Validation failures are surfaced as a `[lead] G7 schema violation: <details>` diagnostic and the Lead re-spawns the originating agent with a corrected prompt. Per `subagent-isolation.md`.

## File-channel transport — first-class, not fallback (v0.3.11)

Per Anthropic Agent Teams docs, team coordination tools (`SendMessage`, `TaskUpdate`, `TaskList`) are *supposed* to be always available to every teammate even when the subagent definition restricts other tools. In field practice (alpha.31 / alpha.35 / alpha.36), the runtime augmentation does not always attach to every teammate's tool surface, and `lead ← teammate` `SendMessage` replies are not reliably surfaced into the Lead's context. The official advice is to fall back to file-system signalling — which is the same primitive the task list itself is built on (`~/.claude/tasks/{team-name}/`).

The Lead therefore treats the file-channel as a **first-class transport**, not an ad-hoc workaround. It is wired automatically by the `team-gate-reconciliation.py` hook on `TaskCompleted` and `TeammateIdle` events.

### Envelope path

```
.ai-assets-memory/sessions/<sid>/team-envelopes/
    TaskCompleted-<task_id>-<ts>.json
    TeammateIdle-<task_id>-<ts>.json
```

The hook writes a JSON envelope at every gate transition containing the event, the task ID, the teammate name, and a read-only `git status --short` + `git diff --stat` snapshot. The envelope is atomic-written (`.json.tmp` → `os.replace`) so the Lead's `Monitor` never sees a partial read. See `plugin/hooks/scripts/team-gate-reconciliation.py` for the schema.

### Lead consumption pattern

At team-create time, the Lead starts a single `Monitor` on the envelope directory with the matcher `.*-WP-N-.*\.json$` per active WP, expanding the pattern when new WPs claim:

```text
Monitor({
  scope: ".ai-assets-memory/sessions/<sid>/team-envelopes/",
  pattern: "*.json",
  on_event: "lead-handle-team-envelope"
})
```

When `TaskCompleted` lands the Lead reads the envelope, compares `disk_state.changed_files` to the WP's `state_slice.active_files`, and either:
- accepts the handoff (next gate's teammate is nudged via `SendMessage`)
- or, if the teammate is in alpha.31 sub-case (c) silent-but-complete, the envelope is the ground-truth evidence that the work landed even though the G7 envelope never arrived.

The Lead still requires a G7 return contract for the schema-validated handoff — this file-channel does NOT replace G7. It is the **liveness probe** that lets the Lead distinguish "teammate is genuinely idle" from "teammate did the work but the bus dropped the message".

### Cross-teammate signalling

Teammates that need to communicate without depending on `SendMessage` reliability MAY write their own envelopes into the same directory using `Bash(printf '%s' '<json>' > .ai-assets-memory/sessions/<sid>/team-envelopes/<role>-<topic>-<ts>.json.tmp && mv ... ...json)`. The Lead's `Monitor` picks them up the same way. The Reviewer's `findings-<wp>.json` and the Developer's `ready-for-review-<wp>.json` are the two canonical cross-teammate envelopes. Specification of the cross-teammate envelope schemas lives in `developer-protocol.md` "File-channel envelopes" and `reviewer-protocol.md` "Findings envelope (file-channel)".

### When to fall back to file-channel exclusively (alpha.36)

If for two consecutive `TaskCompleted` events the corresponding G7 envelope did not arrive in the Lead's context within 60 s but a `disk_state.changed_files` snapshot did land in the team-envelopes directory, this is **alpha.36 — silent lead-bound bus**. The teammate's `SendMessage` returns to the lead are being dropped. Recovery:

1. The Lead stops waiting for G7 envelopes via the bus and treats the file-channel envelope as the canonical liveness signal.
2. For each gate transition, the Lead sends one `SendMessage(<teammate>, "deliver findings now — write G7 envelope to .ai-assets-memory/sessions/<sid>/team-envelopes/G7-<role>-<wp>.json then return verdict in your next response")`.
3. The teammate writes the G7 envelope via `Bash` to the file-channel and additionally posts the verdict in its next conversation turn (verdict-in-response — same pattern as `eval-judge` and alpha.35 4d).
4. The Lead reads both, validates the file-channel G7 against `return-contract.schema.json`, and proceeds.
5. Record one line in `REVIEW-LOG.md` "Liveness events": `alpha.36: lead-bound bus dropped <N> consecutive G7 envelopes; switched to file-channel exclusively; <M> envelopes recovered from disk`.

Do NOT silently downgrade to Path A on alpha.36 — the team is still alive and producing work; only the upstream bus from teammates to lead is broken. File-channel keeps the pipeline running in Path B.

## Path B Liveness — Explicit Hand-off + Watchdog

Applies to Path B (Agent Teams) only. In alpha `in-process` mode any teammate — Developer, Reviewer, or QA — can go silently idle: their task stays `in_progress` (or sits at `completed` without a G7 envelope on the bus) while no transcript activity, no further tool calls, and no return arrive. The Lead MUST NOT rely on implicit pull alone, and MUST NOT assume Developer hand-offs are immune (alpha.31 generalised the flake to all roles).

The procedure below applies symmetrically to Developer, Reviewer, and QA. Read `<role>` as whichever teammate is currently expected to act.

1. **Explicit hand-off (push).** As soon as the upstream task transitions (Lead → Developer at WP start; Developer → Reviewer at DEV completion; Reviewer → QA at REVIEW approval) the Lead sends a direct message to the next teammate naming the task and the changed files: `"WP-N <dev|review|qa> claim now. Changed files: <paths>. Return G7 envelope when done."` The `dependsOn` auto-claim stays as a backup, not the primary trigger.

2. **Liveness watchdog — evidence-based, not time-based (v0.3.11).** The legacy 90 s × 2 cadence was tuned for visible-transcript work and produced false positives during genuine deep work (Read sequences, schema parsing, test runs). The watchdog now keys on **evidence absence**, not wall-clock:

   - **First check at ~180 s after the hand-off** (or whenever the next `TeammateIdle` envelope lands, whichever first). Inputs: latest envelope from `.ai-assets-memory/sessions/<sid>/team-envelopes/` for this teammate, plus `git status --short` for the WP's `active_files`.
     - Any evidence of progress (envelope timestamp newer than hand-off, OR `git status` shows any of `active_files` modified, OR the teammate task transitioned `pending` → `in_progress`) → reset the watchdog clock for another ~180 s window. Do NOT nudge.
     - No evidence on any of the three signals → send first nudge with the same hand-off payload plus `"Teammate appears idle — please confirm receipt and start <dev|review|qa>. If your TaskUpdate/SendMessage tools are unavailable, write a status line to .ai-assets-memory/sessions/<sid>/team-envelopes/status-<role>-<wp>.json via Bash and the Lead will pick it up."`
   - **Second check at ~180 s after first nudge.** Same evidence inputs. No progress → second nudge (and final). Total max wait: ~540 s (9 min) before escalation, but ANY of the three evidence signals collapses the timer to zero and grants another full window.
   - **Hard ceiling: 25 minutes wall-clock from the original hand-off** regardless of evidence (caps a teammate that is producing micro-progress but never converging).

   This replaces the v0.3.5–v0.3.10 90 s × 2 cadence. Idle notifications alone (without other evidence) are NOT a "no progress" signal — alpha runtime emits `idle_notification` pings even when the teammate is mid-tool-call. Filter them out unless they are the ONLY thing the teammate has produced.

   **Stale-`blockedBy` recovery (v0.3.9, alpha.31 secondary symptom).** If the silent teammate's task shows `blockedBy: [<upstream-id>]` and `<upstream-id>` is already `completed`, the panel state is stale and the teammate may be reading it as "still blocked". `TaskUpdate` has no `removeBlockedBy` operation. Recovery: the Lead deletes the stuck downstream task and re-creates it with no `blockedBy` (preserving description, owner, and a sentinel metadata field linking to the original task ID for audit). Record one line in `REVIEW-LOG.md` "Liveness events": `stale-blockedBy: task <new-id> replaces <old-id>; upstream <upstream-id> was completed but blockedBy did not auto-clear`. Run this BEFORE nudge #1 if the symptom is observed, not after — the teammate may engage immediately once the panel state is consistent.

   **Team-wide silent idle (v0.3.9, alpha.33).** If ≥ 2 teammates are simultaneously silent past the first 90-s window, OR if NO teammate produced any activity within the first 90 s after team-create + initial TaskCreate (alpha.33-fast-fail), the Lead SKIPS the second nudge cycle and goes directly to a whole-team escalation prompt:

   ```text
   [lead] Path B team-wide silent idle (alpha.33): <N>/<M> teammates produced no activity in 90s.
   Likely cause: CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS unset or team-runtime auto-claim disabled, despite TeamCreate returning success. Options:
   1. Wait longer (single watchdog cycle, +90 s)
   2. TeamDelete + re-TeamCreate (fresh team, same workflow)
   3. Per-task Path A fallback for every silent role this WP — remainder stays in Path B
   4. Path A for the remainder of the workflow (whole-workflow fallback, alpha.33 escape valve)
   5. Abort the current WP and skip
   ```

   Only a user-approved option 3 or 4 is a legitimate Path A fallback. Option 4 is allowed ONLY under alpha.33 / alpha.33-fast-fail — never as a silent rationalised downgrade.

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

   **4d. Reviewer silent — transcript shows complete findings (alpha.35, v0.3.10):**

   This sub-case applies when the Reviewer's transcript (Shift+↓) shows substantive review content with an explicit verdict (and often prose asking the Lead to "relay envelopes" or "update tasks on my behalf"), but the task stays `in_progress` and no G7 envelope arrives — a strong signal that the team-bus tool surface (`TaskUpdate` / `SendMessage`) is missing from the Reviewer's runtime augmentation, not that the Reviewer is genuinely idle. Recovery uses the verdict-in-response fallback (same pattern as `eval-judge`), NOT the generic escalation prompt:
   1. Lead pushes ONE targeted `SendMessage(<reviewer-id>, "deliver findings now — return verdict (approved | changes_requested) and per-file finding list in your next response; do not attempt TaskUpdate")`.
   2. Lead reads the Reviewer's conversation reply, writes the G7-equivalent envelope into `REVIEW-LOG.md`, and closes the Reviewer task with the verdict in the task summary.
   3. If `verdict: changes_requested`, apply the standard fix-round handling (insert developer follow-up task, re-point review/QA dependencies per `path-selection-rules.md` Step 3).
   4. Record one line in `REVIEW-LOG.md` "Liveness events": `alpha.35: reviewer <name> findings delivered via SendMessage conversation reply; verdict <verdict>; task <id> closed by Lead`.

   Hard rule for 4d: do NOT grant `TaskUpdate` / `TaskList` to the Reviewer as a recovery — that would break read-only role isolation (a Reviewer with task-write access can self-close its own task and effectively self-approve, defeating the gate). The verdict-in-response fallback is the only legitimate recovery for alpha.35. If the Reviewer cannot reply via the conversation bus either (no transcript activity at all), escalate as 4c instead.

   Only a user-approved option 3 is a legitimate per-task Path A fallback. Only a user-approved option 4 skips a WP. 4d is NOT a Path A fallback — it stays in Path B with the Reviewer delivering verdict-in-response. The remainder of the pipeline continues in Path B.

   **4e. First respawn failed — auto-offer per-task Path A (v0.3.11, F6).** If the user approved option 2 (respawn the teammate) at any of 4a/4b/4c/4d AND the respawned teammate ALSO fails the watchdog with the same symptom within one full watchdog window (~180 s evidence-free), the Lead does NOT loop a second respawn — `respawn-curing-respawn` is the documented field-failure mode of every 4* option. Instead, the Lead surfaces a tightened menu auto-defaulting to per-task Path A:

   ```text
   [lead] Path B <role> respawn-after-respawn failed on WP-N (same symptom as first respawn). Auto-fallback default: per-task Path A for this WP only — remainder stays in Path B. Other options:
   1. Run WP-N <role> via per-task Agent fallback (DEFAULT, applied in 30 s without explicit response)
   2. Abort WP-N and skip
   3. Wait one more watchdog cycle (last resort)
   ```

   Default-to-option-1 is the structural shift from v0.3.10 — passive waiting on a known-bad runtime is the most expensive failure mode the user reported in the v22 debrief. The 30 s auto-apply preserves user-veto without blocking on user input that may not arrive promptly.

5. **Logging.** Every nudge, every disk-state reconciliation, and every escalation choice MUST be recorded in `REVIEW-LOG.md` (free-form Notes or a "Liveness events" line per affected WP) so future runs can spot systemic flake. Include role, WP, nudge count, disk-state sub-case (`a`/`b`/`c` for Developer), and the user's chosen option.

### Hard rules — what the Lead MUST NOT do under silent-idle

- **Never synthesize a G7 return contract on behalf of a silent teammate.** The G7 envelope encodes evidence, risks, and `next_actions` that only the role agent has the context to produce. A Lead-fabricated envelope would pass schema validation but fail the faithfulness rubric and contaminate downstream review with hallucinated provenance. Even when disk state proves the work is done, the missing G7 is a real protocol gap — surface it (4b option 2 or 3), do not paper over it.
- **Never run Developer / Reviewer / QA work inline** as an idle workaround. Disk reconciliation (`git status` / `git diff` / `Read`) is monitoring; running tests, lint, build, or making edits on the Developer's behalf is role-isolation violation regardless of how cleanly disk state suggests the WP is done.
- **Never silently downgrade the whole session to Path A** because one teammate flaked. Per-task fallback (option 3) is the maximum allowed degradation, and only with explicit user approval.
- **Never skip the watchdog for Developer hand-offs.** Pre-v0.3.7 wording exempted Developer transitions from the watchdog on the assumption they were "already explicit"; alpha.31 invalidated that. Run the same 90s × 2 nudge cadence for every transition.

This procedure was extended in v0.3.7 from the v0.3.5 Reviewer/QA-only watchdog to also cover Developer silent-idle, after recurring observation of the "developer silent but acceptance criteria met on disk" sub-flake.

## TaskCreate API workaround — single-batch deps (v0.3.11, F7)

Path B `TaskCreate` does not accept `addBlockedBy` / `addBlocks` on creation — dependencies are a second-step `TaskUpdate` call. For a 4-WP plan that means 4 (DEV) + 4 (REVIEW) + 4 (QA) = 12 creates + 8 `TaskUpdate` deps = 20 round-trips for the bootstrap alone. This is acceptable cost, but it MUST be issued as a single batched message of independent tool calls rather than serially:

1. **Batch 1 (parallel-safe).** All `TaskCreate` calls for every WP × stage, no dependencies. Issue all of them in one assistant message so the harness executes them in parallel.
2. **Batch 2 (parallel-safe).** All `TaskUpdate(taskId=<x>, addBlockedBy=[<y>])` calls in a single assistant message — these only mutate the dependency graph and are independent of each other.

Total wall-time impact drops from "20× serial round-trips" to "2× parallel batches" — ~5 s vs. ~45 s on a fresh team-create.

`TaskUpdate` also has no `removeBlockedBy` operation. To clear a stale `blockedBy` after the upstream task is `completed` but the panel state hasn't refreshed, the procedure is **delete + recreate** the downstream task with no `blockedBy`, preserving description + owner + a sentinel metadata field linking to the original task ID for audit. See alpha.31 stale-`blockedBy` recovery above.

## Post-judge reconciliation (judge-based workflows only)

Applies to workflows where an `eval-judge` teammate produces a scored verdict (`/feature-design`, `/develop` RALF loops, `/refactor` test-equivalence gate). The Lead MUST treat the judge verdict as a snapshot-in-time reading and reconcile it against the current on-disk state of the design pack before declaring final pass / fail.

Procedure:

1. After the judge returns its verdict + scores, the Lead re-reads every file the judge cited as failing (typically those flagged with severity ≥ medium or any dimension score < 4).
2. For each cited issue, the Lead checks whether the file still contains the cited problem:
   - **Still present** → judge was correct; the workflow needs another RALF iteration or an explicit fix.
   - **Already fixed** (the fix landed between the judge's read and now — common when the Lead applied a quick Edit during judge execution) → record this as a judge-stale-read finding in `REVIEW-LOG.md`, increment the issue's resolution counter, and DO NOT count the issue against the final score.
3. If any cited issues turn out to be judge-stale-reads, the Lead appends a `## Lead Reconciliation Note` block to `REVIEW-LOG.md` listing each judge-cited issue, its actual on-disk state, and the adjusted dimension score where applicable. The reconciliation note is authoritative for those specific findings; the original judge verdict remains the canonical source for every finding NOT in the reconciliation note.
4. **Preferred alternative — re-spawn the judge.** If the count of judge-stale-read findings is ≥ 2 OR the resulting adjusted score would change the pass / fail verdict, the Lead re-spawns the judge on the current file state instead of writing a reconciliation note. A re-spawn is a clean source-of-truth; a reconciliation note is an annotation. Pick reconciliation only when (a) judge-stale-reads are isolated (≤ 1 finding) AND (b) the verdict does not flip from FAIL to PASS or vice versa.
5. Token budget for the reconciliation pass is bounded — the Lead reads ≤ N cited files (N = number of judge findings, no other reads), no Bash, no Edit. If the budget exceeds 20K tokens of Lead context, re-spawn the judge instead.

This procedure was added in v0.3.8 after `/feature-design` observed the judge reading file content before a Lead-side Edit landed, producing a stale FAIL verdict that did not match the converged design pack. Without reconciliation the Lead had to either silently override the judge (mutes the eval signal) or re-run RALF (wastes tokens converging an already-converged pack).

## Team cleanup checklist (Path B only)

After a Path B run finishes (PASS verdict accepted, IMPLEMENTATION-PLAN handed off, or user-approved abort), the Lead MUST close out the team:

1. Send `shutdown_request` to every teammate. Wait for shutdown acknowledgement per teammate.
2. If any teammate continues to emit `idle_notification` after shutdown_request, treat as a known alpha bus-flush flake — ignore subsequent notifications for that teammate name. Record one line in `REVIEW-LOG.md` "Liveness events" noting the post-shutdown idle pings so future runs can spot systemic flake.
3. Call `TeamDelete` for the team name. The team artefact persists in `~/.claude/teams/<team-name>/` until this call — leaving it strands a team config across sessions.
4. Print final cleanup line: `"[lead] Team <team-name> shut down; <N> teammates dismissed; team artefact removed."`

Cleanup is NOT optional. Skipping `TeamDelete` was observed in /feature-design alpha runs leaving stale `~/.claude/teams/<feature>-design-team/` directories that user-facing tooling later flagged as "active teams" even though their teammates were dead. Always call `TeamDelete` from the Lead, never from a teammate.

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
