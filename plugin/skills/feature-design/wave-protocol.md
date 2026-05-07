# Wave Protocol — Path A Pipeline (feature-design)

The wave-by-wave Path A pipeline ASCII tree for `/feature-design`. Loaded from `SKILL.md` when actually executing the Path A fallback (Path B Step 1 returned a technical error like "Agent Teams not enabled"). Path B's task-list dependency graph is the canonical execution; this is the sequential `Agent({...})` flow used as fallback.

## Pipeline (Path A — Subagents fallback)

```
┌─ Context load: /context-load --for <role> for each Wave-1/2 agent
│  (shrinks per-agent input vs full project dump)
│
├─ WAVE 1 (parallel, independent drafts; 50K tokens each):
│  ├─ product-manager          → PRD.md
│  ├─ marketing-strategist     → MARKET-ANALYSIS.md (skip if not public-facing)
│  └─ system-architect         → ARCHITECTURE.md
│
├─ Gate: all wave-1 files exist & parseable (lead checks)
│
├─ WAVE 2 (parallel, domain reviews; reads wave-1 outputs):
│  ├─ ui-ux-designer (reads ARCHITECTURE + PRD)     → UX-FLOW.md + wireframes
│  ├─ db-engineer (reads ARCHITECTURE + PRD)        → DATA-MODEL.md
│  ├─ security-engineer (reads all wave-1)          → security section in RISKS.md
│  └─ qa-engineer (reads PRD + ARCHITECTURE)        → acceptance criteria review
│
├─ Gate: all wave-2 files exist & complete (lead checks)
│
├─ WAVE 3 (sequential, cross-check + eval):
│  ├─ product-manager-reviewer (fresh subagent, reads all w1+w2)  → feedback.md
│  ├─ system-architect (reviewer role, reads all)                 → architecture-review.md
│  └─ eval-judge (scores against feature-design.md rubric)        → REVIEW-LOG.md
│
├─ Gate: rubric score ≥ 4.0 AND all dimensions ≥ 3 → proceed; else → RALF
│
├─ RALF (if rubric not met):
│  │  Oracle: judge:feature-design.md (min_score 4.0)
│  │  Kill-on: regex:RUBRIC_FAILED_3X (three consecutive failures, same issue)
│  │  Caps: 5 iter / 250K tokens / 60 min (overridable in userConfig)
│  │  On failure: re-prompt Wave 2 agents with reviewer feedback
│  └─ (loop back to WAVE 3)
│
└─ Lead writes IMPLEMENTATION-PLAN.md (maps PRD requirements → work packages → engineer roles)
   Memory write: L4 designs/<feature-id>.md (summary + decisions)
   Final report: TodoList check + token totals + handoff hint to `/develop`
```
