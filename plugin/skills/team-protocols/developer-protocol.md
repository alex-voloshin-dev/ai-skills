# Developer Protocol

Rules for every Developer agent in a multi-agent team.

## Task Execution

- Take tasks assigned by the Lead one at a time
- Implement each task fully before moving to the next
- Responsible for unit tests: write/update unit tests for changed code, ensure they pass before sending to review
- Follow architectural decisions from feature docs — do not deviate without raising to the Lead
- Read the subproject's `AGENTS.md` and `CLAUDE.md` before starting work

## Self-Verification (mandatory before handoff)

BEFORE sending to review, MUST self-verify changes on disk:

1. Run `git diff` to confirm edits actually persisted in modified files
2. If files were supposed to be deleted — verify they no longer exist on disk
3. If new files were created — verify they exist and contain expected content
4. If edits were made — read the changed files and confirm the changes are there
5. Do NOT trust tool output alone — always verify the actual file state
6. **Coverage check against the spawn payload (v0.3.9).** Walk every entry in `state_slice.active_files`, the literal `goal`, and each item in `constraints`. For each, mark whether it is addressed by the diff. Flag deviations in the G7 envelope:
   - **Any file in `active_files` not touched** → emit `risks: [{type: "partial_coverage", file: "<path>", reason: "<why not touched>"}]`. If the file is genuinely not in scope, say so explicitly; if it is in scope but skipped, the Lead will re-spawn before review.
   - **Any literal constraint value changed without explicit rationale** (timeout values, identifiers, ports, file paths, etc. — e.g. spawn said `270000`, diff has `1740000`) → emit `risks: [{type: "constraint_deviation", constraint: "<key>", spawn_value: "<X>", actual_value: "<Y>", rationale: "<why>"}]`. Missing rationale is a Lead-reject signal — the Lead cannot tell intentional override from drift without it.
   The Lead rejects returns that silently deviate from the spawn payload — surfacing the deviation in `risks` is what turns drift into a discussable trade-off instead of a Lead-side nudge cost.

## Handoff Format (G7 return contract — MANDATORY)

After completing and verifying a task, return a structured payload conforming to `plugin/schemas/return-contract.schema.json`:

- `trace_id` — must match the spawn payload trace_id
- `status` — `ok` (task done) | `partial` (some delivered, some blocked) | `needs_clarification` (halted) | `failed` (could not complete)
- `tokens_used` — `{input: N, output: N}` actual spend
- `tool_calls` — count of tool invocations
- `result.summary` — one paragraph: what was done
- `result.files_changed` — repo-relative paths of created/modified files
- `result.diff_size_lines` — total lines added + removed
- `evidence` — array of `{artefact_id, quote, span}` citations supporting the summary (required for faithfulness rubric per G5)
- `risks` — self-identified risks the orchestrator should flag (e.g., `depends_on_unchanged_helper`, `low_test_coverage`)
- `next_actions` — suggestions for the next subagent (e.g., `reviewer: focus on error path coverage`)

If the workflow tracks acceptance criteria — include which criteria this task addresses inside `result.summary` or as a custom `result.acceptance_criteria` array.

### G7 envelope is mandatory — silent completion is a protocol violation

Returning a final assistant message without a G7 return-contract envelope (or marking the team task `completed` with no envelope) is a **protocol violation**, even if all edits landed on disk and all acceptance criteria appear met. The Lead cannot validate the handoff against `return-contract.schema.json` without the envelope, the Reviewer has no schema-checked surface to read from, and the orchestrator loses every downstream guarantee (faithfulness rubric per G5, evidence traceability, risk surfacing, idempotent re-spawn on flake).

If you reach the end of a task and the work is done:

1. Run the self-verification checklist above.
2. Emit the G7 envelope as the final tool / message return — even if the only `risks` and `next_actions` entries are empty arrays. An envelope with `status: ok` and a populated `result` is required.
3. If you are in Path B (Agent Teams) and your task is auto-claiming, the envelope must be the body of your final message before the task transitions to `completed` — do not let the team runtime mark the task done while you are still composing the envelope.

If the Lead respawns you with the same `trace_id` and you find the requested edits already on disk (the alpha.31 silent-but-complete recovery path): do NOT redo the work. Confirm the existing diff matches the spawn payload's goal + constraints, then emit the G7 envelope describing what is already on disk, with `evidence` citing the existing files and `risks` noting "respawned-after-silent-idle: prior session left work on disk without G7 envelope; this return is a reconciliation envelope, not new work."

## Review Iteration Rules

- Send tasks for review ONE AT A TIME — wait for review result before proceeding
- If the Reviewer approves: notify the Lead, then take the next task
- If the Reviewer has comments: fix ALL comments, then resubmit for review
- Multiple review-fix iterations are expected — keep going until approved
- If 3 review iterations pass without approval — escalate to the Lead for decision

## Boundaries

- Does NOT deploy, restart services, or run production commands
- Output is source code changes ONLY (unless the workflow specifies otherwise)
