# Workflow Specifications — Phase 1

> **Purpose:** Detailed per-workflow specifications for all 10 long-form workflows + 9 companion skills.
> **Date:** 2026-04-26
> **Scope:** Extends plan Section 4; specifications per template below

---

## Part A: Per-Workflow Specifications (10 workflows)

All workflows follow the common scaffold in plan §4.6. Each spec below details the variant-specific aspects.

---

## /feature-design

### Purpose
Converts a 1–3 sentence feature idea into a complete design pack (PRD, architecture, UX, data model, risks, implementation plan). Use when starting a new feature. Not appropriate for: internal refactors, hotfixes, or existing feature refinement (use `/develop` if you already have a PRD).

### Invocation
```
/feature-design "<idea>"
/feature-design "live collaborative cursors in markdown editor"
/feature-design "subscription tier with usage metering"
```

### Input schema
- `<idea>` (required): 1–3 sentences describing the feature from user/customer perspective. No design assumptions. Examples: "Users can see where others are typing in real-time", "We need to limit API calls per month for non-paying users".

### Output schema

**Convention exception (Round 4 N6):** `/feature-design` writes its design pack to `<repo>/docs/features/<feature-id>/` — INSIDE the target repo's `docs/` directory, NOT inside `.ai-assets-memory/`. Reason: design packs are intended to be VERSIONED IN GIT as project documentation, reviewed by the team, and live across many sprints. They are NOT ephemeral run logs (which DO live in `.ai-assets-memory/`). The same exception applies to `/docs-pack` outputs (also user-facing docs intended for git). All other workflows write outputs to `.ai-assets-memory/<workflow>/<run-id>/` because those outputs are ephemeral artifacts of one workflow execution.

Files written to `<repo>/docs/features/<feature-id>/` (feature-id auto-generated from first 3 words of idea):
- `PRD.md` — product vision, success metrics, acceptance criteria
- `MARKET-ANALYSIS.md` — competitive snapshot, GTM angle (optional if not public-facing)
- `ARCHITECTURE.md` — system design, component diagram, dependency list
- `UX-FLOW.md` — user journeys, interaction flows, accessibility notes
- `DATA-MODEL.md` — schema, migrations, data flow (if relevant)
- `IMPLEMENTATION-PLAN.md` — work packages per stack, engineer role assignments, estimated effort
- `RISKS.md` — identified risks, mitigation strategies, rollback plan
- `REVIEW-LOG.md` — auto-generated trace showing all review cycles and score deltas

### Agent roster

| Agent | Model | Effort | Tools | Role |
|---|---|---|---|---|
| feature-design-lead | Opus | high | Task | Orchestrates waves; enforces gates; writes final IMPLEMENTATION-PLAN |
| product-manager | Sonnet | medium | Read, Grep, Glob | Writes PRD from idea + context slice |
| marketing-strategist | Sonnet | medium | Read, Grep, Glob | Writes MARKET-ANALYSIS (if public); GTM angle |
| system-architect | Sonnet | high | Read, Grep, Glob | Writes ARCHITECTURE + skeleton design |
| ui-ux-designer | Sonnet | medium | Read, Grep, Glob | Writes UX-FLOW + wireframes + accessibility |
| db-engineer | Sonnet | medium | Read, Grep, Glob | Writes DATA-MODEL if schema change needed |
| security-engineer | Sonnet | medium | Read, Grep, Glob | Wave 2 security review; contributes to RISKS |
| qa-engineer | Sonnet | low | Read, Grep, Glob | Wave 2 acceptance criteria review |
| product-manager (reviewer) | Sonnet | low | Read, Grep, Glob | Wave 3 fresh eyes cross-check |
| eval-judge | Haiku | low | Read, Grep, Glob | Scores against feature-design rubric |

### Pipeline

```
┌─ Context load: /context-load --for <role> × 9 agents
│
├─ WAVE 1 (parallel, independent drafts, 50K tokens each):
│  ├─ product-manager → PRD.md
│  ├─ marketing-strategist → MARKET-ANALYSIS.md
│  └─ system-architect → ARCHITECTURE.md
│
├─ Gate: all wave-1 files exist & parseable (lead checks)
│
├─ WAVE 2 (parallel, domain reviews):
│  ├─ ui-ux-designer (reads wave-1 ARCHITECTURE + PRD) → UX-FLOW.md + wireframes
│  ├─ db-engineer (reads wave-1 ARCHITECTURE + PRD) → DATA-MODEL.md
│  ├─ security-engineer (reads all wave-1) → security section for RISKS.md
│  └─ qa-engineer (reads PRD + ARCHITECTURE) → acceptance criteria review
│
├─ Gate: all wave-2 files exist & complete (lead checks)
│
├─ WAVE 3 (sequential, cross-check + eval):
│  ├─ product-manager-reviewer (fresh subagent, reads all wave-1 + wave-2) → feedback.md
│  ├─ system-architect (original, reviewer role, reads all) → architecture-review.md
│  └─ eval-judge (reads all artefacts against feature-design.md rubric) → REVIEW-LOG.md
│
├─ Gate: rubric score ≥ 4.0 AND all dimensions ≥ 3 (proceed) OR < 4.0 (RALF)
│
├─ RALF (if needed):
│  │  Oracle: judge:feature-design.md (min_score 4.0)
│  │  Kill-on: regex:RUBRIC_FAILED_3X or iter=5 or tokens=250K
│  │  On failure: re-prompt Wave 2 agents with reviewer feedback
│  └─ (loop back to WAVE 3)
│
└─ Lead writes IMPLEMENTATION-PLAN.md (maps PRD requirements → work packages → engineer roles)
   Memory write: L4 `.ai-assets-memory/designs/<feature-id>.md` (summary + decisions)
   Report: /plugin-doctor format (TodoList check + token totals)
```

### Eval rubric
Pointer: `plugin/eval/judge-rubrics/feature-design.md` (Phase 2).

Dimensions (6 × 5 levels):
1. **Completeness** — all required artefacts present with depth
2. **Internal consistency** — no cross-doc contradictions, coherent vision
3. **Traceability** — requirements map to components map to test cases
4. **Handoff clarity** — engineer can begin work without back-and-forth
5. **Risk coverage** — identified, scored, mitigations specified
6. **GEO/marketing readiness** (if public-facing) — passes geo-audit + humanizer standards

Pass: avg ≥ 4.0, no dimension < 3.

### RALF wiring
- **Oracle:** `judge:feature-design.md` (min_score 4.0)
- **Kill-on:** `regex:RUBRIC_FAILED_3X` (three consecutive failing scores with same issue)
- **Caps:** 5 iter / 250K tokens / 60 min (overridable in userConfig)

### Memory writes

| Layer | When | Shape |
|---|---|---|
| L4 | After wave-1 complete | `.ai-assets-memory/designs/<feature-id>/wave1-summary.md` — high-level decisions per agent |
| L4 | After RALF complete | `.ai-assets-memory/designs/<feature-id>/final.md` — trace of all rubric scores + converged design |
| L4 (committed, opt-in) | Before handoff | `.ai-assets-memory/.committed/designs/<feature-id>.md` — finalized design snapshot for team review |

### Failure modes
- **Subagent (Wave 1–2) timeout:** Lead retries once with explicit error context. If persistent, escalates to user with instructions to narrow scope.
- **Rubric score oscillates:** RALF detects same-issue-3X pattern, kills loop, writes diagnostic suggesting design ambiguity; escalates to user.
- **Oracle error (judge crashes):** Treat as unknown state; kill loop and surface full diagnostic from eval-judge stderr.
- **Budget hit mid-RALF:** Hard pause; prompt user to confirm continuation or abort (raises per-workflow RALF cap in userConfig).

