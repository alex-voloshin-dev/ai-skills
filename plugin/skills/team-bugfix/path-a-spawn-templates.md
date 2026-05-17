# Path A Spawn Templates (team-bugfix)

Verbatim `Agent({...})` invocation templates for Path A (Subagents fallback) of `/team-bugfix`. Loaded from `SKILL.md` when Path B technically fails and the Lead falls back to sequential per-task subagent spawns.

For each task from the audit plan, the Lead does this exactly:

**Step 1 — DEVELOP.** Spawn the Developer subagent via `Agent`:

```text
Agent({
  description: "<task-id> fix (<role>)",
  subagent_type: "ai-skills:<java-engineer | python-engineer | frontend-engineer | ...>",
  prompt: "You are the Developer subagent for audit task <ID>. Read plugin/skills/team-protocols/developer-protocol.md before starting. G7 spawn payload:\n\n<JSON-payload-per-team-protocols>\n\nWhen done, return a G7 return contract.",
  isolation: "worktree"
})
```

Wait for return. Validate the return contract.

**Step 2 — REVIEW.** Spawn the Reviewer subagent via `Agent`:

```text
Agent({
  description: "<task-id> review",
  subagent_type: "ai-skills:software-engineer",
  prompt: "You are the Reviewer subagent for audit task <ID>. Read plugin/skills/team-protocols/reviewer-protocol.md and plugin/skills/code-review/SKILL.md before starting. Files to review:\n<list-from-developer-return>\n\nDeveloper summary:\n<from-developer-return>\n\nAudit task brief:\n<original-audit-section>\n\nReturn a G7 contract with `result.verdict` set to 'approved' or 'changes_requested' with a structured issues list.",
  disallowedTools: ["Write", "Edit"]
})
```

Loop on `changes_requested` back to Step 1 with issues attached, until `approved`.

**Step 3 — QA.** Spawn the QA subagent via `Agent`:

```text
Agent({
  description: "<task-id> QA",
  subagent_type: "ai-skills:qa-engineer",
  prompt: "You are the QA subagent for audit task <ID>. Higher-level test scope (smoke / API / integration / E2E — NOT unit tests). Files changed:\n<list>\n\nReturn a G7 contract with `result.qa_verdict` set to 'pass' or 'fail' with issues."
})
```

Loop on `fail` back to Step 1, until `pass`.

## Lead progress reporting

The Lead progress table includes columns: #, Task, Developer subagent_type, Dev, Review, Review rounds, QA, Status.

Final summary includes: total tasks, review iterations, subagent_types used, unresolved issues, all changed files grouped by subproject, and the spawn ledger (count of `Agent` invocations per role).
