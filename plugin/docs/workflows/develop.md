# /develop — Multi-agent feature implementation pipeline

Implement a feature from a design pack or PRD using a coordinated DEVELOP → REVIEW → QA pipeline.

## When to use

- You have an `IMPLEMENTATION-PLAN.md` (from `/feature-design`) ready to execute
- You have a PRD and need engineering execution across multiple stacks
- The `Agent` primitive is available in your harness

## Not for

- Refactors without behavior change → use [`/refactor`](refactor.md)
- Bug fixes → use [`/bugfix`](bugfix.md)
- Single-agent fallback when `Agent` primitive is unavailable → use `/feature-dev`

## How to invoke

```bash
/develop <PRD-path>
/develop docs/features/save-posts-later/IMPLEMENTATION-PLAN.md
/develop "Implement the save-posts-later feature per docs/features/save-posts-later/"
```

## What you get

- Implementation across all work packages in the plan
- Unit tests written by Developer agents
- Higher-level tests added by QA agent
- `REVIEW-LOG.md` consumed by `/create-pr` for the PR description
- Clean commits per work package (per `git-conventions` rule)

## The pipeline

Every work package passes through three stages **in this exact order, no skipping**:

```
DEVELOP → REVIEW → QA
```

- **Developer** (per affected stack — `frontend-engineer`, `python-engineer`, etc.): implements + writes unit tests
- **Reviewer** (`software-engineer` with `code-review` skill): independently verifies changes on disk; catches "ghost changes" pattern
- **QA** (`qa-engineer`): smoke + integration + E2E + SRE-smoke (per Round 6 P20)

The Lead (resolves to `feature-design-lead` orchestrator) enforces gates structurally — no agent advances without the prior stage's explicit approval.

## Multi-stack handling

For features spanning multiple stacks, the Lead spawns one Developer per stack (per `team-protocols/role-selection-table.md`). They take **strict turns** editing — never in parallel — per `subagent-isolation.md` Sequential Code-Modification Gate.

Document-production stages (analysis, design, audit) MAY parallelize. Code-modifying stages are sequential per file. Period.

## RALF on test failures

If the test suite fails after a Developer change, RALF kicks in (8 iter / 640K tokens / 90 min cap). Oracle: `cli:./run-tests.sh`. Kill-on: `oracle-pass`. The Developer iterates with state delta only (continuation prompts) until tests pass or the cap hits.

## Cost expectations

- **Tokens**: 200K–700K typical, depends on plan size + RALF iterations
- **Time**: 15–90 min depending on scope
- **Models**: Opus orchestrator; Sonnet for Developers + Reviewer + QA; Haiku for hooks

## Common questions

**What's the difference between `/develop` and `/feature-dev`?**
`/develop` is the multi-agent pipeline. `/feature-dev` is the single-agent fallback when `Agent` primitive is unavailable. Use `/develop` whenever possible — pipeline + isolated review is the safety net.

**Can I run `/develop` without a design pack?**
Yes — pass a PRD or even a free-form description. The Lead will create an implicit plan first. But quality is much better with a structured `IMPLEMENTATION-PLAN.md` from `/feature-design`.

**What if a work package needs to deviate from the plan?**
The Developer escalates to the Lead. The Lead pauses the pipeline, presents the deviation to you, and waits for approval before resuming. Plan adherence is mandatory; deviations require explicit approval per work package.

**What if the `Agent` primitive isn't available?**
The skill detects at activation time. If unavailable, it halts and recommends `/feature-dev` (single-agent fallback). Inline execution is NOT a fallback — it would break the gate enforcement that this workflow relies on.

**Where does REVIEW-LOG.md live?**
Written to `<repo>/REVIEW-LOG.md` for `/create-pr` to ingest. Also archived to `.ai-skills-memory/develop/<run-id>/` for history.

## Examples

### Single-stack feature
```bash
/develop docs/features/api-rate-limit/IMPLEMENTATION-PLAN.md
```
Lead spawns one Developer (e.g., `python-engineer` for FastAPI). Pipeline runs serially per work package.

### Multi-stack feature (frontend + backend + infra)
```bash
/develop docs/features/realtime-cursors/IMPLEMENTATION-PLAN.md
```
Lead spawns 3 Developers (`frontend-engineer`, `python-engineer`, `devops-engineer`). They take turns editing files (never parallel writes). Reviewer + QA run after each work package.

### Resume after interruption
```bash
/develop --resume <run-id>
```
Picks up from the last completed work package. Useful after a session timeout or rate limit.

## Related

- [`/feature-design`](feature-design.md) — produces the IMPLEMENTATION-PLAN.md this workflow consumes
- [`/bugfix`](bugfix.md) — sibling pipeline for fixes
- [`/run-tests`](feature-design.md) — sub-workflow called by `/develop` for test execution
- [`/create-pr`](feature-design.md) — consumes REVIEW-LOG.md
- [Memory](../concepts/memory.md) — work-package logs go to L4
- [RALF](../concepts/ralf.md) — test-failure iteration loop