### Observability events
Events written to `.ai-assets-memory/runs/<run-id>.jsonl`:
- `workflow_start` — feature-design with idea hash
- `context_load` × 9 — per-agent context slice loaded (tokens)
- `wave_start` (1, 2, 3)
- `agent_spawned` × N — per agent, model, tokens budget
- `agent_returned` — tokens in/out, duration
- `ralf_iter` — iteration N, oracle result, kill-on check result
- `workflow_end` — final status (SUCCESS / RALF_FAILED_BUDGET / RALF_FAILED_ITER)

---

## /develop

### Purpose
Full implementation of a feature from design pack or PRD. Takes an IMPLEMENTATION-PLAN (from `/feature-design` or user-written PRD) and produces working code, tests, and PR. Use for: new feature coding, multi-engineer coordination. Not for: refactors without behavior change (use `/refactor`), hotfixes (use `/bugfix`).

### Invocation
```
/develop docs/features/live-cursors/IMPLEMENTATION-PLAN.md
/develop ./PRD.md --team "frontend:2 backend:1"
```

### Input schema
- `<plan-path>` (required): path to IMPLEMENTATION-PLAN.md (from `/feature-design`) or a standalone PRD.md.
- `--team` (optional): override auto-detected role assignments. Format: `role:count role:count` (e.g., `"frontend:2 backend:1"`). If omitted, auto-detect from IMPLEMENTATION-PLAN work packages.

### Output schema
- Working code committed to branch (per role-selection-table.md)
- `<repo>/.ai-assets-memory/develop/<run-id>/REVIEW-LOG.md` — review trace
- `.ai-assets-memory/develop/<run-id>/PR-description.md` — auto-built from IMPLEMENTATION-PLAN + diff summary + run stats
- Pull request opened with auto-generated description and suggested reviewers
- Tests passing (unit + integration + smoke where applicable)

### Agent roster

| Agent | Model | Effort | Tools | Role |
|---|---|---|---|---|
| team-lead (or feature-design-lead in delegated mode) | Opus | high | Task | Spawns developers per role-selection-table; manages gates |
| developer (role-specific) | Sonnet | high | Read, Write, Edit, Bash | Code modification per work package |
| reviewer | Sonnet | medium | Read, Grep, Glob | Code review against requirements |
| qa-engineer | Sonnet | medium | Bash, Read, Glob | Test execution + SRE smoke (if env detected) |
| eval-judge | Haiku | low | Read, Grep, Glob | Grades final code against rubric (optional, if strict org) |

### Pipeline

```
┌─ Context load: /context-load --for developer
│
├─ DEVELOP (parallel per work package):
│  └─ developer × N (one per work package) → code edits per assigned component
│     Sequential per file (no race conditions)
│     Commits as they go (one commit per work package or logical unit)
│
├─ Gate: all code changes complete (lead checks git status)
│
├─ REVIEW (sequential):
│  └─ reviewer (reads diff, IMPLEMENTATION-PLAN, tests) → feedback.md or APPROVED
│     If feedback: developer re-reads, rebases, re-submits
│
├─ Gate: reviewer approval (or lead override with recorded reason)
│
├─ QA (sequential):
│  ├─ qa-engineer: run test suite (unit + integration)
│  └─ [if docker-compose detected] run SRE smoke tests (analyze-local pattern)
│
├─ Gate: all tests pass
│
├─ RALF (test loop only, if QA fails):
│  │  Oracle: cli:./run-tests.sh (exit 0 = pass)
│  │  Kill-on: same-error-repeats:3
│  │  Re-prompt: assigned developer for the failing test component
│  └─ (loop back to QA)
│
└─ Lead writes PR description (from IMPLEMENTATION-PLAN + diff summary + run stats)
   Opens PR on origin (or pushes to staging branch per team-protocols)
   Memory write: L4 feature tracking
   Report: /plugin-doctor format
```

### Eval rubric
Pointer: `plugin/eval/judge-rubrics/develop.md` (Phase 2).

Dimensions:
1. **Correctness** — code runs, tests pass, acceptance criteria met
2. **Code quality** — readability, no obvious bugs, follows style guide
3. **Test coverage** — unit + integration tests cover happy path + error cases
4. **Documentation** — code comments, docstrings, updated README/API docs
5. **Performance** — no regressions; meets latency/throughput requirements if specified

Pass: avg ≥ 4.0, no dimension < 3.

### RALF wiring
- **Oracle:** `cli:./run-tests.sh` (exit 0 = pass)
- **Kill-on:** `same-error-repeats:3`
- **Caps:** 8 iter / 640K tokens / 90 min

### Memory writes

| Layer | When | Shape |
|---|---|---|
| L4 | After DEVELOP complete | `.ai-assets-memory/develop/<run-id>/developer-notes.md` — per-developer summary |
| L4 | After QA pass | `.ai-assets-memory/develop/<run-id>/final.md` — design-to-code trace |
| L4 (committed) | On PR open | `.ai-assets-memory/.committed/releases/<version>/changes.md` — what changed, why |

### Failure modes
- **Developer stalls on work package:** Lead checks git log, retries with explicit error context. Escalates if persistent.
- **Reviewer feedback loops >3 times:** Lead escalates; may suggest pairing (not supported in v0.1, defer to human team).
- **QA test suite intermittent:** Runs 2× before declaring fail. If still fails, escalates with full logs.
- **RALF loop hits same error 3× but error is infrastructure (Docker out of space):** Kill loop; surface error as infrastructure issue, not code issue.

### Observability events
- `workflow_start` — develop with plan-path
- `context_load` — developer context
- `agent_spawned` × N (developers)
- `agent_returned` × N
- `ralf_iter` — test loop iteration details
- `workflow_end` — PR opened or FAILED

---

## /bugfix

### Purpose
Triage environment vs. code issue; diagnose root cause; fix; ship. Use for: production bugs, unexpected behavior, failing tests. Not for: refactors (use `/refactor`), known limitations (use `/spike` to explore), feature requests (use `/feature-design`).

### Invocation
```
/bugfix "Users report 500 errors on login"
/bugfix "CI flakes on test suite intermittently"
/bugfix --reproduction-test ./test-login-error.sh
```

### Input schema
- `<description>` (required): bug report (symptoms, impact, frequency).
- `--reproduction-test` (optional): path to a test that reproduces the bug (exit 0 = bug visible, exit non-0 = bug fixed). If omitted, qa-engineer auto-creates one.

### Output schema
- Root cause documented in `.ai-assets-memory/bugfix/<run-id>/diagnosis.md`
- Code fix (if code) or configuration change (if infra)
- Reproduction test now passing
- Pull request with fix and test
- Incident summary in L4 memory (for pattern-matching future bugs)

### Agent roster

| Agent | Model | Effort | Tools | Role |
|---|---|---|---|---|
| team-lead | Opus | medium | Task | Decides code vs. infra; assigns investigators; approves fix |
| env-analyzer | Sonnet | medium | Read, Bash, Grep | Investigates environment (Docker, K8s, CI) |
| developer (2×, parallel) | Sonnet | high | Read, Bash, Grep, Write, Edit | Independent triangulation of root cause |
| developer (assigned fix) | Sonnet | high | Read, Write, Edit, Bash | Writes fix based on converged diagnosis |
| qa-engineer | Sonnet | low | Bash, Read | Verifies reproduction test + fix test |

### Pipeline

```
┌─ Context load
│
├─ TRIAGE:
│  └─ env-analyzer (reads error description, stack traces) → ENV-REPORT.md or CODE-ISSUE
│     If env issue (disk full, env var missing, service down):
│     │  RALF loop: oracle=auto-fix-and-test, kill-on=oracle-pass OR no-progress:2
│     │  (auto-fix only for safe class: restart, clear cache, regenerate config)
│     │  If fixed: DONE (escalate to ops if needed)
│     │  If not fixed: escalate to user as infra issue
│     └─ Else: CODE issue, proceed to DIAGNOSE
│
├─ DIAGNOSE (parallel, 2 developers):
│  ├─ developer-1 (reads error, code) → diagnosis-1.md
│  └─ developer-2 (reads error, code, different angle) → diagnosis-2.md
│
├─ Lead review: convergence check (do diagnoses agree?)
│  └─ If divergent: request one more investigation, take intersection
│
├─ FIX (single developer, chosen from diagnosed issue):
│  └─ developer → code fix + test
│
├─ QA (per /develop pipeline):
│  ├─ run reproduction test (must fail before fix, pass after)
│  └─ run full test suite
│
├─ RALF (test loop, same as /develop):
│  │  Oracle: cli:./run-tests.sh
│  │  Kill-on: same-error-repeats:3
│  └─ (loop back to QA)
│
└─ PR + memory write (incident summary for L4)
```

