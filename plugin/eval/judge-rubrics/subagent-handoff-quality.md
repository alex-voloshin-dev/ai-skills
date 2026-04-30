# Subagent Handoff Quality Rubric

## Overview

Cross-cutting rubric: subagent delegations follow G7 spawn payload + return contract per `team-protocols`. Applied to feature-design, develop, security-audit, migrate (any orchestrated workflow).

## Dimensions

### Dimension 1: Context Completeness (spawn payload)
Spawn payload `state_slice` contains everything the subagent needs (no follow-up questions required).

- **Level 1:** Subagent immediately needs more context
- **Level 2:** Subagent partially proceeds; one or two clarifications needed
- **Level 3:** Subagent proceeds; minor inferences required
- **Level 4:** Subagent proceeds without clarification
- **Level 5:** All of L4 + state_slice is minimal (no irrelevant context — no token waste)

### Dimension 2: Task Clarity (spawn payload `goal`)
Goal is one sentence, imperative, with concrete deliverable.

- **Level 1:** Goal is vague ("look at the code")
- **Level 2:** Goal stated; deliverable unclear
- **Level 3:** Goal + deliverable named
- **Level 4:** Goal + deliverable + acceptance criteria implicit
- **Level 5:** All of L4 + acceptance criteria explicit and measurable

### Dimension 3: Output Schema Correctness (return contract)
Return conforms to `plugin/schemas/return-contract.schema.json` — `trace_id`, `status`, `tokens_used`, `result.summary` all present and well-formed.

- **Level 1:** Free-form text return; no schema adherence
- **Level 2:** Some schema fields; many missing
- **Level 3:** All required fields present; some optional missing
- **Level 4:** All required + optional fields present; conforms to schema validation
- **Level 5:** All of L4 + `evidence` array populated with file:line citations

### Dimension 4: Error Recovery
On `status: failed` or `status: needs_clarification`, the contract carries enough info for the orchestrator to act.

- **Level 1:** Failure status with no diagnostic
- **Level 2:** Failure with vague reason
- **Level 3:** Failure with specific reason; no recovery suggestion
- **Level 4:** Failure + specific reason + recovery suggestion
- **Level 5:** All of L4 + `needs_clarification` field has a precise question (when applicable)

### Dimension 5: Trace Integrity
`trace_id` matches across spawn → return; orchestrator can correlate spawn chains.

- **Level 1:** No trace_id, or invalid format
- **Level 2:** trace_id present; format inconsistent across spawns
- **Level 3:** trace_id valid format (`wf-<date>-<id>-spawn-<seq>`)
- **Level 4:** trace_id valid + propagates through nested spawns (when applicable)
- **Level 5:** All of L4 + spawn chain reconstructable from trace_id alone

## Scoring Logic

- **Aggregate:** average of D1–D5
- **Pass threshold:** 4.0
- **Judge model:** Haiku (schema validation is mechanical)

## Anti-Patterns (Auto-Fail)

- Free-form HANDOFF text instead of G7 return contract
- `tools` field of spawn payload includes tools the agent's frontmatter forbids (`disallowedTools` violation)
- `trace_id` missing or unparseable
- `status: needs_clarification` without `needs_clarification` field
- Spawn payload `state_slice` includes secrets or unredacted PII

## Calibration Reference

- **Known-good:** `plugin/eval/calibration/subagent-handoff-quality/good/*`
- **Known-bad:** `plugin/eval/calibration/subagent-handoff-quality/bad/*`
