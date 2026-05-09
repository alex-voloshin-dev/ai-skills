---
name: bugfix
description: >-
  End-to-end bugfix workflow with mandatory DEVELOP → REVIEW → QA pipeline.
  Lead orchestrates triage intake, environment analysis (`/env-analyze` for
  local, `/analyze-prod` for production), evidence collection, and bug report
  — then spawns developer/reviewer/QA via the Anthropic `Agent` tool to apply,
  review, and verify the fix. Use when investigating, diagnosing, and fixing
  a reported bug.
argument-hint: "[bug description or error message]"
---

<!-- ARCHITECTURAL NOTE: no `context: fork` here. Per Anthropic docs, subagents cannot spawn other subagents. The DEV/REVIEW/QA pipeline requires the `Agent` tool, which is only available in the main thread. -->


# Bugfix (Multi-Agent Pipeline)

End-to-end bugfix workflow. The Lead handles intake / env analysis / evidence / bug report in the main thread, then drives a mandatory **DEVELOP → REVIEW → QA** pipeline by spawning named subagents via the **`Agent` tool** for the implementation, review, and verification of the fix.

You are the Lead. Read `@team-protocols` end-to-end before issuing the first spawn — it covers the spawn pattern, role-by-role mapping, conflict prevention, dual-path detection, and the G7 spawn payload + return contract schemas.

> **YOU MUST spawn subagents via `Agent({...})`.** Do not perform Developer / Reviewer / QA work inline with `Bash`/`Read`/`Edit`. Doing so violates the team-protocols hard invariant — the user loses per-role inspection and the pipeline gates collapse. Every fix-apply / review / verify step in this skill is an explicit, executable `Agent({...})` call.

## 1. Receive Bug Report

Gather from the user (Lead, main thread):

- Expected vs actual behavior, error message / stack trace, steps to reproduce
- Environment (local Docker / cloud production / code-only)
- When it started (after deploy / config change / unknown), recent commits
- Severity: P1 (outage), P2 (degraded), P3 (minor), P4 (cosmetic)

For P1/P2 — skip detailed intake and proceed immediately to Step 2.

## 2. Analyze Environment

Based on the environment, delegate to the appropriate diagnostic sub-workflow (these are skills, not subagent spawns — they run inline):

| Environment | Sub-workflow |
|---|---|
| Local Docker / Docker Compose | `/env-analyze` (or `/analyze-local`) |
| Cloud production (GKE/AKS/EKS, managed DB) | `/analyze-prod` |
| Code-only (no infra) | Skip to Step 3 |

The sub-workflow applies the diagnostic role (`Agent(sre-engineer)` / `Agent(devops-engineer)`), collects environment snapshot, and presents diagnosis. **If it resolves the issue at the infra layer** — skip to Step 9 (Summary). **If the root cause is in application code** — continue to Step 3 with the collected evidence.

## 3. Detect Stack and Pick Developer Role

Determine the affected service's tech stack to choose the right Developer `subagent_type` for the pipeline:

1. Read `CLAUDE.md` / `AGENTS.md` — tech stack declaration
2. Scan project files (`package.json`, `pom.xml`, `requirements.txt`, `go.mod`)
3. Inspect Step 2 evidence — which language is the stack trace in?

| Stack signal | Developer `subagent_type` |
|---|---|
| Next.js, React, TypeScript, `.tsx` files | `ai-assets:frontend-engineer` |
| Spring Boot, Java, `.java` files | `ai-assets:java-engineer` |
| FastAPI, Python, `.py` files | `ai-assets:python-engineer` |
| Terraform, Dockerfile, Helm, CI/CD | `ai-assets:devops-engineer` |
| ML model, training pipeline, inference | `ai-assets:ml-engineer` |
| Multiple stacks | One Developer per affected stack (sequential per `subagent-isolation.md`) |
| Unknown / general | `ai-assets:software-engineer` |

Announce the selected Developer role(s) to the user.

## 4. Collect Evidence

Gather a structured evidence collection (Lead, main thread). Combine Step 2 environment data with code-level investigation:

