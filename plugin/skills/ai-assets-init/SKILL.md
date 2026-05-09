---
name: ai-assets-init
description: Use when bootstrapping a target repository to be ai-assets-aware on first run in a new repo or when adopting the ai-assets plugin. Creates CLAUDE.md scaffolding, initializes .ai-assets-memory/ directory tree from L1 templates, configures .gitignore. Idempotent — safe to re-run.
context: fork
argument-hint: "[--codebase-type <type>] [--overwrite]"
---

# /ai-assets-init — Bootstrap a Target Repository

One-time (or re-runnable) setup for a target repo. Detects codebase type, scaffolds `CLAUDE.md` + `AGENTS.md`, creates `.ai-assets-memory/` tree from L1 templates, appends `.gitignore` rules. Idempotent.

## When to use

- First run of any ai-assets workflow on a fresh repo
- Adopting the ai-assets plugin in an existing repo (new for the team)
- After upgrading the plugin to a version that adds new memory paths or templates

## Not for

- Re-initializing only memory (use `/memory-init` for that)
- Modifying an existing `CLAUDE.md` (manual edit — this skill never overwrites without `--overwrite`)

## Invocation

```
/ai-assets-init
/ai-assets-init --codebase-type python-flask
/ai-assets-init --overwrite                  # rare; only when CLAUDE.md is empty/stale
```

## Arguments

| Flag | Default | Effect |
|---|---|---|
| `--codebase-type` | auto-detect | `python-flask`, `python-fastapi`, `nodejs-express`, `nodejs-nextjs`, `astro`, `sveltekit`, `remix`, `nodejs-bun`, `deno`, `java-spring`, `kotlin-spring`, `kotlin-ktor`, `elixir-phoenix`, `go`, `ruby-rails`, `rust`, `dotnet`, `mixed`, `generic` |
| `--overwrite` | false | If `CLAUDE.md` already exists, OVERWRITE with fresh scaffold. Default: skip if exists |

## Output

- `<repo>/CLAUDE.md` — scaffolded with codebase type, empty sections for user
- `<repo>/AGENTS.md` — empty template (optional, for team customization of agents per-repo)
- `<repo>/.ai-assets-memory/` directory tree (per `/memory-init` spec)
- `<repo>/.gitignore` — appended `.ai-assets-memory/` exclusion rule (if not present)

## Agent roster

| Agent | Model | Effort | Tools | Role |
|---|---|---|---|---|
| `scaffolder` (internal — resolves to `software-engineer` with restricted tools) | haiku | low | Write, Read, Glob | Detects codebase type, generates scaffolds |

## Pipeline

```
┌─ Auto-detect codebase type:
│  └─ Check for: Pipfile, pyproject.toml, package.json, pom.xml,
│     build.gradle.kts, go.mod, Cargo.toml, Gemfile, mix.exs,
│     *.csproj, astro.config.mjs, svelte.config.js, remix.config.js,
│     bun.lockb / bunfig.toml, deno.json / deno.jsonc / deps.ts
│     Multiple matches → mixed; none → generic
│
├─ Generate CLAUDE.md scaffold:
│  └─ Sections: Overview, Tech Stack, Directory Layout, Key Decisions,
│     Constraints, Getting Started
│     Pre-fill: tech stack (detected), codebase type
│     Leave blank for user: business context, architectural decisions
│
├─ Generate (optional) AGENTS.md:
│  └─ List all plugin agents enumerated from `plugin/agents/`
│     (count auto-tracks future additions) with brief role descriptions
│     User can override / add per-repo customization
│
├─ Create .ai-assets-memory/ tree (delegate to /memory-init logic):
│  ├─ .gitignore (from plugin/memory/templates/ai-assets-memory.gitignore)
│  ├─ .committed/ subdir with README + allowlist-extensions
│  ├─ config.json (per-repo override stub for token caps + RALF caps)
│  ├─ learnings.md (empty template)
│  ├─ runs.jsonl, errors.log, redactions.log (touch-create)
│  └─ workflow subdirs: designs/, develop/, bugfix/, refactor/,
│     migrate/, spikes/, security-audits/, env-reports/, docs/
│
├─ Update root .gitignore:
│  └─ Add .ai-assets-memory/ rule (if not already present);
│     also add `.committed/` is tracked exception (negation rule)
│
└─ Print scaffold creation summary + next steps
   ("Fill business context in CLAUDE.md, run /feature-design or /develop")
```

No RALF — scaffolding is one-pass; idempotent so safe to re-run.

## Codebase-type detection markers + template deltas

