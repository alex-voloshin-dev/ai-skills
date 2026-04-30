# Memory in ai-assets

How the plugin persists information across turns, sessions, and projects.

> Internal design lives in `plugin-design/03-MEMORY-ARCHITECTURE.md`. This doc is the user-facing summary.

## Why memory matters

LLM agents are stateless between turns. Without persistent memory:
- Every workflow re-discovers your project conventions from scratch (wasted tokens)
- Lessons learned in one session don't carry to the next
- Subagent reports vanish when the parent context compacts
- You can't tell what the team agreed on three weeks ago

ai-assets layers six memory tiers so that the right information is available at the right time, without bloating context.

## The 6 layers

| Layer | What | Where | Lifetime |
|---|---|---|---|
| **L0** Cowork host | Anthropic-managed cross-project memory | `~/.../spaces/<id>/memory/` | Out-of-plugin (Cowork manages) |
| **L1** Plugin templates | Read-only knowledge bundled with the plugin | `${CLAUDE_PLUGIN_ROOT}/memory/templates/` | Frozen at plugin install |
| **L2** Project static | `CLAUDE.md`, `AGENTS.md`, `ARCHITECTURE.md`, `marketing/MARKETING.md` | Target repo | Per-repo, owned by repo |
| **L3** Session | Per-session run logs, token meter, RALF iter dirs | `<repo>/.ai-assets-memory/sessions/<id>/` | Until session ends, then summarized to L4 |
| **L4** Project cross-session | Project's persistent learnings, run history, eval baselines | `<repo>/.ai-assets-memory/` | Per-repo, persistent |
| **L5** User-global | Patterns the user wants across ALL projects (opt-in only) | `~/.claude/ai-assets/learnings.md` | Forever, across all projects |

## What goes where

The plugin enforces strict rules per `memory-discipline.md`:

- **L4 / L5 writes go through `memory-curator`** — centralized review, dedupe, schema validation, PII filter
- **PII filter runs on every write** to L3, L4, L5 (regex from `pii-patterns.txt` + project extensions)
- **L5 writes require BOTH `userConfig.user_global_memory_enabled: true` AND the `--global` flag** on `/learnings-write`
- **Per-project paths NEVER written to L5** — L5 is for cross-project patterns only
- **`.committed/` writes are allowlist-validated** — only paths matching `committed-allowlist.txt` patterns are accepted

## How to interact with memory

### Initialize the tree

```bash
/memory-init
```

Creates the `.ai-assets-memory/` skeleton. Idempotent.

### Recall what you've stored

```bash
/memory-recall "authentication"
/memory-recall "React migration" --layer L4
/memory-recall "security patterns" --layer L5 --global
```

Returns matching excerpts wrapped in `<untrusted_content>` envelope (per G1 — memory entries are user-/agent-authored and treated as untrusted by default).

### Capture a learning

```bash
/learnings-write "Postgres text column index ignores trailing whitespace"
/learnings-write "Why we chose gRPC over REST" --global
```

Spawns the `memory-curator` agent to dedupe, PII-filter, and append per `learnings-schema.md` format.

## Retention

| Layer | Default retention | Pruning trigger |
|---|---|---|
| L3 sessions/ | session lifetime | SessionEnd hook archives summary to L4, deletes L3 |
| L3 RALF runs | until oracle pass / kill / budget | Terminal state promotes summary to L4, keeps iter dirs 7d then deletes |
| L4 learnings.md | indefinite | Auto-tag as `[stale]` after 90d unconfirmed; auto-delete after 365d |
| L4 runs/<id>.jsonl | 90 days | Compress >30d, delete >90d unless tagged "keep" |
| L4 errors.log | 30 days | Truncate to last 30d on rotation |
| L4 eval-baselines | last 5 release tags + last 30d | Delete older |
| L5 learnings.md | indefinite | User-driven only — never auto-prune |

## What gets versioned in git

By default, **none of `.ai-assets-memory/` goes to git.** It's session/project-local state.

The exception: `.ai-assets-memory/.committed/` is intentionally tracked for memory the team agrees on:
- `conventions.md` — team-confirmed coding conventions
- `learnings.md` — curated learnings worth sharing
- `architecture-decisions/*.md` — ADRs
- `eval-baselines/*.json` — eval scores per release tag
- `decisions/*.md` — research/spike decisions (always-asked-before-write per Q4)

Everything in `.committed/` is allowlist-validated by the `pre-tool-use-committed-write.py` hook — writes outside the allowlist are blocked.

## Related workflows

- [`/memory-init`](../workflows/ai-assets-init.md) — initial setup (also runs as part of `/ai-assets-init`)
- [`/learnings-write`](../workflows/feature-design.md) — capture a learning (used during any workflow)
- [`/feature-design`](../workflows/feature-design.md) — writes designs to L4 + optionally `.committed/`
- [`/security-audit`](../workflows/security-audit.md) — CRITICAL findings written to `.committed/security/incidents/`

## Privacy and PII

The PII filter runs on every memory write. Default patterns cover emails, phone numbers, AWS/GCP/Azure/Stripe/GitHub tokens, JWTs, PEM private keys, and generic API key shapes. Project-specific patterns can be added at `.ai-assets-memory/.committed/pii-patterns.txt`. Redactions are logged to `.ai-assets-memory/redactions.log` for audit.

If you ever see PII in memory, treat it as a bug — the filter should have caught it. File the redaction trail and consider adding the missed pattern to project extensions.
