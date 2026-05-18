# Feature Plan — Dependency Graph, Risk, Presentation & Review Mechanics

Binding detail for the `/plan` workflow, moved out of `SKILL.md` for
progressive disclosure. **Behavior is identical to the prior single-file form —
nothing here is optional.** `SKILL.md` instructs you to *Read this file and
apply Steps 4–9 verbatim*; the templates, rules, and the multi-reviewer cycle
below are the enforcement contract.

## 4. Dependency Graph

Visualize the execution order:

```
## Dependency Graph

WP-1: [DB migration]
  └─► WP-2: [Backend API]
        ├─► WP-3: [Frontend integration]
        └─► WP-4: [Infrastructure/config]
WP-5: [Tests] ← depends on WP-2, WP-3
```

Identify:
- **Critical path**: Longest chain of dependent WPs — determines minimum timeline
- **Parallelizable**: WPs that can be worked on simultaneously by different roles
- **Blockers**: External dependencies (other teams, third-party APIs, approvals)

## 5. Risk Assessment

Evaluate risks for each work stream:

| Risk | Impact | Likelihood | Mitigation |
|---|---|---|---|
| [risk description] | High/Med/Low | High/Med/Low | [mitigation strategy] |

**Common risks to evaluate**:
- Breaking changes to existing APIs (backward compatibility)
- Database migration on large tables (performance, downtime)
- Cross-service coordination (deployment order matters)
- New dependencies or services (operational complexity)
- Security implications (new auth flows, data exposure)

## 6. Present the Plan

Compile the full plan and present to the user:

```
# Feature Plan: [Feature Name]

## Goal
[1–2 sentences]

## Architecture Impact
- Services affected: [list]
- New services: [if any]
- Database changes: [yes/no — summary]
- Infrastructure changes: [yes/no — summary]

## Work Packages

### Stream 1: [name] — @[role]
| WP | Title | Complexity | Dependencies | Status |
|----|-------|------------|--------------|--------|
| WP-1 | [title] | M | — | planned |
| WP-2 | [title] | S | WP-1 | planned |

### Stream 2: [name] — @[role]
| WP | Title | Complexity | Dependencies | Status |
|----|-------|------------|--------------|--------|
| WP-3 | [title] | L | WP-1 | planned |

## Critical Path
WP-1 → WP-2 → WP-5 (estimated: [timeframe])

## Risks
[table from Step 5]

## Next Step
Run `/develop` per work package, applying the designated role.
```

Wait for user approval. The user may reorder, split, merge, or remove work packages.

## 7. Multi-Reviewer Feedback Loop

The Feature Plan MUST pass a mandatory multi-reviewer cycle before handoff. Do
not update `FEATURES.md` or hand off to `/develop` until every reviewer returns
`approved`.

### Reviewer Panel

Spawn each role as an independent named subagent per `@team-protocols`
`Spawn Primitives`. If `Agent` is unavailable, apply the three roles
sequentially in the main thread and note the degraded fan-out in the Review
History. Each reviewer runs with the current plan as input:

- `Agent(product-manager)` as `reviewer-product` — scope alignment with the PRD, WP coverage of acceptance criteria, risk coverage, correct prioritization, missing requirements
- `Agent(solution-architect)` as `reviewer-solution` — end-to-end design coherence, integration points, API contracts, cross-service coordination, tech stack fit per WP, non-functional requirements coverage
- `Agent(system-architect)` as `reviewer-system` — system boundaries, component topology, data flow, ARCHITECTURE.md consistency, scalability and deployment implications of the WP decomposition

### Cycle

1. **Spawn reviewers in parallel**. Each produces a findings report: Critical (must fix), Major (should fix, justify if waived), Minor (optional), plus an explicit verdict: `approved` / `approved-with-changes` / `rejected`
2. **Collect all reports** before editing
3. **Apply all actionable findings** to the plan (re-scope WPs, adjust dependencies, add missing streams, revise complexity). Resolve conflicts with priority Critical > Major > Minor; on ties, system-architect (topology/boundaries) > solution-architect (design coherence) > product-manager (scope fit). Record waivers with a one-line rationale
4. **Re-spawn the same three reviewers** against the updated plan
5. **Loop until every reviewer returns `approved`** with zero remaining critical/major findings

Termination: pass when all three are `approved`. On divergence (findings not
shrinking, mutually exclusive asks) — pause and ask the user to arbitrate. Max
5 cycles before escalation.

Record the review history at the bottom of the plan as a `## Review History`
section listing each cycle's reviewer verdicts and open issue counts.

## 8. Update FEATURES.md

After the plan is approved, **apply `Agent(product-manager)`** and update
`FEATURES.md`:

1. If `FEATURES.md` does not exist — create it at the project root
2. Add or update the feature entry with status `planned`
3. If the feature has a PRD or spec — save it in `features/` directory and link from `FEATURES.md`

## 9. Handoff to Implementation

After approval, guide execution:

- **Sequential** (single developer): Execute WPs in dependency order using `/develop` for each
- **Parallel** (multiple developers/sessions): Assign independent WPs to separate sessions, each applying the appropriate role
- Track WP status: `planned` → `in_progress` → `done`
- Update the plan if scope changes during implementation