| Type | Markers | CLAUDE.md template deltas |
|---|---|---|
| `astro` | `astro.config.mjs`; `package.json` has `"astro"` dep | Primary role: `frontend-engineer`. Note SSG/SSR/hybrid mode. Likely Tailwind / shadcn-ui. Playwright for E2E |
| `sveltekit` | `svelte.config.js`; `package.json` has `"@sveltejs/kit"` dep | Primary role: `frontend-engineer`. Note SSR/SSG modes. Tailwind / shadcn-ui likely. Playwright for E2E |
| `remix` | `remix.config.js`; `package.json` has `"@remix-run/*"` deps | Primary role: `frontend-engineer`. Note SSR-first full-stack. Tailwind / shadcn-ui likely. Playwright for E2E |
| `nodejs-bun` | `bun.lockb` or `bunfig.toml` | Use `bunx` over `npx`. Native TypeScript (no `tsc` step). Native test runner (`bun test`) |
| `deno` | `deno.json` / `deno.jsonc`; `deps.ts` | Use `deno run` / `deno test`. Built-in TS. Document the permissions model (`--allow-net`, `--allow-read`, …) |
| `elixir-phoenix` | `mix.exs` with `:phoenix` dep | Primary role: `elixir-engineer` (NOT `software-engineer` for stack-specific work). ExUnit for tests. `mix release` for deploy |
| `kotlin-spring` | `build.gradle.kts` + `kotlin` plugin + Spring deps | Primary role: `java-engineer`. Gradle Kotlin DSL. JUnit + Kotlin idioms |
| `kotlin-ktor` | `build.gradle.kts` + `io.ktor` deps | Primary role: `java-engineer`. Ktor coroutines model. H2 + Exposed common stack |

## Hard rules

- **Never overwrite `CLAUDE.md` without `--overwrite`** — refuse with: "CLAUDE.md exists; pass --overwrite to replace"
- **`pre-tool-use-committed-write.py` hook applies** to any `.committed/` writes (committed-allowlist enforcement)
- **Idempotent** — re-running on a fully-set-up repo is a no-op + report

## Eval rubric

Pointer: `plugin/eval/judge-rubrics/ai-assets-init.md` (B10).

Dimensions:
1. **Correctness** — scaffold matches detected codebase type
2. **Completeness** — all expected directories and files present
3. **Clarity** — placeholder comments are helpful
4. **No conflicts** — respects existing `CLAUDE.md` if `--overwrite` not set
5. **Gitignore safety** — no important files accidentally ignored

Pass: avg ≥ 4.0, no dimension < 3.

## Memory writes

| Layer | When | Shape |
|---|---|---|
| L4 | After complete | `.ai-assets-memory/init-summary.md` — timestamp, plugin version, codebase type detected, files created/skipped |

## Failure modes

- **Codebase type ambiguous (multiple stacks detected):** scaffolder defaults to `mixed`; user can specify with `--codebase-type`
- **CLAUDE.md exists and `--overwrite` not set:** skip CLAUDE.md creation; report exists; continue with `/memory-init` portion
- **Write permission denied:** escalate to user with clear path; suggest checking repo writeability or running with elevated permissions
- **Plugin not installed properly (`${CLAUDE_PLUGIN_ROOT}` empty):** error with: "Plugin templates not found. Verify plugin install with `/plugin status ai-assets`"

## Observability events

- `workflow_start` — ai-assets-init
- `codebase_type_detected` — detected type
- `scaffold_created` — files/dirs created (vs skipped)
- `workflow_end` — `COMPLETE`

## Integration

- **Reads templates from**: `${CLAUDE_PLUGIN_ROOT}/memory/templates/` (7 files for memory skeleton). PII pattern file is at `${CLAUDE_PLUGIN_ROOT}/hooks/scripts/pii-patterns.txt` (loaded by hooks, not copied during init); project extension at `.ai-assets-memory/.committed/pii-patterns.txt` (created on demand).
- **Schemas**: `plugin/schemas/spawn-payload.schema.json` (G7 — even though `scaffolder` is internal, payload still embedded for consistency)
- **Sub-workflow**: `/memory-init` (the memory portion of the bootstrap)
- **Companions**: `/plugin-doctor` (verify install before init), `/context-load` (after init, validate context loads correctly)
- **Rules**: `memory-discipline` (write rules per layer), `untrusted-content-wrapping` (G1 wrap on existing CLAUDE.md if `--overwrite` reads it for backup)
- **Hooks**: `pre-tool-use-committed-write.py` (committed-allowlist enforcement on `.committed/` writes), `session-start-context.py` (will read newly-created CLAUDE.md on next session)