- Error output (full message, stack trace, exit code)
- Logs (timestamped) from the affected service
- Reproduction (local? consistent or intermittent?)
- Scope (which endpoints / features / components)
- Timeline + recent commits (`git log -n 20 --oneline`)
- Triggering inputs (request payload, user ID, dataset)
- Production metrics (error rate, latency change, affected users) if relevant
- Related code (files, functions, lines most likely involved)

Identify the **minimal reproduction case** — this becomes the regression-test oracle in Step 7.

## 5. Prepare Bug Report

Compile findings into a structured bug report (Summary, Severity, Environment, Expected/Actual, Steps to reproduce, Evidence, Root cause analysis, Affected components). Present to the user. Wait for confirmation that the diagnosis is correct before committing the fix to the pipeline.

## 6. Choose execution path (ATTEMPT Path B FIRST — literal, mandatory)

Per `@team-protocols/path-selection-rules.md`: Path B (Agent Teams) is MANDATORY default — visual team panel, Shift+↓ context-switching, dedicated transcript per role. Path A (sequential subagents) is fallback-only.

Detection is implicit — go to Path B Step 1 directly, no Bash env-var check. The ONLY valid Path A trigger is a literal "Agent Teams not enabled" / equivalent technical error from team-creation. Display-mode, platform, "small bug", "sequential pipeline", "single-stack", "Windows host", or "no tmux" — NEVER valid Path A triggers (Path B has `in-process` mode that works in any terminal). **No silent fallback for non-technical reasons** — rationalised downgrades violate alpha.27.

The FIRST sentence when announcing the path MUST be one of:

- "Attempting Path B (Agent Teams) team-create..."
- (after fallback) "Agent Teams API returned: <verbatim error>. Falling back to Path A."

## 7. Mandatory Pipeline — DEV → REVIEW → QA (both paths)

Every fix MUST pass all three stages. Gate semantics are identical regardless of execution path; only the spawn mechanism differs.

### Gate Rules

1. The fix CANNOT enter REVIEW until the Developer's `Agent` call returns a valid G7 contract.
2. The fix CANNOT enter QA until the Reviewer's contract has `verdict: approved`.
3. The fix is NOT COMPLETE until QA returns `qa_verdict: pass`.
4. If the Developer reports "no changes needed" — the Reviewer STILL runs (independent confirmation).
5. If any spawn returns malformed JSON — re-spawn the same role with a corrected prompt; do NOT advance.
6. **The Lead MUST NEVER skip a spawn and do the work inline.**

Optional RALF on the reproduction test (kill-on `oracle-pass`): wrap the DEV spawn in `/ralph` per `ralph-budget.md` for intermittent / environment-dependent / hard-to-converge bugs (race conditions, memory leaks, off-by-ones). Defaults: 6 iter / 300K tokens / 60 min. Skip RALF for trivial bugs where the regression test passes on the first DEV iteration.

## Path B — Agent Teams (PREFERRED — try this FIRST)

### Step 1 — create the team

```text
Create an agent team named "<bug-id>-bugfix-team" with these teammates, all using subagent definitions from the ai-assets plugin:

- "developer" (ai-assets:<java-engineer | python-engineer | frontend-engineer | ...>) — implements the fix per the bug report's affected-components list, follows team-protocols/developer-protocol.md, isolation: worktree
- "reviewer" (ai-assets:software-engineer) — read-only review (disallow Write/Edit), follows reviewer-protocol.md, applies code-review skill
- "qa" (ai-assets:qa-engineer) — runs the regression test, full test suite, smoke checks; follows the QA section of develop/SKILL.md

Use teammate-mode `in-process` by default. Pick `tmux` split-pane mode ONLY if the user has explicitly indicated tmux or iTerm2 is available.
```

### Step 2 — populate the shared task list

Three tasks per fix iteration (DEV / REVIEW / QA) linked via `dependsOn`. If the bug report identifies multiple affected components / stacks, create one DEV task per component (with `isolation: worktree`).

