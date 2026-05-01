# Parity Matrix

This document tracks semantic parity between the Codex and Windsurf runtime packages stored in this repository.

## Scope (v0.2.0+)

After v0.2.0 parity is enforced between **Codex** and **Windsurf** only. Claude Code lives in `plugin/` and follows its own internal organization (no longer mirrored into a sibling top-level package). The legacy `.claude/` package was removed in v0.2.0.

Pre-v0.2.0 changelog entries below reference `.claude/` as the source of truth for that point in time — those entries are kept verbatim as historical record. Going forward, parity entries reference only `.codex/` ↔ `.windsurf/` (and the shared `.agents/skills/`).

Parity means the runtimes provide equivalent capability coverage, even when the runtime primitives differ.

- Codex uses `.agents/skills` plus `.codex/roles`, `.codex/rules`, `.codex/operations`, templates, and checklists.
- Windsurf uses `.windsurf/rules`, `.windsurf/skills`, `.windsurf/workflows`, `hooks.json`, and supporting skill resources.
- A direct file-for-file match is not required.
- Capability coverage and intent must match.

## Current Baseline

### Roles

- Status: full semantic match
- Coverage target: every role in `.claude/agents/` has a corresponding role in `.codex/roles/` and `.windsurf/rules/roles/`
- Codex execution note: runtime behavior may be attached to skills via visible `.codex/rules/role-overlays/` plus `codex-roles` frontmatter instead of hidden agent invocation

### Skills

- Status: full semantic match (with documented exceptions)
- Coverage target: every skill in `.agents/skills/` has a corresponding skill in `.windsurf/skills/`
- Notes: Windsurf skill bodies stay concise and use `.claude/skills/` as workflow/reference input when the Claude version is more detailed

#### Intentional Claude-only skills

These skills rely on Claude Code's native multi-agent spawning capability, which has no equivalent in Codex or Windsurf runtimes. They are intentionally excluded from parity.

| Skill | Reason |
|---|---|
| `team-protocols` | Shared protocols for Claude Code's Agent tool with named subagent spawning. Codex and Windsurf lack runtime multi-agent primitives. |
| `team-bugfix` | Multi-agent coordinated bugfix workflow using Claude Code's parallel Agent spawning. No equivalent runtime primitive exists. |
| `team-dev` | Multi-agent coordinated feature development workflow using Claude Code's parallel Agent spawning with developer/reviewer/QA pipeline. No equivalent runtime primitive exists. |

### Rules and Guardrails

- Status: semantic match
- Claude uses rules, hooks, and settings
- Codex uses rules, operations, and checklists
- Windsurf uses rules plus workspace hooks
- Mapping is capability-based rather than file-name-based

### Workflows

- Status: semantic match
- Claude stores many user-facing procedures as skills
- Windsurf exposes user-facing procedures as `.windsurf/workflows/` while keeping reusable knowledge in `.windsurf/skills/`

### Templates

- Status: semantic match
- Claude templates focus on Claude-oriented runtime assets
- Codex templates focus on `AGENTS.md`, skill authoring, and Codex-native scaffolding
- Windsurf stores template and checklist material as supporting resources inside relevant skills instead of a separate top-level primitive

## Change Log

### 2026-04-19: product-mgmt → product, feature-plan → plan, multi-reviewer loops

Renamed planning skills and added mandatory multi-reviewer feedback loops:

- `product-mgmt` → `product` (all three packages and Windsurf workflow). Added Step 8 "Multi-Reviewer Feedback Loop" with `product-manager`, `marketing-strategist`, `content-writer`, `seo-engineer` as reviewers. Existing steps 8–9 renumbered to 9–10.
- `feature-plan` → `plan` (all three packages and Windsurf workflow). Added Step 7 "Multi-Reviewer Feedback Loop" with `product-manager`, `solution-architect`, `system-architect` as reviewers. Existing steps 7–8 renumbered to 8–9.

