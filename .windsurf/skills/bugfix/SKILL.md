---
name: bugfix
description: End-to-end bugfix workflow — analyze environment (local Docker or cloud production), collect evidence, prepare bug report, plan fix, apply appropriate engineer role, implement and verify the fix.
context: fork
argument-hint: [bug description or error message]
---

# Bugfix

End-to-end workflow for investigating, diagnosing, and fixing bugs. Orchestrates environment analysis (`analyze-local` skill or `analyze-prod` skill), evidence collection, bug report preparation, fix planning, and implementation by the appropriate engineering role.

## 1. Receive Bug Report

Gather the bug description from the user:

- **What is the expected behavior?**
- **What is the actual behavior?** (error message, wrong output, crash, performance issue)
- **Steps to reproduce** (if known)
- **Environment**: local (Docker) or production (cloud K8s)?
- **When did it start?** (after deploy, config change, or unknown)
- **Severity**: P1 (outage), P2 (degraded), P3 (minor), P4 (cosmetic)

If the user provides partial information, extract what you can and fill gaps during analysis. For P1/P2 — skip detailed intake and proceed immediately to Step 2.

## 2. Analyze Environment

Based on the environment, delegate to the appropriate analysis follow-up skill:

| Environment | follow-up skill | When to use |
|---|---|---|
| Local Docker / Docker Compose | `analyze-local` skill | Bug observed in local dev environment |
| Cloud production (GKE/AKS/EKS, managed DB) | `analyze-prod` skill | Bug observed in production or staging |
| Code-only (no infra) | Skip to Step 3 | Bug is in application logic, no environment analysis needed |

Run the follow-up skill. It will:
- Apply the appropriate diagnostic role (`sre-engineer` role or `devops-engineer` role)
- Collect environment snapshot (container/pod status, logs, metrics, networking)
- Identify infrastructure-level issues
- Present diagnosis

**If the follow-up skill resolves the issue** (e.g., container restart, config fix) — skip to Step 8.

**If the root cause is in application code** — continue to Step 3 with the collected evidence.

## 3. Detect Stack and Apply Engineer Role

Determine the affected service's tech stack and apply the appropriate engineering role:

1. **Read project's `AGENTS.md`** — tech stack declaration
2. **Scan project files** — `package.json`, `pom.xml`, `requirements.txt`, `go.mod`, etc.
3. **Check evidence from Step 2** — which service's logs show the error? What language is the stack trace in?

**Role assignment:**

| Stack Signal | Role |
|---|---|
| Next.js, React, TypeScript, `.tsx` files | `frontend-engineer` role |
| Spring Boot, Java, `.java` files | `java-engineer` role |
| FastAPI, Python, `.py` files | `python-engineer` role |
| Terraform, Dockerfile, Helm, CI/CD | `devops-engineer` role |
| ML model, training pipeline, inference | `ml-engineer` role |
| Multiple stacks affected | Apply all relevant roles |
| Unknown / general | `software-engineer` role |

Announce the applied role(s) to the user.

## 4. Collect Evidence

Gather all evidence into a structured collection. Combine data from Step 2 (environment analysis) with code-level investigation:

<evidence_checklist>
- **Error output**: Full error message, stack trace, exit code
- **Logs**: Relevant log entries (timestamped) from the affected service
- **Reproduction**: Can you reproduce locally? Consistent or intermittent?
- **Scope**: Which endpoints / features / components are affected?
- **Timeline**: When did it start? What changed? (recent commits, deploys, config)
- **Data**: Specific inputs that trigger the bug (request payload, user ID, dataset)
- **Metrics** (if from prod): Error rate, latency change, affected user count
- **Related code**: Files, functions, lines most likely involved
</evidence_checklist>

Use the applied role's debugging methodology to trace the bug:
- Read error stack traces to identify the failing code path
- Search codebase for related functions, error handlers, and data flows
- Check recent changes (`git log -n 20 --oneline`) for potential regressions
- Identify the **minimal reproduction case**

## 5. Prepare Bug Report

Compile findings into a structured bug report. Present to the user for review:

```
## Bug Report

### Summary
[One sentence: what is broken]

### Severity: [P1 | P2 | P3 | P4]

### Environment
- **Type**: [local | production]
- **Service**: [name]
- **Stack**: [detected] | **Role**: [applied]

### Expected Behavior
[What should happen]

### Actual Behavior
[What actually happens — include error messages]

### Steps to Reproduce
1. [step]
2. [step]
3. [observed error]

### Evidence
- **Stack trace**: [snippet or reference]
- **Logs**: [relevant entries]
- **Metrics**: [if applicable]
- **Affected code**: [file:line references]

### Root Cause Analysis
[Technical explanation of why the bug occurs]

### Affected Components
- [file/module 1] — [how it's affected]
- [file/module 2] — [how it's affected]
```

Wait for user confirmation before proceeding to fix.

