# Learnings Entry Schema (L4 + L5)

> Plugin-shipped template. Read by `memory-curator` agent and `/learnings-write` skill. Documents the canonical format for entries appended to `.ai-skills-memory/learnings.md` (L4) or `~/.claude/ai-skills/learnings.md` (L5).

## Required Fields (from memory-validation.md)

Every learning entry MUST record:

| Field | Type | Notes |
|---|---|---|
| `name` (heading) | H2 string | Entity name — short, specific, search-friendly |
| `Type` | enum | `convention` \| `gotcha` \| `preference` \| `architecture-fact` \| `decision` |
| `Source` | string | `session-<run-id>` OR `<agent-name>` OR `user-manual` OR file path |
| `Confidence` | float [0.0–1.0] | How sure we are. <0.5 = treat as hypothesis |
| `Created` | ISO8601 | First time this entry was written |
| `Last confirmed` | ISO8601 | Last time observed/validated |
| `Scope` | enum | `project` (L4) OR `global` (L5) |

## Body

Free-form Markdown. Aim for 3-15 lines. Include:
- **What** the learning is (2-3 sentences)
- **Why** it matters (1-2 sentences) — context that makes the rule judgeable
- **How to apply** — when this kicks in
- **References** to files/lines/commits if applicable

## Template

```markdown
## <Entity name — what is this learning about>

**Type:** convention | gotcha | preference | architecture-fact | decision
**Source:** session-<run-id> | <agent-name> | user-manual
**Confidence:** <0.0-1.0>
**Created:** <ISO8601>
**Last confirmed:** <ISO8601>
**Scope:** project | global

<Body: what the learning is, why it matters, how to apply, file/line refs>
```

## Example (valid L4 entry)

```markdown
## Async migration files broke when DEFAULT was set without nullability

**Type:** gotcha
**Source:** session-20260424-xyz789
**Confidence:** 0.95
**Created:** 2026-04-24T14:30:00Z
**Last confirmed:** 2026-04-24T14:30:00Z
**Scope:** project

In Alembic migrations, adding a NOT NULL column with a Python-side default (server_default=None)
caused production rollout to fail when run against the 50M-row users table — the backfill needed
explicit server_default for the default to be applied at SQL level, not Python ORM level.

**How to apply:** every Alembic migration adding a NOT NULL column to a non-empty table MUST
specify `server_default=` (raw SQL value), NOT `default=` (Python-side). Test in shadow DB
before prod.

**Files:** alembic/versions/0042_add_user_email_verified.py L23
```

## Example (INVALID L5 entry — would be blocked)

```markdown
## acme-corp auth flow gotcha

**Source:** session in /home/user/dev/acme-corp-app/
**Scope:** global

The magic_token field in AuthRequest must be prefixed with "ac_"...
```

Rejected because:
- Contains specific project name in heading (L5 must be cross-project applicable)
- Contains project path in Source field
- Contains project-specific identifier (`magic_token`, `AuthRequest`, `ac_`)

These belong in **L4 of the project that owns them**, not in cross-project L5.

## Conflict resolution

When a new entry's name matches an existing entry, `memory-curator` agent applies the conflict resolution algorithm from `memory-validation.md`:

1. user-stated > inferred (unless user later corrects)
2. higher confidence wins when gap is material (≥0.3 confidence delta)
3. more recently confirmed wins
4. on ambiguity: ask user, do not silently merge

Conflict resolution writes a log line to `.ai-skills-memory/redactions.log` with `winner_id`, `loser_id`, `reason`, `timestamp`, `trace_id`.

## Retention

- L4 entries auto-tagged `[stale]` if `Last confirmed` >90 days old
- L4 entries auto-deleted if `Last confirmed` >365 days old
- L5 entries: never auto-pruned (user-driven only)

## PII filter

Every write through `memory-curator` agent passes through `apply_pii_filter()` from `_lib.py`. PII matches replaced with `[REDACTED:<pattern-name>]`. Audit log to `.ai-skills-memory/redactions.log`.
