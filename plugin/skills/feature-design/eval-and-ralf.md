# Eval, RALF, Memory, and Observability (feature-design)

Eval rubric scoring, RALF iteration caps, memory-write layers, failure modes, and observability events for `/feature-design`. Loaded from `SKILL.md` when running the Wave-3 → RALF retry loop, validating rubric scores, or diagnosing why a design didn't converge.

## Eval rubric

Pointer: `plugin/eval/judge-rubrics/feature-design.md` (B10 deliverable).

Six dimensions × 5 levels:

1. **Completeness** — all required artefacts present with depth
2. **Internal consistency** — no cross-doc contradictions, coherent vision
3. **Traceability** — requirements map to components map to test cases
4. **Handoff clarity** — engineer can begin work without back-and-forth
5. **Risk coverage** — identified, scored, mitigations specified
6. **GEO/marketing readiness** (if public-facing) — passes geo-audit + humanizer standards

Pass: avg ≥ 4.0, no dimension < 3.

## RALF wiring

- **Oracle:** `judge:feature-design.md` (min_score 4.0)
- **Kill-on:** `regex:RUBRIC_FAILED_3X`
- **Caps:** 5 iter / 250K tokens / 60 min — overridable in userConfig
- **State:** `<repo>/.ai-assets-memory/ralph/<run-id>/`

## Memory writes

| Layer | When | Shape |
|---|---|---|
| L4 | After Wave 1 complete | `.ai-assets-memory/designs/<feature-id>/wave1-summary.md` — high-level decisions per agent |
| L4 | After RALF complete | `.ai-assets-memory/designs/<feature-id>/final.md` — trace of rubric scores + converged design |
| L4 (committed, opt-in) | Before handoff | `.ai-assets-memory/.committed/designs/<feature-id>.md` — finalized snapshot for team review |

## Failure modes

- **Wave 1 or 2 subagent timeout:** lead retries once with explicit error context. If persistent, escalates to user with "narrow scope" instruction
- **Rubric score oscillates:** RALF detects same-issue-3X pattern, kills loop, writes diagnostic suggesting design ambiguity
- **Oracle (judge) crashes:** treat as `ORACLE_ERROR`; kill loop; surface full diagnostic from eval-judge stderr
- **Budget hit mid-RALF:** hard pause; prompt user to confirm continuation, raise budget, or abort
- **Judge returns intermediate response with continuation `agentId` (v0.3.10, observed in field feedback):** Path B `eval-judge` is intended to be a single-shot foreground call returning the fenced JSON verdict in its first response. A subset of alpha Agent Teams runtimes treat the call as background and return an intermediate message ("Let me check the wireframes...") plus a continuation `agentId` instead of the final verdict. Recovery: the Lead issues a single `SendMessage` to the returned `agentId` with `"continue — return the final verdict JSON now"` and waits for the second response. If the second response is also intermediate, treat as oracle crash (`ORACLE_ERROR`) and surface to the user — do NOT loop continue-prompts. Record `judge-intermediate-recovered` or `judge-intermediate-failed` in `REVIEW-LOG.md` "Liveness events" with the agentId.

## Wave-2.5 pre-judge fix-sweep — policy

Empirically the Lead has sometimes applied a single in-Lead documentation fix-sweep between Wave-2 producers completing and Wave-3 judge running, based on PM-review / sysarch-review findings, when the findings are unambiguous doc-edit fixes (missing section headers, broken cross-refs, typos in user stories). This shortcut can pass the judge on first try without invoking RALF, but it bypasses the rubric-failure → RALF retry contract.

Policy (v0.3.10):

- **Permitted only for prose-level, non-substantive doc edits** — section header insertion, cross-reference path fix, typo, formatting normalisation. The Lead does these in its own main thread using `Edit`. This is monitoring/curation work, not Developer/Designer/Architect work, so it does not violate role isolation.
- **Forbidden for substantive content changes** — new acceptance criteria, new threat-model entries, architectural revisions, new risks, new wireframes, new data-model rows. These MUST go back to the originating Wave-2 producer (re-spawn via `SendMessage` with the finding) — bypassing them strips role authorship from the design pack and breaks traceability.
- **Forbidden for changes that touch the judge's evidence base** — anything the judge will cite must come from the role agent, not the Lead. Otherwise the judge scores Lead-authored content, which is a calibration leak.
- **Disclosure** — every Wave-2.5 fix-sweep MUST be logged in `REVIEW-LOG.md` with file paths and line ranges, even if it consists of three typo fixes. RALF iteration counters are NOT incremented (this is pre-judge curation, not a RALF retry).
- **One sweep per design pack** — if the Lead would do a second sweep before the judge, that's a signal the Wave-2 producers under-delivered. Re-spawn the originating producer instead.

## Observability events

Written to `<repo>/.ai-assets-memory/sessions/<sid>/runs.jsonl` by `task-event-log.py` + `subagent-start-budget.py` + `subagent-stop-learnings.py` hooks:

- `workflow_start` — feature-design + idea hash
- `context_load` × 9 — per-agent context slice tokens
- `wave_start` (1, 2, 3)
- `agent_spawned` × N — per agent + model + tokens budget
- `agent_returned` — tokens in/out, duration
- `ralf_iter` — iteration N, oracle result, kill-on check
- `workflow_end` — final status (`SUCCESS` / `RALF_FAILED_BUDGET` / `RALF_FAILED_ITER`)