## 6. Plan the Fix

Create an ordered fix plan following the applied role's guidelines:

1. **Root cause fix** — address the actual cause, not symptoms
2. **Complete fix** — fix everything described in the bug report. Do not leave cosmetic issues, lint warnings, or minor problems unfixed. Do not create follow-up tickets for things you can fix now
3. **Regression test** — test that would have caught this bug
4. **Related fixes** — any adjacent issues discovered during investigation. Fix them in the same changeset — do not increase tech debt

Present the plan:

```
## Fix Plan

### Root Cause
[What caused the bug — one sentence]

### Changes
1. [file] — [what to change and why]
2. [file] — [what to change and why]
...

### Tests
1. [test file] — [test that reproduces and verifies the fix]
2. [test file] — [regression test for edge cases]

### Risk Assessment
- **Blast radius**: [which features could be affected by this change]
- **Rollback**: [how to revert if the fix causes issues]
```

Wait for user approval before implementing.

## 7. Implement the Fix

Execute the approved plan step by step.

**For each change:**
1. State what you are about to do (file, change summary)
2. Implement the fix following the applied role's code quality standards
3. Verify the code compiles/parses without errors

**Then write tests:**
1. **Regression test**: Reproduces the original bug — must fail without fix, pass with fix
2. **Edge case tests**: Cover related scenarios discovered during investigation
3. Run the full test suite to catch regressions

**Rules:**
- Fix the root cause, not the symptom
- Fix EVERYTHING reported in the bug — do not leave non-blocking or cosmetic issues unfixed
- Fix all lint errors, style violations, and warnings introduced or exposed by the change
- Follow existing code patterns and conventions
- No new warnings or linter errors — and fix pre-existing ones in the affected files if trivial
- Do not defer fixes to "follow-up" tasks — complete the fix in this changeset
- Do not increase tech debt — if you touch it, leave it better than you found it
- If the fix is more complex than expected — stop and discuss with the user
- If you need more information about the environment, run specialized follow-up skills (`analyze-local` skill or `analyze-prod` skill) to collect it

## 8. Self-Review the Fix

Before declaring the bug fixed, perform a thorough self-review. Do NOT skip this step.

**Code review checklist:**
- [ ] Re-read every changed file diff — verify correctness and completeness
- [ ] Every item from the bug report or user description is addressed — nothing left unfixed
- [ ] No cosmetic issues, lint warnings, or style violations remain in changed files
- [ ] No TODO, FIXME, or "will fix later" comments introduced
- [ ] No tech debt created — the code is clean and production-ready
- [ ] Run linter on all changed files — zero warnings
- [ ] Run formatter on all changed files — zero diffs

If the self-review reveals any remaining issues — fix them before proceeding. Do not declare the bug fixed with known remaining problems.

## 9. Verify the Fix

Verify the bug is resolved in the appropriate environment:

**For local bugs:**
- Run the reproduction steps — confirm the bug no longer occurs
- Run the full test suite — all tests pass (new + existing)
- If Docker-based: rebuild and verify with `analyze-local` skill (optional)
- If you need more data, run specialized follow-up skills for `analyze-local` skill to collect environment state

**For production bugs:**
- Verify the fix locally first
- Deploy through normal CI/CD pipeline (do NOT hotfix production directly)
- After deploy: re-run relevant checks from `analyze-prod` skill to confirm resolution
- Monitor error rates and SLIs for regression

**Verification checklist:**
- [ ] Original bug no longer reproduces
- [ ] ALL items from the bug report are fixed — not just the primary symptom
- [ ] Regression test passes
- [ ] Full test suite passes (no new failures)
- [ ] Linter passes with zero warnings on changed files
- [ ] No unrelated files modified
- [ ] Code follows project conventions and role guidelines
- [ ] No deferred work — everything is done in this changeset

If any check fails — fix and re-verify. Do NOT declare the bug fixed until every checkbox passes.

## 10. Summary

Present the completed bugfix:

- **Bug**: one-sentence summary
- **Severity**: P1–P4
- **Environment**: local / production
- **Role(s) applied**: which roles were used
- **Root cause**: technical explanation
- **Fix**: what was changed (files, brief description)
- **Tests added**: count and description
- **Self-review**: passed — all items verified
- **Verification**: how it was confirmed fixed
- **Remaining issues**: NONE (if any remain, go back and fix them before reporting)
- **Prevention**: recommendations to avoid similar bugs (e.g., add validation, improve error handling, add monitoring)

## Integration

- **follow-up skills**: `analyze-local` skill, `analyze-prod` skill (environment diagnostics — launch as specialized skills when more data is needed)
- **Follow-up**: `run-tests` skill (verify fix), `pre-commit` skill (quality gate), `create-pr` skill (submit fix)
- **Skills**: `code-review` skill (review fix), `testing-procedures` skill (test strategy), `worktree-isolation` skill (branch isolation)
