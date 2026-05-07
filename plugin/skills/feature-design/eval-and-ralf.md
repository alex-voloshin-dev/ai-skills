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

## Observability events

Written to `<repo>/.ai-assets-memory/sessions/<sid>/runs.jsonl` by `task-event-log.py` + `subagent-start-budget.py` + `subagent-stop-learnings.py` hooks:

- `workflow_start` — feature-design + idea hash
- `context_load` × 9 — per-agent context slice tokens
- `wave_start` (1, 2, 3)
- `agent_spawned` × N — per agent + model + tokens budget
- `agent_returned` — tokens in/out, duration
- `ralf_iter` — iteration N, oracle result, kill-on check
- `workflow_end` — final status (`SUCCESS` / `RALF_FAILED_BUDGET` / `RALF_FAILED_ITER`)
