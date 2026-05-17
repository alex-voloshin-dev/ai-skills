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

## Subagent type selection (Path A)

Always prefer the specialised `ai-skills:<role>` subagent_type — the role agent's frontmatter `description`, `model`, `effort`, and body system-prompt carry domain knowledge (GEO structure for `marketing-strategist`, OWASP framing for `security-engineer`, WCAG checklist for `ui-ux-designer`, etc.) that the Lead would otherwise have to inline manually.

`subagent_type: "general-purpose"` is a last-resort fallback when the specialised role definition is unavailable in the current plugin installation (alpha runtime missing the subagent registry, plugin not loaded, role removed in a future plugin version). When it IS used:

- The Lead MUST inline the role's domain knowledge in the spawn prompt — copy the relevant Hard Rules + reference-skill pointers from `plugin/agents/<role>.md` into the prompt body.
- The Lead MUST log `subagent-type: general-purpose (fallback for <intended-role>)` in `REVIEW-LOG.md` so the design pack provenance is auditable.
- This is a degraded-mode signal — surface it in the final report and recommend that the next run use the specialised role once the runtime issue is resolved.

`general-purpose` is NEVER an appropriate choice when the specialised role is available — even if the role's body is short, the framing in `description` (which is what the model selector keys off) is load-bearing.
