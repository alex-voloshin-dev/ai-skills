# Spawn Pattern (team-protocols)

The literal `Agent({...})` invocation pattern, the JSON G7 spawn-payload example, the validate-and-pass-through steps, and the role-by-role spawn map. Loaded from `SKILL.md` when authoring or auditing a workflow that spawns DEV/REVIEW/QA subagents.

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

- **Plugin agents** (the 26 specialized agents this plugin ships) — use the scoped form: `ai-skills:java-engineer`, `ai-skills:frontend-engineer`, `ai-skills:qa-engineer`, etc. The `<plugin-name>` prefix is the `name` field from `plugin/.claude-plugin/plugin.json` (`ai-skills`); the `<agent-name>` is the `name` frontmatter from `plugin/agents/<file>.md`.
- **Built-in subagents** — `general-purpose`, `Explore`, `Plan`, `statusline-setup`. Use `general-purpose` as the universal fallback when a more specific role is unavailable.

### Hard constraints (per Anthropic docs)

1. **Subagents cannot spawn other subagents.** All orchestration MUST happen in the Lead (main thread). The Developer / Reviewer / QA subagents you spawn cannot themselves spawn more agents.
2. **Each `Agent` call creates fresh context.** No conversation history is shared with the spawned subagent unless you put it in the `prompt`. Pass everything the role needs to know.
3. **Spawn results return to the Lead, not to other subagents.** The Lead is the message bus.

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
  subagent_type: "ai-skills:java-engineer",
  prompt: "You are the Developer subagent for work package WP-3. Read the developer role card at plugin/skills/team-protocols/role-cards/developer-card.md before starting (slim card — do NOT read lead-protocol.md or path-selection-rules.md, those are lead-only). Your G7 spawn payload:\n\n<JSON-from-step-1>\n\nWhen done, return a G7 return contract (per plugin/schemas/return-contract.schema.json) summarizing files changed, tests added, and any risks.",
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
| 1 | Developer (per stack) | `ai-skills:java-engineer` / `ai-skills:python-engineer` / `ai-skills:frontend-engineer` / etc. — pick from `role-selection-table.md` | One Developer per affected subproject; sequential code-modification gate per `subagent-isolation.md` |
| 2 | Reviewer | `ai-skills:software-engineer` | Read-only via `disallowedTools: ["Write", "Edit"]` in the `Agent` call |
| 3 | QA | `ai-skills:qa-engineer` | Higher-level tests only — Developer owns unit tests |

If a more specific specialized agent is unavailable in this plugin install, fall back to `subagent_type: "general-purpose"` and put the role brief entirely in the prompt.