Loop semantics: reviewers produce findings reports (Critical/Major/Minor + verdict), deliverable author applies all actionable findings, cycle re-runs until every reviewer returns `approved`. Max 5 cycles, user arbitration on divergence. Claude uses parallel `Agent` subagent spawning; Codex/Windsurf apply roles sequentially per-reviewer pass.

Updated all inbound cross-references (`/product-mgmt` → `/product`, `/feature-plan` → `/plan`, and skill-style references in `.agents/`, `.codex/`, `.windsurf/`) across agents, roles, skills, workflows, and `.claude/settings.json` permissions.

| Asset | Claude | Codex | Windsurf |
|---|---|---|---|
| Skill directory (was product-mgmt) | `.claude/skills/product/` | `.agents/skills/product/` | `.windsurf/skills/product/` |
| Skill directory (was feature-plan) | `.claude/skills/plan/` | `.agents/skills/plan/` | `.windsurf/skills/plan/` |
| Workflow (was product-mgmt) | N/A (skill is user-invocable) | N/A | `.windsurf/workflows/planning/product.md` |
| Workflow (was feature-plan) | N/A (skill is user-invocable) | N/A | `.windsurf/workflows/planning/plan.md` |
| Multi-reviewer step | Step 8 (product), Step 7 (plan) — `Agent` subagent spawn | Step 8 / Step 7 — sequential role application | Step 8 / Step 7 — sequential role application |
| Cross-reference updates | agents (5), skills (architecture, context-engineering, feature-dev, infra-change, ml-pipeline, project-init, team-dev) | roles (5), skills mirror | rules/roles (5), skills + workflows mirror |
| `.claude/settings.json` | permissions entry renamed product-mgmt → product, plan permission added | — | — |

Canonical names: `product` (was `product-mgmt`), `plan` (was `feature-plan`).

### 2026-04-15: geo-writer skill + geo-content guardrail

Added `geo-writer` skill and `geo-content` guardrail across all three packages. Optimizes public-facing text for Generative Engine Optimization (GEO) and Answer Engine Optimization (AEO) so content is cited by AI engines (ChatGPT, Claude, Perplexity, Gemini, Google AI Overviews).

| Asset | Claude | Codex | Windsurf |
|---|---|---|---|
| Skill | `.claude/skills/geo-writer/` | `.agents/skills/geo-writer/` | `.windsurf/skills/geo-writer/` |
| Full reference | `geo-writing-guide.md` (resource) | `geo-writing-guide.md` (resource) | `geo-writing-guide.md` (resource) |
| Checklist | `pre-publish-checklist.md` (resource) | `pre-publish-checklist.md` (resource) | `pre-publish-checklist.md` (resource) |
| Guardrail rule | `.claude/rules/geo-content.md` | `.codex/rules/geo-content.md` | `.windsurf/rules/geo-content.md` |
| blog-post | step 4 added (GEO pass), humanizer renumbered to 4.5, structured data upgraded, decision gate updated | step 4 added, step 4.5, structured data, decision gate | workflow step 4 added, step 4.5, structured data, decision gate |
| content-creation | Gate 7 (GEO/AEO Structure) added, humanization renumbered to Gate 8 | Gate 7 added, Gate 8 | Gate 7 added, Gate 8 |
| docs | GEO/AEO checklist added for public content | GEO checklist added | GEO checklist added |
| marketing | GEO note on email ops, social excluded | GEO note on email ops | GEO note on email ops |
| seo-review | step 3h (GEO/AEO Audit) added | step 3h added | step 3h added, workflow step 3h added |
| marketing-operations | Integration section updated | Integration section updated | Integration section updated |
| Agents/roles updated | content-writer, content-designer, seo-engineer, marketing-strategist | content-writer, content-designer, seo-engineer, marketing-strategist | content-writer, content-designer, seo-engineer, marketing-strategist |
| Windsurf workflow | N/A | N/A | `.windsurf/workflows/marketing/geo-writer.md` |
| humanize-content rule | Pairing section added | Pairing section added | Pairing section added |

Canonical name: `geo-writer` (skill), `geo-content` (rule/guardrail).

