---
name: memory-init
description: Initialize the .ai-assets-memory/ skeleton in the current project — directory structure, .gitignore rules, learnings.md template, .committed/ allowlist. Idempotent — safe to re-run on a project that already has memory wired. Use after cloning a new repo or upgrading from a pre-memory plugin version.
context: fork
---

# /memory-init — Memory Skeleton Initializer

Create the `.ai-assets-memory/` directory tree from `plugin/memory/templates/` per `03-MEMORY-ARCHITECTURE.md` §3 L4. Idempotent.

## When to use

- After cloning a repo that uses ai-assets but has no `.ai-assets-memory/` (first run on a fresh checkout)
- After upgrading the plugin to a version that adds new memory paths
- When `/plugin-doctor` reports "no memory tree present"

Not needed when running `/ai-assets-init` — that workflow runs memory-init as one of its steps.

## Behavior

1. Detect current project root (`<repo>` = the cwd where the user runs the command).
2. Check for existing `.ai-assets-memory/`:
   - If missing → create
   - If present → no-op for existing files; create only what is missing (idempotent)
3. Create directory tree:
   ```
   <repo>/.ai-assets-memory/
   ├── .gitignore               (from plugin/memory/templates/ai-assets-memory.gitignore)
   ├── learnings.md             (empty header template)
   ├── runs.jsonl               (touch-create, append-only)
   ├── errors.log               (touch-create, append-only)
   ├── redactions.log           (touch-create, append-only)
   ├── sessions/                (per-session subdirs created by hooks)
   ├── ralph/                   (per-RALF-run subdirs)
   ├── pending-flush/           (PreCompact flush markers)
   ├── designs/                 (/feature-design output summaries)
   ├── env-reports/             (/env-analyze baselines)
   ├── refactor/                (/refactor logs)
   ├── migrate/                 (/migrate plans)
   ├── spikes/                  (/spike reports)
   ├── security-audits/         (/security-audit findings)
   ├── docs/                    (/docs-pack generation summaries)
   └── .committed/
       ├── README.md            (from plugin/memory/templates/committed-readme.md)
       ├── .allowlist-extensions.txt   (project-extension allowlist, empty by default)
       ├── conventions.md       (from plugin/memory/templates/conventions-schema.md, empty body)
       └── learnings.md         (committed-learnings template, empty body)
   ```
4. Append `.ai-assets-memory/` rule to `<repo>/.gitignore` if not already present.
5. Print summary: created vs skipped paths.

## Hard rules

- **Never overwrite** existing files. If a file exists, skip it and report "skipped: <path>".
- **Never write to `.committed/` paths outside the allowlist** — `pre-tool-use-committed-write.py` hook (Round 8 CRIT-1) enforces; this skill should not bypass.
- **PII filter applies** to any seeded content per `memory-discipline.md` rule 2.

## Failure modes

- **No write permission in cwd:** report error, suggest `cd` to a writable directory or run with elevated permissions.
- **Existing `.ai-assets-memory/` corrupted (bad JSON, bad allowlist):** flag corrupted files but do not delete or rewrite them. Suggest user inspect and back up before re-running.

## Memory writes

| Layer | When | Shape |
|---|---|---|
| L4 | On first init | `.ai-assets-memory/init-summary.md` — timestamp + version + paths created |

## Integration

- **Templates source**: `${CLAUDE_PLUGIN_ROOT}/memory/templates/` (B9: 7 + pii-patterns.txt)
- **Called by**: `/ai-assets-init` (full bootstrap including memory), used standalone for upgrades
- **Rules**: `memory-discipline` (write rules per layer), `memory-validation` (entry validation)
- **Hooks**: `pre-tool-use-committed-write.py` validates `.committed/` writes against allowlist
