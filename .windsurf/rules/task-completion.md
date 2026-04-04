---
trigger: model_decision
description: Task completion self-verification — prevents agents from reporting work as done when plan items are skipped, incomplete, or silently dropped.
---

# Task Completion Verification

This rule applies to every agent. Never report work as complete without running the self-audit below.

## Before Reporting Completion

When you finish working on an assigned task, plan, or multi-step request:

1. **Re-read the original request or plan** — go back to the user's message, the plan steps, or the task list that started this work
2. **Build a checklist** — list every discrete deliverable or action item from the plan
3. **Audit each item** — for every item, verify one of:
   - **Done**: the deliverable exists and meets the stated criteria
   - **Partially done**: state what was completed and what remains
   - **Skipped**: state why (blocked, out of scope, needs user input)
   - **Not applicable**: state why the item no longer applies
4. **Report honestly** — include the checklist in your completion report. Never collapse multiple items into a vague summary

## Completion Report Format

Structure your completion message as:

```
## Completed
- [x] Item 1 — what was delivered
- [x] Item 2 — what was delivered

## Incomplete (if any)
- [ ] Item 3 — reason (blocked by X / needs user input / out of scope)

## Issues Found (if any)
- Description of unexpected problems encountered
```

## Hard Rules

1. **Never say "done" with skipped items hidden** — if any planned item was not delivered, it must appear in the Incomplete section
2. **Never silently reduce scope** — if you decided to skip something, say so and say why
3. **Never substitute a different deliverable** — if the plan says "write integration tests" and you wrote unit tests instead, that is not done — report it as a scope change
4. **Verify artifacts exist** — if the task was to create a file, confirm the file exists. If the task was to run tests, confirm you actually ran them and include results
5. **Re-read before final message** — the last thing you do before writing your completion report is re-read the original plan one more time

## When Working Without a Plan

If the user gave a direct request (not a multi-step plan):

1. Restate what was asked
2. Confirm what was delivered
3. Flag anything that was not done or needs follow-up

## Escalation

If you discover during self-audit that you missed something:
- **Do not report completion** — go back and finish the work
- If finishing is blocked — report what is done and what is blocked, with the reason
