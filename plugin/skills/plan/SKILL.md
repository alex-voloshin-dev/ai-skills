---
name: plan
description: Use this skill when the user has a PRD or feature brief and needs an executable plan before code is written — to plan feature implementation across services and roles by parsing the PRD/feature brief, reading project architecture (ARCHITECTURE.md, CLAUDE.md), decomposing into work packages per service/role with complexity estimates, and running a multi-reviewer feedback loop (product-manager + solution-architect + system-architect).
context: fork
argument-hint: [PRD or feature brief path]
---

# Feature Plan

Plan a feature implementation by understanding the project architecture, decomposing work into service-level and role-level packages, and producing an actionable plan. This is the **planning phase** — no code is written here. Output feeds into `/develop` for execution.

## 1. Receive Feature Requirements

Gather the feature specification from the user:

- **Accepted formats**: PRD, ARD, design doc, implementation plan, ticket/issue, verbal description
- Read every provided document thoroughly
- Extract and organize:
  - **Goal**: What the feature does (1–2 sentences)
  - **Requirements**: Functional (what it does) and non-functional (performance, security, compliance)
  - **Acceptance criteria**: How to verify the feature works
  - **Constraints**: Deadlines, compatibility, dependencies on other teams/services
  - **Out of scope**: What this feature explicitly does NOT cover

If the specification is ambiguous or incomplete — ask before proceeding. Do not assume missing requirements.

## 2. Understand Project Architecture

Read and internalize the project's structure to plan correctly:

### 2a. Read Architecture Documentation

Read the following files (if they exist):

1. **`ARCHITECTURE.md`** — system overview, component boundaries, data flow, service map
2. **`CLAUDE.md`** (root) — tech stack declaration, project structure, conventions
3. **Subdirectory `CLAUDE.md` files** — per-service/module context and stack info

**Extract**:
- Service/module boundaries (monolith modules, microservices, frontend/backend split)
- Tech stack per service (language, framework, database, messaging)
- Communication patterns (REST, gRPC, events, shared DB)
- Data flow relevant to the feature
- Deployment topology (monorepo vs polyrepo, shared vs independent deploys)

### 2b. Scan Project Structure

If documentation is incomplete or absent, scan the filesystem (cross-platform via `Glob` / `Read`, or use one of):

```
// turbo
ls -la 2>/dev/null || dir
```

Look for:
- **Monorepo signals**: `packages/`, `services/`, `apps/`, root `package.json` with workspaces, Nx/Turborepo config
- **Polyrepo signals**: Single service, one `CLAUDE.md`, one tech stack
- **Infrastructure**: `terraform/`, `infra/`, `k8s/`, `helm/`, `docker-compose.yml`
- **Dependency files**: `package.json`, `pom.xml`, `requirements.txt`, `go.mod`, `*.csproj` per service

### 2c. Build Service Map

Create a map of services/modules the feature touches:

```
## Service Map

| Service/Module | Tech Stack | Role | Affected by Feature |
|---|---|---|---|
| [name] | [lang + framework] | @[role] | [yes/no — how] |
| [name] | [lang + framework] | @[role] | [yes/no — how] |
| infrastructure | Terraform / K8s | Agent(devops-engineer) | [yes/no — how] |
```

## 3. Decompose into Work Packages

Break the feature into **work packages** — each package is a self-contained unit of work scoped to one service/module and one role.

### 3a. Identify Work Streams

Group changes by responsibility:

| Work Stream | Role | Scope |
|---|---|---|
| **Frontend** | `Agent(frontend-engineer)` | UI components, pages, client-side logic, API integration |
| **Backend API** | `Agent(java-engineer)` / `Agent(python-engineer)` | Endpoints, business logic, data access, validation |
| **Data Layer** | `Agent(db-engineer)` | Database schema, migrations, queries, indexing, optimization |
| **Infrastructure** | `Agent(devops-engineer)` | Terraform, Docker, K8s, config, secrets |
| **Cloud Architecture** | `Agent(cloud-architect)` | Cloud platform design, landing zones, networking, cost optimization |
| **CI/CD Architecture** | `Agent(devops-architect)` | Pipeline design, deployment strategy, GitHub org governance, platform engineering |
| **ML / Data** | `Agent(ml-engineer)` | Models, pipelines, feature engineering. For LLM/RAG/agent features also consult `context-engineering` skill |
| **Data Pipelines** | `Agent(data-engineer)` | ETL/ELT, data warehousing, Spark, dbt, Airflow |
| **Mobile** | `Agent(mobile-engineer)` | React Native, Flutter, iOS, Android apps |
| **Marketing Content** | `Agent(marketing-strategist)` | Positioning, messaging, GTM, landing pages |
| **Architecture** | `Agent(system-architect)` | System design, ARCHITECTURE.md, component boundaries, tech selection |
| **Cross-cutting** | `Agent(software-engineer)` | Shared libraries, contracts, API specs |

