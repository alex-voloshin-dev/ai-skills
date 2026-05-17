# `.ai-skills-memory/.committed/` — versioned project memory

> Seeded by `/ai-skills-init` into target repo at `.ai-skills-memory/.committed/README.md`. Edit freely.

This directory is the **opt-in versioned** part of the `ai-skills` plugin's project memory (L4 in the 6-layer model). Everything else under `.ai-skills-memory/` is gitignored — only paths matching the allowlist (see `pii-patterns.txt` and `.allowlist-extensions.txt`) are permitted here, and they ARE committed to git so the team shares them.

## When to write here

Put content here that the **whole team** should see and version-control:

- `conventions.md` — team-confirmed coding/architectural conventions
- `architecture-decisions/<date>-<title>.md` — ADRs with full context, options, decision, consequences
- `eval-baselines/<release-tag>.json` — eval scorecards worth tracking across releases
- `decisions/<date>-<topic>.md` — `/spike` go/no-go outcomes the team accepted (per Q4: ALWAYS-ASK before write here)
- `releases/<version>/changes.md` — release notes per `/develop` PR open
- `pii-patterns.txt` — project-specific PII regex patterns (extends plugin defaults)
- `.allowlist-extensions.txt` — additional file patterns to allowlist

## When NOT to write here

- Ephemeral session state — goes to `.ai-skills-memory/sessions/<run-id>/` (L3, gitignored)
- Subagent reports — `.ai-skills-memory/sessions/<run-id>/subagent-reports/` (L3)
- Tool failure logs — `.ai-skills-memory/errors.log` (L4 root, gitignored)
- Run-specific RALF iterations — `.ai-skills-memory/ralph/<run-id>/` (L4 root, gitignored)
- Personal learnings (cross-project) — those go to L5 user-global, never project-committed

## Allowlist enforcement

The `pre-tool-use-committed-write.py` hook (PreToolUse on Write|Edit) checks every write to `.committed/*` against an allowlist. Writes outside the allowlist are blocked with exit 2. Default patterns ship with the plugin; project extensions live in `.allowlist-extensions.txt` (which is itself allowlisted — bootstrap problem solved).

## Why this design

Two failure modes the design avoids:

1. **Accidental commit of ephemeral state** — without the `.committed/` opt-in pattern, every session would dirty the working tree with run logs, learnings drafts, eval intermediate state. The gitignored default + allowlisted `.committed/` keeps git history clean.
2. **Lost team knowledge** — without ANY versioned memory, the plugin's learnings are per-developer-machine. The `.committed/` subdir lets teams share durable knowledge.

## Maintenance

- Review `conventions.md` quarterly for staleness
- Archive `eval-baselines/` older than 5 release tags (per memory-discipline retention)
- Treat `architecture-decisions/` as immutable ADRs — supersede via new entry, never edit history
