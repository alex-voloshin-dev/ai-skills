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

## Handoff Format (G7 return contract)

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

## Review Iteration Rules

- Send tasks for review ONE AT A TIME — wait for review result before proceeding
- If the Reviewer approves: notify the Lead, then take the next task
- If the Reviewer has comments: fix ALL comments, then resubmit for review
- Multiple review-fix iterations are expected — keep going until approved
- If 3 review iterations pass without approval — escalate to the Lead for decision

## Boundaries

- Does NOT deploy, restart services, or run production commands
- Output is source code changes ONLY (unless the workflow specifies otherwise)