### 2026-04-04: team-dev skill + team-bugfix analyze-local integration

Added `team-dev` as a new Claude-only multi-agent feature development skill. This is the
team-coordinated version of `feature-dev`, using the same DEVELOP → REVIEW → QA pipeline
as `team-bugfix` but applied to feature implementation from PRD/design docs.

Added optional local environment analysis (`@analyze-local` via env-analyzer subagent) to
`team-bugfix` for bugs involving Docker/container/local dev environment issues.

| Asset | Claude | Codex | Windsurf |
|---|---|---|---|
| `team-dev` | `.claude/skills/team-dev/` | N/A (Claude-only) | N/A (Claude-only) |
| `team-bugfix` update | `.claude/skills/team-bugfix/` | N/A (Claude-only) | N/A (Claude-only) |

### 2026-04-04: social-media-manager generalization

Removed all project-specific references (friendly4AI, founder names, product-specific domain)
from the `social-media-manager` skill across all three packages. The skill now reads product
context from `marketing/MARKETING.md` at runtime, making it reusable for any project.
Cleaned machine-specific paths from `settings.json`. Scoped parity rules in `.claude/CLAUDE.md`
as "ai-assets repo only". Created `PARITY.md` documenting the full cross-vendor parity model.

### 2026-03-23: social-media-manager skill

Added `social-media-manager` skill across all three packages. Creates social media posts across X/Twitter, LinkedIn, and Facebook with 2026 algorithm knowledge, brand voice guidelines, anti-AI-detection patterns, and post templates.

| Asset | Claude | Codex | Windsurf |
|---|---|---|---|
| Skill | `.claude/skills/social-media-manager/` | `.agents/skills/social-media-manager/` | `.windsurf/skills/social-media-manager/` |
| Brand voice reference | `references/brand-voice.md` (resource) | `references/brand-voice.md` (resource) | `references/brand-voice.md` (resource) |
| Platform guide reference | `references/platform-guide.md` (resource) | `references/platform-guide.md` (resource) | `references/platform-guide.md` (resource) |
| Workflow | user-invocable skill | user-invocable skill | `.windsurf/workflows/marketing/social-media-manager.md` |
| Consumers | `marketing`, `content-creation` | `marketing`, `content-creation` | `marketing`, `content-creation` |

Canonical name: `social-media-manager` (skill).

### 2026-03-19: humanizer skill + humanize-content guardrail

Added `humanizer` skill and `humanize-content` guardrail across all three packages.

| Asset | Claude | Codex | Windsurf |
|---|---|---|---|
| Skill | `.claude/skills/humanizer/` | `.agents/skills/humanizer/` | `.windsurf/skills/humanizer/` |
| Pattern catalog | `ai-writing-patterns.md` (resource) | `ai-writing-patterns.md` (resource) | `ai-writing-patterns.md` (resource) |
| Guardrail rule | `.claude/rules/humanize-content.md` | `.codex/rules/humanize-content.md` | `.windsurf/rules/humanize-content.md` |
| blog-post | step 4 added | step 4 added | workflow step 4 added |
| content-creation | Gate 7 added | Gate 7 added | Gate 7 added |
| docs | public content checklist added | public content humanizer step added | public content checklist added |
| marketing | social-post + email steps added | step 4 added | social-post + email steps added |

Canonical name: `humanizer` (skill), `humanize-content` (rule/guardrail).

## Review Rules

- new roles must be added to all runtime packages in the same change set
- new skills must be added to all runtime packages in the same change set, using runtime-native representations where needed
- new user-facing task procedures should update Windsurf workflows when an equivalent skill is added to Codex (or vice versa)
- shared skill bodies in `.agents/skills/` must use neutral wording readable by both runtimes
- never introduce a project-specific reference into shared assets
- record every parity-impacting change with a dated entry in this file
- (v0.2.0+) Claude Code plugin changes are tracked in `plugin/CHANGELOG.md` and do NOT need to land in `.codex/` or `.windsurf/`
