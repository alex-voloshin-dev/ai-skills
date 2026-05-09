# `.ai-assets-memory/.committed/` — versioned project memory

> Seeded by `/ai-assets-init`. Edit freely.

This directory is the **opt-in versioned** part of the `ai-assets` plugin's project memory (L4 in the 6-layer model). Everything else under `.ai-assets-memory/` is gitignored — only paths matching the allowlist in `.allowlist-extensions.txt` (plus the plugin defaults) are permitted here, and they ARE committed to git so the team shares them.

## When to write here

Put content here that the **whole team** should see and version-control:

- `conventions.md` — team-confirmed coding/architectural conventions
- `architecture-decisions/<date>-<title>.md` — ADRs with full context, options, decision, consequences
- `eval-baselines/<release-tag>.json` — eval scorecards worth tracking across releases
- `decisions/<date>-<topic>.md` — `/spike` go/no-go outcomes the team accepted (ALWAYS-ASK before write here)
- `releases/<version>/changes.md` — release notes per `/develop` PR open
- `pii-patterns.txt` — project-specific PII regex patterns (extends plugin defaults)
- `.allowlist-extensions.txt` — additional file patterns to allowlist

## When NOT to write here

- Ephemeral session state — goes to `.ai-assets-memory/sessions/<run-id>/` (L3, gitignored)
- Subagent reports — `.ai-assets-memory/sessions/<run-id>/subagent-reports/` (L3)
- Tool failure logs — `.ai-assets-memory/errors.log` (L4 root, gitignored)
- Run-specific RALF iterations — `.ai-assets-memory/ralph/<run-id>/` (L4 root, gitignored)
- Personal learnings (cross-project) — those go to L5 user-global, never project-committed

## Allowlist enforcement

The `pre-tool-use-committed-write.py` hook (PreToolUse on Write|Edit) checks every write to `.committed/*` against an allowlist. Writes outside the allowlist are blocked with exit 2. Default patterns ship with the plugin; project extensions live in `.allowlist-extensions.txt` (which is itself allowlisted — bootstrap problem solved).

## Maintenance

- Review `conventions.md` quarterly for staleness
- Archive `eval-baselines/` older than 5 release tags
- Treat `architecture-decisions/` as immutable ADRs — supersede via new entry, never edit history