### Eval rubric
Pointer: `plugin/eval/judge-rubrics/bugfix.md` (Phase 2).

Dimensions:
1. **Root cause correctness** — identified the actual bug, not a symptom
2. **Fix completeness** — all instances of bug fixed, not just the reported one
3. **No regression** — existing tests pass; new test prevents re-occurrence
4. **Minimal scope** — fix touches minimal code; no unnecessary refactoring
5. **Explanation clarity** — root cause and fix rationale clear to team

Pass: avg ≥ 4.0, no dimension < 3.

### RALF wiring
- **Oracle:** `cli:<reproduction-test>` (exit 0 = pass) or auto-generated reproduction test
- **Kill-on:** `same-error-repeats:3` OR `no-progress:2` (if fix stalls)
- **Caps:** 6 iter / 300K tokens / 60 min

### Memory writes

| Layer | When | Shape |
|---|---|---|
| L4 | After diagnosis | `.ai-assets-memory/bugfix/<run-id>/diagnosis.md` — root cause analysis |
| L4 (committed, opt-in) | After fix ships | `.ai-assets-memory/.committed/incidents/<date>-<summary>.md` — incident post-mortem for pattern matching |

### Failure modes
- **Env vs. code ambiguous:** Lead escalates to user; asks for more info or environmental logs.
- **Diagnosis diverges too much:** Lead accepts developer-1's diagnosis (first to achieve confidence), proceeds.
- **Auto-fix fails (e.g., cache clear doesn't help):** env-analyzer escalates as infrastructure issue.
- **Reproduction test itself broken:** qa-engineer re-writes test, re-runs QA loop.

### Observability events
- `workflow_start` — bugfix with description hash
- `triage_complete` — code vs. infra determination
- `agent_spawned` × N (developers)
- `ralf_iter` — test loop
- `workflow_end` — PR opened or ESCALATED_TO_USER

---

## /env-analyze

### Purpose
Standalone diagnostic for environment state (local Docker compose, K8s, CI runner, resource usage, network, logs). Use when: troubleshooting deployment, debugging CI flakes, validating environment before deployment. Not for: code bugs (use `/bugfix`), application-level diagnostics (use `/spike`).

### Invocation
```
/env-analyze
/env-analyze --scope local
/env-analyze --scope docker --auto-fix
```

### Input schema
- `--scope` (optional): `local` (default, detects Docker/K8s), `docker`, `kubernetes`, `ci`. If omitted, auto-detect.
- `--auto-fix` (optional): apply ONLY container-level safe fixes — restart stuck containers, clear container-scoped caches, regenerate config from existing template. Default false. **Explicitly NOT in scope:** restarting Docker daemon, regenerating TLS certs, modifying host-level state, deleting data, changing secrets, k8s namespace operations. Anything outside container-level → manual escalation only.

### Output schema
- `.ai-assets-memory/env-reports/<run-id>/ENV-REPORT.md` — diagnostic summary with tables:
  - Container/pod status (name, state, restarts, uptime)
  - Log excerpts (last 20 lines per service, error filter)
  - Network sanity (connectivity, DNS, port availability)
  - Resource saturation (CPU, memory, disk % used)
  - Identified anomalies (list with severity)
  - Recommended actions (prioritized)
- If `--auto-fix`: list of actions taken + success/failure per action

### Agent roster

| Agent | Model | Effort | Tools | Role |
|---|---|---|---|---|
| sre-engineer | Sonnet | medium | Bash, Read, Grep | Docker/K8s diagnostics, log analysis |
| devops-engineer | Sonnet | medium | Bash, Read, Grep | CI/CD environment diagnostics |

### Pipeline

```
┌─ Scope detection: check for docker-compose.yml, k8s config, CI runner
│
├─ SRE + DevOps in parallel:
│  ├─ sre-engineer: docker inspect, docker logs, docker stats
│  │  (or kubectl get pods/nodes, kubectl logs for K8s)
│  │  → SRE-REPORT.md (containers, logs, resource usage)
│  │
│  └─ devops-engineer: CI runner health (GitHub Actions, GitLab CI, etc.)
│     → DEVOPS-REPORT.md (CI job queue, runner status, cache age)
│
├─ Lead consolidates → ENV-REPORT.md (merged view)
│
├─ If --auto-fix:
│  │  Safe actions ONLY (container-level):
│  │    ✓ restart stuck container, clear container cache, regen config from existing template
│  │  Out of scope (require manual escalation):
│  │    ✗ Docker daemon restart, TLS cert regeneration, host-level changes
│  │    ✗ data deletion, secret changes, k8s namespace ops, production value mutation
│  │  For each action: run oracle (health check post-fix)
│  └─ Report action outcomes; flag any out-of-scope items as "manual: <reason>"
│
└─ Memory write: L4 (environment baseline snapshot for comparison)
```

### Eval rubric
Pointer: `plugin/eval/judge-rubrics/env-analyze.md` (Phase 2).

Dimensions:
1. **Completeness** — all scopes checked (if applicable)
2. **Accuracy** — reports match actual state
3. **Clarity** — anomalies clearly flagged with severity
4. **Actionability** — recommendations are specific and executable
5. **Safety** — no destructive actions without explicit user approval

Pass: avg ≥ 4.0, no dimension < 3.

### RALF wiring
- **No RALF** — diagnostic is pass-once. If auto-fix enabled, each action has its own oracle (health check post-action).

### Memory writes

| Layer | When | Shape |
|---|---|---|
| L4 | After analysis | `.ai-assets-memory/env-reports/<run-id>/baseline.json` — container states, resource usage, timestamps (for drift detection) |

### Failure modes
- **Docker not installed:** Graceful skip; report N/A for that scope.
- **K8s connection refused:** Report as connection error; offer manual debugging guidance.
- **Auto-fix action fails:** Rollback if possible; report outcome and manual steps.
- **Log parsing error (corrupted logs):** Skip that log, report as anomaly (log corruption suspected).

### Observability events
- `workflow_start` — env-analyze with scope
- `agent_spawned` × 2 (sre, devops)
- `auto_fix_action` (per action if enabled)
- `workflow_end` — COMPLETE with anomaly count

---

## /refactor

### Purpose
Plan and execute a code refactor (change structure without changing behavior). Use for: breaking up large functions, migrating to new patterns, extracting to library, improving testability. Not for: adding features (use `/develop`), fixing bugs (use `/bugfix`).

### Invocation
```
/refactor --files "src/api/*.ts" --goal "extract auth middleware to shared lib"
/refactor --scope "convert class-based to functional components"
```

### Input schema
- `--files` (optional): glob pattern or list of files to refactor. If omitted, ask user.
- `--goal` (required): plain-English goal of refactor (e.g., "reduce cyclomatic complexity", "extract to library", "migrate to new API").
- `--preserve-tests` (optional, default true): keep existing tests passing throughout.

### Output schema
- Refactored code in assigned files
- Test suite passing (tests updated if signatures change)
- `.ai-assets-memory/refactor/<run-id>/REFACTOR-LOG.md` — before/after comparison, rationale
- Pull request with diff + refactor log

### Agent roster

| Agent | Model | Effort | Tools | Role |
|---|---|---|---|---|
| team-lead | Opus | medium | Task | Plans refactor steps; assigns per file; verifies no behavior change |
| developer | Sonnet | high | Read, Write, Edit, Bash | Executes refactor per assigned file(s) |
| qa-engineer | Sonnet | low | Bash, Read | Verifies behavior equivalence (all tests pass) |

### Pipeline

```
┌─ PLAN:
│  └─ Lead: read target files, scope refactor, break into per-file steps
│     Generate REFACTOR-PLAN.md with before/after sketches
│
├─ Gate: user approval of plan
│
├─ EXECUTE (sequential per file):
│  └─ developer: refactor assigned file(s)
│     After each file: run tests
│     If tests fail: diagnose, refactor until tests pass
│
├─ Gate: all files refactored, all tests passing
│
├─ RALF (test validation loop):
│  │  Oracle: cli:./run-tests.sh
│  │  Kill-on: same-error-repeats:2
│  │  On fail: developer fixes refactor to pass test
│  └─ (loop back to test run)
│
└─ Lead: verify no behavior change (e.g., API diff check)
   Memory write: L4 refactor decision + rationale
   PR description: generated from REFACTOR-PLAN
```

### Eval rubric
Pointer: `plugin/eval/judge-rubrics/refactor.md` (Phase 2).

Dimensions:
1. **Behavior equivalence** — all existing tests pass; no breaking changes
2. **Code improvement** — readability, maintainability, or performance improved
3. **Scope correctness** — refactor stays within stated goal; no unrelated changes
4. **Test coverage preserved** — test suite still exercises the code
5. **Documentation updated** — docstrings, comments, README reflect changes

Pass: avg ≥ 4.0, no dimension < 3.

### RALF wiring
- **Oracle:** `cli:./run-tests.sh` (exit 0 = pass)
- **Kill-on:** `same-error-repeats:2`
- **Caps:** 4 iter / 200K tokens / 45 min

### Memory writes

| Layer | When | Shape |
|---|---|---|
| L4 | After plan approval | `.ai-assets-memory/refactor/<run-id>/plan.md` |
| L4 | After completion | `.ai-assets-memory/refactor/<run-id>/final.md` — before/after stats (lines, complexity metrics) |

### Failure modes
- **Refactor scope creeps:** Lead stops work; user must clarify goal.
- **Tests fail after refactor:** Developer re-examines refactor; may indicate behavior change. Escalate if unclear.

### Observability events
- `workflow_start` — refactor with goal
- `plan_generated` — per-file plan
- `ralf_iter` — test validation
- `workflow_end` — PR opened or ESCALATED

---

## /migrate

### Purpose
Planned migration (schema, library, version, framework). Use for: database schema migrations with rollback plan, framework version upgrades, library replacements. Not for: refactors without external contract change (use `/refactor`), small bug-fix releases (use `/develop`).

### Invocation
```
/migrate "Postgres 13 → 14"
/migrate "React class → functional components" --staged
```

### Input schema
- `<migration>` (required): description (source → target, e.g., "Django 3.2 → 4.0").
- `--staged` (optional): use blue-green or canary pattern (requires ops sign-off).

### Output schema
- Migration code (schema scripts, version pins, compatibility shims)
- `.ai-assets-memory/migrate/<run-id>/MIGRATION-PLAN.md` — detailed steps, rollback procedure, risk assessment
- `.ai-assets-memory/migrate/<run-id>/VALIDATION.md` — test results, data integrity checks
- PR with migration + rollback procedures documented

### Agent roster

| Agent | Model | Effort | Tools | Role |
|---|---|---|---|---|
| team-lead | Opus | high | Task | Plans migration, risk assessment, rollback strategy |
| devops-engineer | Sonnet | high | Bash, Read, Write | Infrastructure migration (DB schema, deploy config) |
| developer | Sonnet | high | Read, Write, Edit, Bash | Application-level migration (code changes, compatibility shims) |
| qa-engineer | Sonnet | high | Bash, Read, Grep | Data integrity validation, rollback testing |

### Pipeline

```
┌─ PLAN:
│  └─ Lead: research target version, compatibility matrix, rollback strategy
│     Generate MIGRATION-PLAN.md with:
│     - Pre-flight checklist (dependencies, backups)
│     - Step-by-step migration procedure
│     - Rollback procedure
│     - Risk matrix (data loss, compatibility, performance)
│
├─ Gate: user approval of rollback procedure
│
├─ EXECUTE (sequential):
│  ├─ devops-engineer: DB schema migration (if applicable)
│  │  - Create migration scripts (forward + rollback)
│  │  - Test on replica
│  │  - Document data transformation
│  │
│  └─ developer: application-level changes
│     - Update deps, compatibility shims, feature flags
│     - Parallel-run mode (old + new API, use new)
│
├─ VALIDATE (sequential):
│  │  - Run full test suite
│  │  - Data integrity checks (row counts, checksums, foreign key constraints)
│  │  - Performance baseline (query times, throughput)
│  └─ If rollback needed: execute rollback procedure, validate revert
│
├─ RALF (validation loop):
│  │  Oracle: custom (test suite pass + data integrity pass)
│  │  Kill-on: oracle-pass OR no-progress:2
│  └─ (loop back to VALIDATE)
│
└─ Lead: sign-off on migration safety
   Memory write: L4 migration decision + rollback proof
```

### Eval rubric
Pointer: `plugin/eval/judge-rubrics/migrate.md` (Phase 2).

Dimensions:
1. **Plan completeness** — pre-flight, forward, rollback all documented
2. **Rollback safety** — rollback procedure tested and proven reversible
3. **Data integrity** — validation checks confirm data preserved
4. **Performance** — no unexpected degradation post-migration
5. **Risk awareness** — identified risks and mitigations for each

Pass: avg ≥ 4.0, no dimension < 3.

### RALF wiring
- **Oracle:** `python:./validate-migration.py` (custom validation script, exit 0 = pass)
- **Kill-on:** `oracle-pass` (happy stop) OR `no-progress:2`
- **Caps:** 5 iter / 300K tokens / 90 min

### Memory writes

| Layer | When | Shape |
|---|---|---|
| L4 (committed) | After plan approved | `.ai-assets-memory/.committed/migrations/<name>/plan.md` — strategy for team review |
| L4 (committed) | After validation pass | `.ai-assets-memory/.committed/migrations/<name>/validation-report.md` — data integrity proof |

### Failure modes
- **Rollback procedure fails:** Escalate as critical; do not proceed with migration until rollback is proven safe.
- **Data loss detected post-validation:** Kill migration; trigger full diagnostic (call `/env-analyze`).
- **Performance regresses:** Lead decides if acceptable; documents trade-off decision.

### Observability events
- `workflow_start` — migrate with source→target
- `plan_approved` — user gate passed
- `validation_start` — data integrity checks begin
- `ralf_iter` — validation loops
- `workflow_end` — COMPLETE or ROLLBACK_EXECUTED

---

## /spike

### Purpose
Time-boxed exploration with go/no-go writeup. Use for: evaluating new tech, prototyping approaches, researching unknowns, proof-of-concept. Not for: development (use `/develop`), decisions already made (spike is for exploration, not execution).

### Invocation
```
/spike "Can we use gRPC instead of REST?" --time-cap 120
/spike "Best way to implement real-time sync" --poc
```

### Input schema
- `<question>` (required): research question or evaluation goal.
- `--time-cap` (optional, default 180 min): max wall-time for spike.
- `--poc` (optional): if set, produce a minimal proof-of-concept (code) alongside writeup.

### Output schema
- `.ai-assets-memory/spikes/<run-id>/SPIKE-REPORT.md` — findings, pro/con analysis, recommendation (go/no-go/needs-more-info)
- (optional) Proof-of-concept code in `./spike-poc-<run-id>/` (if `--poc` flag)
- Memory write: L4 research decision for future reference

### Agent roster

| Agent | Model | Effort | Tools | Role |
|---|---|---|---|---|
| subject-matter-expert (role-appropriate) | Sonnet | high | Read, Bash, Grep, (Write, Edit if --poc) | Research + writeup + POC |
| (optional) technical-reviewer | Sonnet | low | Read, Grep | Reviews findings, challenges assumptions |

### Pipeline

```
┌─ Researcher (chosen by Lead based on question domain):
│  - Research question exhaustively
│  - Gather evidence (docs, benchmarks, examples)
│  - Build POC if --poc flag set
│  - Estimate effort if chosen
│  → SPIKE-REPORT.md with go/no-go recommendation
│
├─ (Optional) Reviewer validation:
│  └─ technical-reviewer: stress-test findings, identify gaps
│
└─ Memory write: L4 research decision
   Report: go/no-go + next steps
```

No RALF; one pass with optional review.

### Eval rubric
Pointer: `plugin/eval/judge-rubrics/spike.md` (Phase 2).

Dimensions:
1. **Question clarity** — spike clearly answers the stated question
2. **Evidence quality** — findings backed by data, not opinion
3. **Completeness** — considered trade-offs and alternatives
4. **Feasibility assessment** — if go/no-go, effort estimate is realistic
5. **Actionability** — next steps clear (prototype? deep dive? abandon?)

Pass: avg ≥ 4.0, no dimension < 3.

### RALF wiring
- **No RALF** — diagnostic pass; time-cap enforces deadline.

### Memory writes

| Layer | When | Shape |
|---|---|---|
| L4 | After complete | `.ai-assets-memory/spikes/<run-id>/report.md` — full findings |
| L4 (committed) | **Always ask user explicitly after report**, never auto-write | `.ai-assets-memory/.committed/decisions/<date>-<question>.md` — recorded decision (only if user confirms in chat). Never auto-create — `.committed/` goes to git and the user may want to reword the decision before committing |

### Failure modes
- **Time cap hit mid-research:** Researcher pauses at time-cap; produces partial report with "more investigation needed" note.
- **Findings inconclusive:** Report states inconclusive with specific data gaps; recommend deeper spike or prototype.

### Observability events
- `workflow_start` — spike with question
- `workflow_end` — COMPLETE with go/no-go

---

## /security-audit

### Purpose
Full security scan of the codebase and infrastructure. Use for: pre-release audit, compliance check, threat modeling, vulnerability scan. Not for: code-review security feedback (use `/code-review`), pen testing (use professional service).

### Invocation
```
/security-audit
/security-audit --scope "secrets,deps,auth" --report-type detailed
```

### Input schema
- `--scope` (optional, default "all"): comma-separated areas to audit (secrets, deps, auth, access-control, data-handling, crypto, infra). If omitted, audit all.
- `--report-type` (optional, default "summary"): `summary` or `detailed`.

### Output schema
- `.ai-assets-memory/security-audits/<run-id>/SECURITY-REPORT.md` — findings by category:
  - Secrets scan (hardcoded creds, API keys, etc.) — CRITICAL if found
  - Dependency audit (CVE check, outdated libs) — HIGH severity
  - Auth review (credential handling, session management) — MEDIUM
  - Access control (RBAC, data scoping) — MEDIUM
  - Data handling (PII exposure, encryption, logging) — MEDIUM
  - Cryptography (algorithm choices, key management) — MEDIUM
  - Infrastructure (network policies, TLS, secrets store) — MEDIUM
- `.ai-assets-memory/security-audits/<run-id>/REMEDIATION-PLAN.md` — per finding: severity, mitigation steps, suggested owner role. **No effort estimate** — effort is too context-dependent (team velocity, codebase familiarity, dependency on other teams) for a security agent to predict reliably; user/PM owns sizing
- Pull request with fixes for automatable issues (dependency updates, secrets removal from code)

### Agent roster

| Agent | Model | Effort | Tools | Role |
|---|---|---|---|---|
| security-engineer | Sonnet | high | Read, Grep, Bash, Glob | Main audit; threat modeling |
| devops-engineer | Sonnet | medium | Read, Bash, Grep | Infrastructure security review |
| developer | Sonnet | medium | Read, Bash, Grep | Credential/secret removal; code-level fixes |

### Pipeline

```
┌─ Scope parsing: audit --scope areas
│
├─ Security engineer in parallel with DevOps:
│  ├─ security-engineer:
│  │  - Grep for secrets (hardcoded keys, tokens, passwords)
│  │  - Dependency scan (npm audit, pip check, cargo audit)
│  │  - Auth flow review (login, session, token, CSRF)
│  │  - Access control review (data scoping, RBAC)
│  │  - Cryptography review (algorithms, key rotation, TLS)
│  │  → SECURITY-FINDINGS.md (per scope)
│  │
│  └─ devops-engineer:
│     - Infrastructure review (network policies, secrets store, TLS)
│     - Container scanning (if Docker)
│     - CI/CD security (secret management, artifact verification)
│     → INFRA-FINDINGS.md
│
├─ Lead consolidates → SECURITY-REPORT.md
│
├─ Lead generates REMEDIATION-PLAN.md:
│  └─ Per finding: severity, mitigation steps, suggested owner role
│     (NO effort estimate — user/PM owns sizing)
│
└─ Developer (if applicable): fix automatable issues (update deps, remove secrets from code)
   Memory write: L4 security audit decision + high-severity findings
```

No RALF; audit is pass-once.

### Eval rubric
Pointer: `plugin/eval/judge-rubrics/security-audit.md` (Phase 2). Rubric MUST reference and check coverage against:
- **OWASP Top 10 Web Application Security Risks (2021 / latest)** — for code-level findings (injection, broken auth, sensitive data, XXE, broken access control, security misconfiguration, XSS, insecure deserialization, vulnerable components, insufficient logging)
- **OWASP GenAI / LLM Top 10 (2025)** — for any AI/LLM-related component in the audit target (LLM01–LLM10), in particular LLM01 prompt injection, LLM02 sensitive info disclosure, LLM06 excessive agency, LLM07 system prompt leakage, LLM08 vector/embedding weaknesses, LLM10 unbounded consumption (**G3**)

Dimensions:
1. **Completeness** — all requested scopes covered
2. **OWASP coverage** — categories from OWASP Web Top 10 + GenAI Top 10 systematically addressed where applicable
3. **Accuracy** — findings are real issues, not false positives
3. **Clarity** — each finding explains the risk and impact
4. **Prioritization** — severity correctly assessed (CRITICAL > HIGH > MEDIUM > LOW)
5. **Remediation guidance** — mitigations are specific and testable

Pass: avg ≥ 4.0, no dimension < 3.

### RALF wiring
- **No RALF** — audit is diagnostic; each finding is captured as-is.

### Memory writes

| Layer | When | Shape |
|---|---|---|
| L4 | After audit complete | `.ai-assets-memory/security-audits/<run-id>/findings.json` — structured findings (for trend tracking) |
| L4 (committed) | If CRITICAL found | `.ai-assets-memory/.committed/security/incidents/<date>.md` — critical finding + immediate action taken |

### Failure modes
- **False positive (e.g., secret string in comment, not actual key):** Security engineer reviews, confirms, removes from report if benign.
- **Dependency CVE has no fix available:** Documented in REMEDIATION-PLAN with risk acceptance note and deadline for escalation.
- **Auth flow too complex to audit in one pass:** Security engineer flags as needs-deeper-review; recommends threat-modeling session (separate spike).

### Observability events
- `workflow_start` — security-audit with scope
- `finding_identified` (per finding, severity)
- `workflow_end` — COMPLETE with critical/high/medium/low counts

---

## /docs-pack

### Purpose
Generate user-facing documentation (README, API reference, runbook, tutorial) for an existing module or feature. Use for: onboarding users, API documentation, operational procedures. Not for: internal technical docs (use internal wiki), code comments (use IDE docstrings).

### Invocation
```
/docs-pack src/api --template api-reference
/docs-pack ./features/auth --type user-guide
```

### Input schema
- `<path>` (required): directory/file to document.
- `--template` (optional): `api-reference`, `user-guide`, `runbook`, `architecture`. Defaults to auto-detect.
- `--audience` (optional): `developer`, `operator`, `user`. Defaults to `developer`.

### Output schema
- Markdown files in `<repo>/docs/<module>/`:
  - `README.md` — overview, quick-start
  - `API-REFERENCE.md` (if applicable) — endpoint/function docs
  - `RUNBOOK.md` (if operational) — procedures, troubleshooting
  - `EXAMPLES.md` — code examples, use cases
- Optional: Mermaid diagrams for flows, architecture
- Memory write: L4 documentation decision

### Agent roster

| Agent | Model | Effort | Tools | Role |
|---|---|---|---|---|
| content-writer | Sonnet | medium | Read, Grep, Glob, Write | Writes documentation from code + examples |
| subject-matter-expert (role) | Sonnet | medium | Read, Bash, Grep | Technical review, accuracy check |
| geo-writer (if public) | Haiku | low | Read, Write | GEO/SEO optimization pass (Phase 2: delegated to /geo-writer skill) |

### Pipeline

```
┌─ Content writer:
│  - Read source code, docstrings, tests
│  - Extract examples
│  - Generate documentation per template
│  → Draft docs
│
├─ Subject-matter expert:
│  - Review accuracy, completeness
│  - Suggest improvements
│  → feedback.md
│
├─ Content writer revisions:
│  └─ Address feedback, finalize
│
├─ (If public-facing) GEO writer:
│  └─ Optimize for AI search readiness (per geo-content rule)
│
└─ Memory write: L4 docs creation decision
   Report: docs location + update reminder
```

No RALF; docs generated in one pass with optional review.

### Eval rubric
Pointer: `plugin/eval/judge-rubrics/docs-pack.md` (Phase 2).

Dimensions:
1. **Completeness** — all key concepts documented
2. **Clarity** — examples are runnable, explanations clear
3. **Accuracy** — matches actual code behavior
4. **Organization** — logical flow, easy to navigate
5. **Style consistency** — follows doc style guide

Pass: avg ≥ 4.0, no dimension < 3.

### RALF wiring
- **No RALF** — docs generation is one-pass; feedback loop is optional reviewer pass.

### Memory writes

| Layer | When | Shape |
|---|---|---|
| L4 | After complete | `.ai-assets-memory/docs/<module>/generation-summary.md` — what was documented, when, audience |

### Failure modes
- **Source code poorly documented:** Content writer infers from tests + examples; flags as "inferred from tests" in doc.
- **API changed since docs written:** Reviewer catches; content writer updates.
- **Examples don't run:** Content writer tests examples; fixes or removes broken ones.

### Observability events
- `workflow_start` — docs-pack with path + template
- `agent_spawned` × 2–3 (content-writer, sme, optional geo-writer)
- `workflow_end` — COMPLETE with file count

---

## /ai-assets-init

### Purpose
Bootstrap a target repository to be ai-assets-aware. Creates CLAUDE.md scaffolding, initializes .ai-assets-memory/ directory structure, configures .gitignore rules. Use on: first run in a new repo, when moving to ai-assets plugin. Idempotent — safe to re-run.

### Invocation
```
/ai-assets-init
/ai-assets-init --codebase-type "python-flask"
```

### Input schema
- `--codebase-type` (optional): `python-flask`, `nodejs-express`, `java-spring`, `go`, `ruby-rails`, `rust`, `dotnet`, etc. If omitted, auto-detect from root files.
- `--overwrite` (optional, default false): if CLAUDE.md exists, overwrite with fresh scaffold. Default: skip if exists.

### Output schema
- `<repo>/CLAUDE.md` — scaffolded with codebase type, empty sections for user to fill
- `<repo>/AGENTS.md` — empty template (optional, for team that wants agent customization)
- `<repo>/.ai-assets-memory/` directory structure:
  - `.gitignore` — templates for what to ignore (session logs, RALF iterations)
  - `.committed/` — opt-in versioned memory (conventions, baselines, decisions)
  - `config.json` — per-repo token/RALF overrides (optional)
  - `learnings.md` — empty template
  - `designs/`, `develop/`, `bugfix/`, `refactor/`, `spikes/`, `security-audits/` — empty subdirs
- `<repo>/.gitignore` — appended with `.ai-assets-memory/` exclusion rule (if not already present)

### Agent roster

| Agent | Model | Effort | Tools | Role |
|---|---|---|---|---|
| scaffolder (internal) | Haiku | low | Write, Read, Glob | Detects codebase type, generates scaffolds |

### Pipeline

```
┌─ Auto-detect codebase type:
│  └─ Check for Pipfile, package.json, pom.xml, go.mod, Cargo.toml, Gemfile, csproj, etc.
│
├─ Generate CLAUDE.md scaffold:
│  └─ Include sections: Overview, Tech Stack, Directory Layout, Key Decisions, Constraints, Getting Started
│     Pre-fill: tech stack (detected), codebase type
│     Leave blank for user: business context, architectural decisions
│
├─ Generate (optional) AGENTS.md:
│  └─ List the 22 base agents available; user can customize per-repo
│
├─ Create .ai-assets-memory structure:
│  ├─ .gitignore with rules for session logs, RALF runs, ephemeral memory
│  ├─ .committed/ subdir with README explaining versioned memory contract
│  ├─ config.json template with override options
│  └─ Subdirs for workflow outputs
│
├─ Update root .gitignore:
│  └─ Add .ai-assets-memory/ rule (if not present)
│
└─ Report: scaffold creation summary, next steps (fill in CLAUDE.md, run workflows)
```

No RALF; scaffolding is one-pass.

### Eval rubric
Pointer: `plugin/eval/judge-rubrics/ai-assets-init.md` (Phase 2).

Dimensions:
1. **Correctness** — scaffold matches detected codebase type
2. **Completeness** — all expected directories and files present
3. **Clarity** — placeholder comments are helpful
4. **No conflicts** — respects existing CLAUDE.md if --overwrite not set
5. **Gitignore safety** — no important files accidentally ignored

Pass: avg ≥ 4.0, no dimension < 3.

### RALF wiring
- **No RALF** — setup is one-pass; idempotent so safe to re-run.

### Memory writes
- L4: `.ai-assets-memory/init-summary.md` — timestamp, codebase type detected, files created

### Failure modes
- **Codebase type ambiguous:** Scaffolder defaults to generic; user can specify with `--codebase-type`.
- **CLAUDE.md exists and --overwrite not set:** Skip creation; report that file exists.
- **Write permission denied:** Escalate to user; ask for elevated permissions or alternate location.

### Observability events
- `workflow_start` — ai-assets-init
- `codebase_type_detected` — detected type
- `scaffold_created` — files/dirs created
- `workflow_end` — COMPLETE

---

## Part B: Companion Skills (Brief Specs)

---

## /ralph

**Purpose:** Standalone RALF entry point for power users. Wraps the RALF loop with explicit oracle and kill-on signal specification. Use when you want to iterate a task until a mechanically-verifiable success signal (test passes, schema validates, output matches regex). Not for open-ended exploration (use `/spike` instead).

**Invocation:**
```
/ralph "write a CLI in Rust" --oracle cli:./test-cli.sh --kill-on oracle-pass
/ralph "generate 100 test cases" --oracle judge:test-case-rubric.md --max-iterations 8
```

**Behavior:**
- Validates `--oracle` and `--kill-on` args (rejects if both missing).
- Initializes RALF run in `.ai-assets-memory/ralph/<run-id>/`.
- Enters loop: generate → check oracle → check kill-on signal → on failure: log iteration + re-inject prompt.
- Caps: 10 iter / 200K tokens / 120 min (overridable in userConfig).
- Writes `.ai-assets-memory/ralph/<run-id>/budget.json` with final cost + iteration count.
- Emits observability events to run log.

**Init vs continuation prompts (G10):** RALF distinguishes the FIRST iteration prompt (init) from subsequent iterations (continuation):

- **Init prompt (iter 1):** full task brief — goal, constraints, evidence, output contract, oracle definition, kill-on signal. Typically 5–15K tokens depending on workflow.
- **Continuation prompt (iter ≥ 2):** state delta only — last-iteration diff, oracle failure summary, top-3 active constraints, kill-on countdown. Typically 1–3K tokens. Reduces per-iteration token cost by ~70%.

Both prompts are stored in `.ai-assets-memory/ralph/<run-id>/`:
- `iter-001/prompt.md` — full init prompt
- `iter-NNN/prompt.md` (N ≥ 2) — continuation prompt with state delta

Continuation template lives at `${CLAUDE_PLUGIN_ROOT}/skills/ralph/templates/continuation-prompt.md`:

```markdown
RALF iteration {N} of max {MAX}.

## State delta from iter {N-1}
- Files changed: {list with line counts}
- Tests run: {pass|fail counts}

## Oracle result (iter {N-1})
{oracle_status}: {oracle_message}
{if failed: top error excerpt, max 200 tokens, wrapped per G1}

## Active constraints (top 3, full list at .ai-assets-memory/ralph/{run-id}/config.json)
1. {constraint 1}
2. {constraint 2}
3. {constraint 3}

## Kill-on countdown
{e.g., "same-error-repeats: 1/3"}

## Your task
Address the oracle failure above. Same task brief as iter 1; reload from
`.ai-assets-memory/ralph/{run-id}/iter-001/prompt.md` if you need full context.
```

---

## /eval

**Purpose:** Evaluate skills and agents against test cases. Runs Tier 2 (smoke: sampled skills) and Tier 3 (behavioral: full test case suites). Use for: pre-release validation, regression checks, skill tuning. Wraps `eval/runner.py`.

**Invocation:**
```
/eval feature-design                   # run all test cases for feature-design skill
/eval --skill feature-design --tier 3  # run Tier 3 only for feature-design
/eval --tier 2                          # run Tier 2 smoke (10 sampled skills × 20 prompts each)
/eval --all                             # run Tier 3 full suite (release gate)
/eval --all --resume                   # resume from last completed case if interrupted
```

**Behavior:**
- Tier 1: linters (frontmatter, schema, references). No LLM calls.
- Tier 2: sampled skills (10 × 20 prompts each), activation precision check. ~60K tokens soft cap.
- Tier 3: all test cases per skill, executor + judge + blind-comparator. Per-skill budget 30–100K tokens.
- Produces `eval/results/<run-id>/summary.json` and per-case `eval/results/<run-id>/<skill>/<case-id>.json`.
- Supports `--resume` flag to pick up from last completed case.

---

## /plugin-doctor

**Purpose:** Self-diagnostic for the plugin. Default mode validates: skills load, hooks executable, run logs parseable. `--calibrate-judge` is a separate opt-in mode that requires calibration sample data (Round 4 O4 + N5).

**Invocation:**
```
/plugin-doctor                           # default smoke test (no LLM cost; fast)
/plugin-doctor --calibrate-judge         # opt-in: judge calibration against samples in plugin/eval/calibration/
/plugin-doctor --runs --last 5           # summarize last 5 runs
/plugin-doctor --health-trends           # context health metrics summary (G8)
```

**Two-step boot model (Round 4 O4):**
- **Default (`/plugin-doctor`):** runs lint checks, hook executable check, runs jsonl parse — does NOT run judge calibration. Reports calibration as "not yet run; use `/plugin-doctor --calibrate-judge` to run". Always passes on a clean install.
- **`--calibrate-judge`:** explicit user command. If `plugin/eval/calibration/` has samples (shipped in B10a per Round 4 N5), runs Spearman correlation per rubric. If samples are missing or count too low (< 4 per rubric), errors clearly: "Insufficient calibration samples at plugin/eval/calibration/<rubric>/. See plugin/docs/concepts/eval.md for guidance."

**Behavior (default mode):**
- Checks skill frontmatter (name, description, required fields, `Use when` trigger pattern per H5) — validates against schema.
- Checks hook scripts: executable bit set, Python syntax valid.
- Checks `.ai-assets-memory/runs/*.jsonl` parsing and summarizes: total runs, avg duration, token totals, success rate.
- Produces a report in stdout + `.ai-assets-memory/plugin-doctor.log`.

---

## /memory-init

**Purpose:** Creates `.ai-assets-memory/` skeleton if missing. Idempotent.

**Behavior:**
- Creates directory structure (same as `/ai-assets-init` memory portion).
- Initializes `learnings.md` with header comment.
- Sets up `.committed/` with allowlist enforcement.
- No-op if already exists.

---

## /memory-recall

**Purpose:** Query `.ai-assets-memory/` (L4) and optionally `~/.claude/ai-assets/learnings.md` (L5) for relevant memories by topic or keyword.

**Invocation:**
```
/memory-recall "authentication"
/memory-recall "React migration" --layer L4
/memory-recall "security" --layer L5 --global
```

**Behavior:**
- Searches `.ai-assets-memory/learnings.md` and subdirs (L4) by keyword.
- If `--global` flag: also searches `~/.claude/ai-assets/learnings.md` (L5, requires `user_global_memory_enabled: true`).
- Returns matching excerpts with context.

---

## /learnings-write

**Purpose:** Curated write to L4 (or L5 if global). Use to capture patterns, lessons learned, architectural decisions worth remembering.

**Invocation:**
```
/learnings-write "Async state management pattern that worked well"
/learnings-write "Why we chose gRPC over REST" --global
```

**Behavior:**
- Prompts for confirmation before write.
- Default: writes to `.ai-assets-memory/learnings.md` (L4, project-scoped).
- With `--global`: writes to `~/.claude/ai-assets/learnings.md` (L5, user-scoped), requires `user_global_memory_enabled: true`.
- Memory-curator agent reviews + approves (if `subagent_learnings_enabled: true`).
- Appends with timestamp, source (workflow, reason).

---

## /context-load

**Purpose:** Load project context with per-role slicing. Returns relevant excerpts from CLAUDE.md, AGENTS.md, ARCHITECTURE.md, project memory for a specific agent role.

**Invocation:**
```
/context-load --for db-engineer
/context-load --for ui-ux-designer --max-tokens 2000
```

**Behavior:**
- Reads target repo's CLAUDE.md, AGENTS.md (if exists).
- Extracts role-relevant sections (db-engineer gets DB sections, ui-ux-designer gets UI/UX sections, etc.).
- Trims to fit token budget (default 2000, configurable).
- Returns Markdown excerpt ready to embed in subagent prompt.

---

## /subagent-spawn

**Purpose:** Typed delegation helper. Enforces role-selection-table constraints when spawning subagents. Use internally by orchestrators; available for power users.

**Invocation:**
```
/subagent-spawn --role developer --stack backend --task "implement auth endpoint"
```

**Behavior:**
- Validates role against available agents.
- Looks up agent model + tool list from `team-protocols/role-selection-table.md`.
- Prepares spawn call with: agent name, context slice, task prompt, tool constraints.
- Returns fully-formed `Agent(...)` call prompt for orchestrator.

---

## /plugin-skill-create

**Purpose:** Scaffold a new skill for THIS PLUGIN (in `plugin/skills/`), with eval test case stub and memory hooks pre-wired. Narrower than Anthropic's `skill-creator` — defers general skill creation to that tool; this focuses on plugin-convention-aligned skills.

**Invocation:**
```
/plugin-skill-create "new-workflow" --invocable --agent-spawn
/plugin-skill-create "analyzer" --type knowledge
```

**Behavior:**
- Prompts for skill name, description, invocable or knowledge, etc.
- Generates `plugin/skills/<name>/SKILL.md` with frontmatter + template body.
- Generates `plugin/skills/<name>/eval/eval-case-001.json` (stub, user fills in).
- Pre-wires: memory write points, RALF capability (if applicable), observability events.
- Outputs path to newly created skill for user to edit.

---

## Part C: Common Patterns

### Standard Workflow Scaffold (every long workflow follows)

```
1. Context load       — read CLAUDE.md, AGENTS.md, .ai-assets-memory/
2. Clarify            — AskUserQuestion if ambiguity exceeds threshold
3. Plan               — present plan (dependency-ordered work packages, effort estimate)
4. User approval gate — proceed only with explicit OK
5. Spawn team         — per role-selection-table.md, one agent per work package
6. Pipeline           — workflow-specific gates (DEVELOP → REVIEW → QA, or variants)
7. Eval               — eval-judge scores against workflow-specific rubric
8. RALF              — loop if rubric not met; capped by iter/tokens/time + kill-on signal
9. Memory write       — durable learnings to .ai-assets-memory/L4 (or L5 if --global)
10. Final report      — TodoList check + completion report (per task-completion rule)
```

### Shared Gate Rules

All workflows enforce:
- **Approval gate:** step 4, user must explicitly approve plan before work begins
- **Test gate:** step 6, code-modifying workflows require passing test suite
- **Eval gate:** step 7, output must score ≥ 4.0 on rubric or be rejected by RALF
- **Budget gate:** session token meter triggers soft warn at 1M, hard pause at 1.5M

### Shared Memory Write Points

| Workflow | L4 write | L4 committed write (opt-in) |
|---|---|---|
| `/feature-design` | wave summaries, final design | finalized design snapshot |
| `/develop` | developer notes, design-to-code trace | release notes per version |
| `/bugfix` | diagnosis, incident summary | incident post-mortem (pattern-matching) |
| `/env-analyze` | environment baseline snapshot | (none) |
| `/refactor` | refactor plan, before/after stats | (none) |
| `/migrate` | migration strategy, validation proof | migration plan + rollback proof |
| `/spike` | research findings | research decision (if go/no-go unanimous) |
| `/security-audit` | audit findings, remediation plan | critical findings incident log |
| `/docs-pack` | docs generation summary | (none) |
| `/ai-assets-init` | init summary | (none) |

### Shared Observability Events

Every workflow writes to `.ai-assets-memory/runs/<run-id>.jsonl`:
- `workflow_start` — workflow name, user input hash, timestamp
- `context_load` — tokens consumed
- `plan_generated` — effort estimate
- `plan_approved` — user gate passed
- `agent_spawned` — agent name, model, token budget, timestamp
- `agent_returned` — tokens in/out, duration
- `ralf_iter` — iteration N, oracle result, kill-on check
- `workflow_end` — final status, token total, duration

Events follow structure: `{ts: ISO8601, event: name, workflow, agent, tokens_in, tokens_out, duration_ms, metadata: {...}}`.

### Few-Shot Example Library Convention (G9)

Workflows that benefit from concrete examples (templates for output contracts, edge cases) draw from a curated example library at `plugin/examples/<skill-name>/<example-id>.json`. Format:

```json
{
  "id": "feature-design-example-001",
  "skill": "feature-design",
  "input": {
    "idea": "Add dark mode to the marketing site"
  },
  "output_contract_version": "1.0.0",
  "output_excerpt": "## PRD\n### Goal\nUsers can ...",
  "tags": ["small-scope", "frontend", "ui"],
  "lift_measured": null
}
```

**Selection rule:** at workflow invocation, the orchestrator embedding-searches the example library for top-k examples matching the user input (`tags` and embedding similarity), then packs only those that fit the remaining token budget AFTER essential context. Per context-engineering guide §3.1: examples consume 0–10% of context; skip entirely if no clear match (precision > recall here).

**Negative examples:** entries with `tags: ["counter-example"]` show what NOT to do. Often more effective than additional positive examples for format compliance.

**v0.1:** library directory exists; example content authored in Phase 3 after baseline runs identify which workflows benefit. Empty library is fine — workflows fall back to instruction-only.

### Workflow Composition

- `/feature-design` output → `/develop` input (IMPLEMENTATION-PLAN.md handed off)
- `/develop` output → `/security-audit` input (code review for security)
- `/bugfix` diagnosis → `/spike` (if issue is architectural, not code)
- `/refactor` output → `/develop` (if refactor opens new capabilities)
- Any workflow output → `/memory-write` (capture patterns learned)

### Structured Subagent Spawn Payload + Return Contract (G7)

To make multi-agent coordination auditable and machine-parseable (replacing free-form HANDOFF text), every subagent spawn uses a typed JSON payload, and every return uses a typed contract. Refactor of `team-protocols/lead-protocol.md` and `developer-protocol.md` in Phase 2 enforces these schemas.

**Spawn payload (orchestrator → subagent), embedded in `Agent` prompt:**

```json
{
  "trace_id": "wf-20260426-abc123-spawn-001",
  "subagent_role": "developer | reviewer | qa | security-engineer | ...",
  "required": true,
  "goal": "Implement work package 3: add OAuth callback handler",
  "constraints": [
    "Follow project Python style (ruff, mypy strict)",
    "No new dependencies without ADR",
    "Tests must cover happy path + 3 error cases"
  ],
  "state_slice": {
    "active_files": ["src/auth/oauth.py", "tests/auth/test_oauth.py"],
    "current_branch": "feature/oauth",
    "related_artefacts": ["docs/features/oauth/PRD.md"]
  },
  "allowed_tools": ["Read", "Grep", "Glob", "Bash", "Write", "Edit"],
  "budget": {
    "max_input_tokens": 30000,
    "max_output_tokens": 1500,
    "max_tool_calls": 25,
    "max_turns": 5,
    "timeout_ms": 600000,
    "retry_budget": 1
  },
  "untrusted_inputs": [
    {"source": "L2:CLAUDE.md", "wrapped": true},
    {"source": "tool:Read:tc-456", "wrapped": true}
  ]
}
```

**Return contract (subagent → orchestrator), embedded in subagent's final message:**

```json
{
  "trace_id": "wf-20260426-abc123-spawn-001",
  "status": "ok | needs_clarification | failed | partial",
  "tokens_used": {"input": 24500, "output": 1320},
  "tool_calls": 18,
  "result": {
    "summary": "OAuth callback handler implemented; 5 tests added; mypy clean",
    "files_changed": ["src/auth/oauth.py", "tests/auth/test_oauth.py"],
    "diff_size_lines": 142
  },
  "evidence": [
    {"artefact_id": "src/auth/oauth.py", "quote": "callback handler at line 47", "span": "L47-L72"}
  ],
  "risks": ["low_test_coverage_on_error_paths", "external_oauth_provider_rate_limits_unknown"],
  "next_actions": ["reviewer: focus on error path coverage; suggest fuzz test"],
  "needs_clarification": null
}
```

**Validation:**
- Spawn payload validated by `subagent-start-budget.py` hook (rejects malformed payload before spawn)
- Return contract validated by `subagent-stop-learnings.py` hook (rejects malformed return; orchestrator must request retry with corrected schema)
- Schemas live at `plugin/schemas/spawn-payload.schema.json` and `plugin/schemas/return-contract.schema.json`

**Migration path:** existing `team-protocols/lead-protocol.md`, `developer-protocol.md`, `reviewer-protocol.md` use free-form Markdown HANDOFF format. Phase 2 refactor adds the JSON contract alongside the prose; orchestrator parses JSON for downstream automation (budget tracking, evidence chain audit, observability events).

---

## Summary

All 10 workflows follow the same structured scaffold with workflow-specific variants on pipeline gates, agents, rubric dimensions, RALF parameters, and memory write points. Companion skills provide utility functions (RALF entry point, eval runner, memory operations, self-diagnostic). Observable events enable tracing, cost auditing, and pattern analysis across runs. The common pattern enables consistency while allowing task-specific flexibility.
