# Bugfix — Path B / Path A Pipeline Execution

Detailed mechanics for the `bugfix` DEV → REVIEW → QA pipeline. `SKILL.md`
keeps intake/analysis (Steps 1–6), the binding Gate Rules, and final
verification; this file keeps the executable Path B / Path A detail. **Read
this file and apply the steps verbatim** when driving the pipeline — these
rules are mandatory, not optional reference. Behavior is identical to the
prior single-file form.

## Path B — Agent Teams (PREFERRED — try this FIRST)

### Step 1 — create the team

```text
Create an agent team named "<bug-id>-bugfix-team" with these teammates, all using subagent definitions from the ai-skills plugin:

- "developer" (ai-skills:<java-engineer | python-engineer | frontend-engineer | ...>) — implements the fix per the bug report's affected-components list, follows team-protocols/developer-protocol.md, isolation: worktree
- "reviewer" (ai-skills:software-engineer) — read-only review (disallow Write/Edit), follows reviewer-protocol.md, applies code-review skill
- "qa" (ai-skills:qa-engineer) — runs the regression test, full test suite, smoke checks; follows the QA section of develop/SKILL.md

Use teammate-mode `in-process` by default. Pick `tmux` split-pane mode ONLY if the user has explicitly indicated tmux or iTerm2 is available.
```

### Step 2 — populate the shared task list

Three tasks per fix iteration (DEV / REVIEW / QA) linked via `dependsOn`. If
the bug report identifies multiple affected components / stacks, create one
DEV task per component (with `isolation: worktree`).

### Step 3 — drive and monitor

Teammates self-claim next unblocked task. On reviewer `changes_requested` →
Lead inserts a follow-up DEV task and re-points dependencies. On QA `fail` →
same. Loop until reviewer approves AND QA passes.

**Liveness watchdog (v0.3.7).** Any teammate (Developer included) can silently
idle in `in-process` mode — covering the alpha.31 "silent-but-complete"
Developer sub-flake. Full procedure (explicit hand-off, 90 s watchdog × 2
nudges, disk-state reconciliation on Developer-silent, role-specific
escalation menu, no Lead-synthesized G7) in
`@team-protocols/lead-protocol.md` "Path B Liveness".

### Step 4 — final cleanup

After the fix passes the pipeline: run final verification in main thread (full
test suite, linter), produce the Step 9 (Summary) report, then ask: "Clean up
the team."

## Path A — Subagents fallback (only if Path B Step 1 returned a technical error)

If Path B Step 1 returns a literal "Agent Teams not enabled" / equivalent
technical error, fall back silently to Path A: per-fix sequential spawns of
Developer → Reviewer → QA via the `Agent` tool.

> The verbatim per-step `Agent({...})` invocation templates (DEVELOP / REVIEW
> / QA), the `disallowedTools: ["Write", "Edit"]` reviewer constraint, the
> `isolation: "worktree"` directive, and the loop-on-`changes_requested` /
> loop-on-`fail` rules live in
> [`team-bugfix/path-a-spawn-templates.md`](../team-bugfix/path-a-spawn-templates.md).
> The same templates apply here — the only difference vs `/team-bugfix` is the
> input shape (one bug from a report vs N issues from an audit doc). Load the
> template file when actually executing the Path A fallback loop.
