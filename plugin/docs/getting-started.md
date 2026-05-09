# Getting Started with ai-assets

A 30-minute tutorial: install the plugin, bootstrap your repo, run a first feature design, observe the outputs.

## Prerequisites

- Claude Code installed (any recent version)
- A target repo to apply the plugin to (this can be your real project — the plugin is idempotent and doesn't modify your source code on first run)
- 30 minutes

## 1. Install the plugin

```bash
# From git
claude plugin install https://github.com/alex-voloshin-dev/ai-assets

# From local checkout (developer mode)
claude plugin install ./plugin
```

Claude Code will prompt for `userConfig` values (token caps, RALF defaults, opt-in flags). Defaults are sensible for personal use on a Max subscription. Press Enter to accept; you can change them later via `/plugin configure ai-assets`.

Verify install:

```bash
/plugin status ai-assets
```

You should see the plugin listed with all its skills and agents discovered.

## 2. Bootstrap your repo

```bash
cd /path/to/your/project
/ai-assets-init
```

This is idempotent — safe to run on a fresh checkout or an existing project. It:
- Auto-detects your codebase type (`pyproject.toml` → python-fastapi, `package.json` → node, etc.)
- Creates `CLAUDE.md` if it doesn't exist (skipped if you already have one)
- Creates `.ai-assets-memory/` directory tree
- Adds `.ai-assets-memory/` to your `.gitignore` (with `.committed/` exception for opt-in versioned memory)

Open the new `CLAUDE.md` and fill in the **Business Context** section. The other sections are pre-filled from auto-detection.

## 3. Run a first feature design

Pick a small feature idea — 1 to 3 sentences. The plugin works best with concrete user-facing capabilities:

```bash
/feature-design "Users can save posts to read later"
```

This invokes the `feature-design-lead` orchestrator agent, which spawns a 9-agent team across three waves:
- **Wave 1** (parallel): `product-manager` writes PRD, `system-architect` writes ARCHITECTURE, `marketing-strategist` writes MARKET-ANALYSIS
- **Wave 2** (parallel): `ui-ux-designer` writes UX-FLOW, `db-engineer` writes DATA-MODEL, `security-engineer` reviews for risks, `qa-engineer` reviews acceptance criteria
- **Wave 3** (sequential): cross-check + `eval-judge` scores against the rubric

Output goes to `<repo>/docs/features/<feature-id>/` (versioned in git). You should see 8 markdown files: PRD, MARKET-ANALYSIS, ARCHITECTURE, UX-FLOW, DATA-MODEL, IMPLEMENTATION-PLAN, RISKS, REVIEW-LOG.

Token spend: ~150–250K total. Time: 5–15 minutes depending on complexity. The eval-judge will RALF (re-iterate) up to 5 times if the rubric score is below 4.0.

## 4. Observe the outputs

Open `<repo>/docs/features/<feature-id>/REVIEW-LOG.md`. This is the trace of what every agent did, what scores the rubric assigned, and what (if anything) needed revision.

Open `IMPLEMENTATION-PLAN.md`. This is the input to `/develop` — work packages mapped to engineering roles, with effort estimates and dependencies.

Now you have a complete design pack. From here you can:
- Iterate on the design manually (it's just markdown — edit and commit)
- Hand it off to engineers (the plan is structured for hand-off)
- Pipe it directly into `/develop` for multi-agent implementation

## 5. Try a smaller workflow

Not every task needs the full design pack. Try one of these for shorter feedback loops:

```bash
# Plan a specific change without spawning the full team
/plan "Add OAuth login with Google as an alternative to email/password"

# Diagnose a local environment issue
/env-analyze

# Quick exploration of a question
/spike "Should we use gRPC instead of REST?"
```

Each workflow has its own user doc under `plugin/docs/workflows/` — start there.

## 6. Check plugin health

```bash
/plugin-doctor
```

Default mode runs linters (no LLM cost). It validates skill frontmatter, hook references, run-log integrity. Pass on a clean install.

## What's next

- Read [docs/concepts/memory.md](concepts/memory.md) to understand what gets persisted across sessions
- Read [docs/concepts/eval.md](concepts/eval.md) to understand how `eval-judge` scores workflow outputs
- Read [docs/concepts/ralf.md](concepts/ralf.md) to understand the iteration loop with `--kill-on` signals
- Browse [docs/workflows/](workflows/) for one user doc per slash command

## Troubleshooting

**`/feature-design` is taking too long.** Check `userConfig.ralph_session_max_iter` and `ralph_session_token_budget` — RALF iterations may be eating your budget. The hard cap will pause and ask you before continuing.

**`/plugin-doctor` reports CRITICAL findings.** Read the report. Most common issue: missing `CLAUDE.md` in the target repo (run `/ai-assets-init` first).

**Memory writes failing.** Check that `.ai-assets-memory/` exists and is writable. Run `/memory-init` to recreate the skeleton.

**A subagent returns `status: needs_clarification`.** The orchestrator surfaces the question. Answer it in chat; the workflow resumes from the spawn point.