### Step 3 — drive and monitor

Teammates self-claim next unblocked task. On reviewer `changes_requested` → Lead inserts a follow-up DEV task and re-points dependencies. On QA `fail` → same. Loop until reviewer approves AND QA passes.

**Liveness watchdog (v0.3.5).** In `in-process` mode the Reviewer / QA can go silently idle after a `dependsOn` claim. Lead MUST push explicit hand-off, run 90 s watchdog, retry up to 2 nudges, escalate after 3 — full procedure in `@team-protocols/lead-protocol.md` "Path B Liveness".

### Step 4 — final cleanup

After the fix passes the pipeline: run final verification in main thread (full test suite, linter), produce the Step 9 (Summary) report, then ask: "Clean up the team."

## Path A — Subagents fallback (only if Path B Step 1 returned a technical error)

If Path B Step 1 returns a literal "Agent Teams not enabled" / equivalent technical error, fall back silently to Path A: per-fix sequential spawns of Developer → Reviewer → QA via the `Agent` tool.

> The verbatim per-step `Agent({...})` invocation templates (DEVELOP / REVIEW / QA), the `disallowedTools: ["Write", "Edit"]` reviewer constraint, the `isolation: "worktree"` directive, and the loop-on-`changes_requested` / loop-on-`fail` rules live in [`team-bugfix/path-a-spawn-templates.md`](../team-bugfix/path-a-spawn-templates.md). The same templates apply here — the only difference vs `/team-bugfix` is the input shape (one bug from a report vs N issues from an audit doc). Load the template file when actually executing the Path A fallback loop.

## 8. Self-Review and Final Verification (Lead, main thread)

After the pipeline returns the final fix:

- Re-read every changed file diff — verify correctness and completeness against the Step 5 bug report
- Run linter on changed files — zero warnings
- Run formatter — zero diffs
- Run the full test suite (or `/run-tests`) one more time — all tests pass
- For production bugs: verify the fix locally first; deploy through normal CI/CD (no direct prod hotfix); after deploy re-run relevant `/analyze-prod` checks; monitor error rates and SLIs

Do NOT declare the bug fixed until every item passes.

## 9. Summary

Present the completed bugfix:

- **Bug** (one sentence) and **severity** (P1–P4)
- **Environment** (local / production) and **roles applied** (developer + reviewer + qa subagent_types)
- **Root cause** (technical explanation)
- **Fix** (files changed, brief description) and **tests added** (count + description)
- **Pipeline trace**: DEV/REVIEW/QA iterations + verdicts (e.g. `DEV-1 → REVIEW changes_requested → DEV-2 → REVIEW approved → QA pass`)
- **Verification** (how it was confirmed fixed)
- **Remaining issues**: NONE (if any remain, go back through the pipeline before reporting)
- **Prevention**: recommendations to avoid similar bugs

## Integration

- **Sub-workflows (inline, not spawns)**: `/env-analyze` (local Docker diagnostic), `/analyze-prod` (production diagnostic), `/ralph` (optional RALF wrap on the DEV spawn for hard-to-converge bugs)
- **Auxiliary multi-agent skill**: `/team-bugfix` (same DEV/REVIEW/QA pipeline applied to a batch of issues from a code-review or audit document — use it when the input is an audit doc rather than a single bug report)
- **Followed by**: `/run-tests` (final test gate), `/pre-commit` (commit gate), `/create-pr` (submit fix)
- **Protocols**: `@team-protocols` (execution model, spawn primitives, agent coordination, G7 contracts)
- **Schemas**: `plugin/schemas/spawn-payload.schema.json`, `plugin/schemas/return-contract.schema.json`
- **Skills**: `code-review` (Reviewer applies), `test-strategy` (QA applies), `worktree-isolation` (multi-Developer isolation)
- **Rules**: `subagent-isolation` (G7 + bounded recursion + sequential code-mod gate), `ralph-budget` (RALF caps), `untrusted-content-wrapping` (G1 wrap on `/env-analyze` + `/analyze-prod` outputs)
