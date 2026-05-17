---
description: Memory layer write rules per skill, PII filter mandatory on every write, conflict resolution, retention policy. Applies whenever writing to .ai-skills-memory/ (project L4), ~/.claude/ai-skills/ (user-global L5), or session L3 dirs. Activates before any persistent memory write.
---

# Memory Discipline

Rules for what gets written to which memory layer, when, and how. Pairs with `memory-validation.md` (general validation) and the 6-layer memory architecture from `plugin-design/03-MEMORY-ARCHITECTURE.md`.

## 6-Layer Model Recap

| Layer | Path | Writer | Lifetime |
|---|---|---|---|
| L0 Cowork host | `~/.../spaces/<id>/memory/` | Cowork only | Out-of-plugin; plugin NEVER writes |
| L1 Plugin templates | `${CLAUDE_PLUGIN_ROOT}/memory/templates/` | Plugin author at build time | Read-only at runtime |
| L2 Project static | `<repo>/CLAUDE.md`, `AGENTS.md`, `ARCHITECTURE.md` | Repo maintainer | Per-repo, owned by repo |
| L3 Session | `<repo>/.ai-skills-memory/sessions/<run-id>/` | Hooks + skills + subagents | Until session ends, then summarized to L4 |
| L4 Project cross-session | `<repo>/.ai-skills-memory/` (gitignored; opt-in `.committed/` for versioned) | Hooks + skills + memory-curator | Per-repo, persistent |
| L5 User-global | `~/.claude/ai-skills/learnings.md` | memory-curator (opt-in only) | Forever, across all projects |

## Hard Rules

1. **L4/L5 writes go through `memory-curator` agent** — centralized review, dedup, schema validation. No skill writes to learnings.md directly; spawn memory-curator with intent in spawn payload.
2. **PII filter runs on every write** to L3, L4, L5. Pattern file at `${CLAUDE_PLUGIN_ROOT}/hooks/scripts/pii-patterns.txt`. Project extension at `.ai-skills-memory/.committed/pii-patterns.txt`. On match: replace with `[REDACTED:<pattern-name>]`. Audit log to `.ai-skills-memory/redactions.log`.
3. **L5 writes require explicit user opt-in**: `userConfig.user_global_memory_enabled: true` AND `--global` flag on `/learnings-write`. Both required.
4. **Per-project paths NEVER written to L5.** L5 is for cross-project patterns only. L5 entries containing `/path/to/repo/`, `src/`, project-specific names = automatic block.
5. **Secrets NEVER written to any layer.** PII filter is defense-in-depth; primary discipline is "do not generate secrets in subagent outputs that get written to memory."
6. **`.ai-skills-memory/.committed/` writes are schema-validated** against allowlist patterns at `${CLAUDE_PLUGIN_ROOT}/memory/templates/committed-allowlist.txt`. Hook `pre-tool-use-committed-write.py` enforces.

## Write Rules Per Skill / Hook

| Source | Layer | Event | Shape |
|---|---|---|---|
| `session-start-context.py` | L3 | SessionStart | metadata.json, locale.txt, token-meter.json |
| `instructions-loaded-augment.py` | (read only) | InstructionsLoaded | reads L4 `.committed/conventions.md` |
| `pre-compact-memory-flush.py` | L4 | PreCompact | learnings.md (append, via memory-curator subagent) |
| `session-end-finalize.py` | L4 | SessionEnd | runs/<id>.jsonl (archive), ralf-history.jsonl (append) |
| `subagent-start-budget.py` | (read only) | SubagentStart | reads L3 token-meter.json |
| `subagent-stop-learnings.py` | L3 (opt-in) | SubagentStop | subagent-reports/<name>-<id>.md |
| `task-event-log.py` | L3 | TaskCreated, TaskCompleted | sessions/<id>/runs.jsonl |
| `tool-failure-log.py` | L4 | PostToolUseFailure, StopFailure | errors.log |
| `log-actions.py` (B2 carried, refactored alpha.15 MED-A) | L4 | PostToolUse(.*) | `.ai-skills-memory/agent-actions.log` (audit log of all tool calls). PII filter applied via `_lib.apply_pii_filter()` before persistence. Audit log remains L4-tier sensitivity (PII filter is best-effort, not exhaustive) |
| `pre-tool-use-committed-write.py` (Round 8 CRIT-1) | (no write — guards writes) | PreToolUse(Write\|Edit) | enforces committed-allowlist.txt against `.committed/` paths; blocks unauthorized writes with exit 2 |
| `ralph-stop.py` | L4 | Stop | ralph/<run-id>/iter-NNN/* |
| `tool-output-wrap.py` | (no write — wraps stdout) | PostToolUse | applies G1 envelope |
| `tool-output-normalize.py` | (no write — wraps + summarizes stdout) | PostToolUse | extends G1 envelope with `injected_tokens` |
| `memory-curator` agent | L4 (default) / L5 (opt-in) | Triggered by Stop, SubagentStop, PreCompact, manual | learnings.md curated entries with provenance |
| `/learnings-write` skill | L4 (default) / L5 (`--global`) | User-invoked | learnings.md append |
| `/ai-skills-init` skill | L4 | First-time init in target repo | seeds L1 templates into target repo's L4 root |

## Conflict Resolution (extends `memory-validation.md`)

```text
On conflict between memory entries about the same entity:
1. user-stated > inferred (unless explicitly superseded by user)
2. higher confidence wins when gap is material (≥0.3 confidence delta)
3. more recently confirmed (last_confirmed_at) wins
4. on ambiguity, ask user; do not silently merge

Inter-layer conflicts:
- L0 (Cowork) vs L4: trust the more recently confirmed; if both same age, trust L4 (plugin-managed)
- L4 vs L5: trust L4 (project-specific overrides global)
- L3 vs L4: L3 is in-flight, do not promote until SessionEnd
- Stale > 30d in L4: re-validate before acting on it; flag with [stale: 2026-MM-DD] marker
```

## Retention

| Layer | Default retention | Pruning trigger | Pruning action |
|---|---|---|---|
| L3 sessions/ | session lifetime | SessionEnd hook | Summarize and archive to L4 runs/, delete sessions/<id>/ |
| L3 ralph runs in progress | until oracle pass / kill / budget | RALF terminal state | Promote summary to L4 ralf-history.jsonl, keep iter dirs 7 days then delete |
| L4 learnings.md | indefinite | manual or memory-curator | Auto-tag entries unconfirmed >90d as [stale]; auto-delete entries unconfirmed >365d |
| L4 runs/<id>.jsonl | 90 days | session-end-finalize.py | Compress >30d old; delete >90d unless tagged "keep" |
| L4 errors.log | 30 days | session-end-finalize.py | Truncate to last 30d on rotation |
| L4 eval-baselines | last 5 release tags + last 30d | release tag or `/eval --baseline` | Delete older |
| L5 learnings.md | indefinite | manual | User-driven only — never auto-prune |

## Pairing

- `memory-validation.md` — general memory entry schema (required fields, conflict ordering)
- `untrusted-content-wrapping.md` — every L2/L4 read MUST be wrapped before injection
- `subagent-isolation.md` — subagent return contracts feed memory-curator inputs
