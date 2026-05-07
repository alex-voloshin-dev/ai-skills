# G7 Contracts and File Conflict Prevention (team-protocols)

The G7 spawn-payload + return-contract JSON examples, the `needs_clarification` halting protocol, and the file-conflict prevention rules. Loaded from `SKILL.md` when authoring a workflow that needs the literal contract shapes or the conflict-prevention sequencing rules.

## G7 Spawn Payload (Lead → Subagent)

Every spawn embeds a JSON payload conforming to `plugin/schemas/spawn-payload.schema.json` (full example in `spawn-pattern.md`). The `subagent-start-budget.py` hook validates the payload and enforces the budget against the session token meter.

## G7 Return Contract (Subagent → Lead)

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

## When `status: needs_clarification`

If the subagent halts awaiting user input, the return contract MUST include a `needs_clarification` field with the question. The Lead surfaces it to the user verbatim before re-spawning.

## Agent and File Conflict Prevention

**Single instance per role** — except Developers, where one instance per affected subproject stack is allowed (see `role-selection-table.md`). Do NOT spawn multiple Reviewers or multiple QA agents. Tasks within a role are processed strictly one at a time, sequentially.

**Only ONE agent may edit files at any time.** Agents take turns — never work on files in parallel.

- **Writing agents**: Developer(s) and QA (if the workflow includes higher-level test edits). Reviewer is always read-only (`disallowedTools: ["Write", "Edit"]` in the spawn).
- **If multiple Developers are spawned**: each gets `isolation: "worktree"` so they edit isolated copies and merge serially.
- **Workflow per task is strictly sequential**: Developer works → Developer returns → Reviewer reads → (QA works if applicable) → next task.
- **No overlap**: Developer MUST NOT be re-spawned for the next task while another writing agent is still active on the current task.
- **Lead enforces**: if two writing agents would be concurrent — the Lead waits for the first to return before spawning the second, and reports the queue state to the user.