Only include work streams that the feature actually requires. Do not add empty streams.

### 3b. Define Work Packages

For each work stream, create ordered work packages:

```
### [Work Stream]: [Service Name] — @[role]

#### WP-[N]: [Title]
- **Description**: What to implement
- **Files**: Expected files to create/modify
- **Dependencies**: Which WPs must complete first
- **Acceptance criteria**: How to verify this WP is done
- **Complexity**: S (hours) / M (day) / L (days) / XL (week+)
```

**Rules for decomposition**:
- Each WP is independently testable
- WPs within a stream are ordered by dependency (foundations first)
- Cross-service dependencies are explicitly marked
- Database migrations always come before code that uses them
- API contracts defined before consumer implementation

### 3c. Define Integration Points

For features spanning multiple services, explicitly document:

<integration_points>
- **API contracts**: Request/response schemas for new or modified endpoints
- **Events/messages**: New event types, payload schemas, producers, consumers
- **Shared types**: DTOs, enums, or constants shared across services
- **Database changes**: Schema migrations, new tables/columns, index requirements
- **Configuration**: New env vars, feature flags, secrets needed
</integration_points>

## 4–9. Dependency Graph → Risk → Present → Multi-Reviewer → FEATURES.md → Handoff

Steps 4 through 9 — the dependency-graph and risk-table formats, the
plan-presentation template, the **mandatory** multi-reviewer feedback loop
(product-manager + solution-architect + system-architect, loop until all three
`approved`, max 5 cycles), the `FEATURES.md` update, and the implementation
handoff — are binding and unchanged. **Read
[`planning-mechanics.md`](./planning-mechanics.md) and apply Steps 4–9
verbatim.** The plan MUST NOT hand off to `/develop` or update `FEATURES.md`
until the Step 7 multi-reviewer cycle returns `approved` from all three
reviewers with zero remaining critical/major findings.

## Failure modes

- **Ambiguous / incomplete spec** — do NOT assume missing requirements; stop and ask the user (Step 1).
- **Absent architecture docs** — `ARCHITECTURE.md`/`CLAUDE.md` missing → fall back to filesystem scan (Step 2b) to infer service map; never plan blind.
- **Empty work streams** — include only streams the feature actually requires; do not add placeholder streams (Step 3a).
- **Missing dependency ordering** — DB migrations before consuming code, API contracts before consumers; an unordered WP set is a defect (Step 3b).
- **Reviewer divergence** — findings not shrinking or mutually-exclusive asks across cycles → pause and ask the user to arbitrate; hard cap 5 cycles before escalation (Step 7, in `planning-mechanics.md`).
- **`Agent` unavailable** — apply the three Step 7 reviewer roles sequentially in the main thread and record the degraded fan-out in the Review History (`planning-mechanics.md`).
- **Scope drift during build** — update the plan and re-run the affected Step 7 cycle; never let `/develop` proceed against a stale plan (Step 9).

## Integration

- **Input**: PRD, ARD, design doc, or user request
- **Preceded by**: `/feature-design` (produces design pack: PRD + ARD + UX + impl plan), `/architecture` (produces ARD, design docs, API contracts, engineering estimates)
- **Followed by**: `/develop` (implementation per work package)
- **Roles**: `Agent(product-manager)` (requirements; Step 7 reviewer), `Agent(solution-architect)` + `Agent(system-architect)` (architecture; Step 7 reviewers), `Agent(cloud-architect)` (cloud platform), `Agent(devops-architect)` (CI/CD architecture), stack-specific roles (work packages)
- **Skills**: `context-engineering` skill (context pipeline design, RAG, memory, agent harness — for AI/LLM feature work packages), `@team-protocols` (reviewer spawning primitives, Step 7)
- **Companions**: `planning-mechanics.md` — Steps 4–9 binding detail (dependency graph, risk table, plan template, multi-reviewer cycle, FEATURES.md, handoff) — Read + apply verbatim
