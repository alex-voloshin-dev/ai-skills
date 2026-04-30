---
name: context-load
description: Load a per-role slice of project context from CLAUDE.md / AGENTS.md / ARCHITECTURE.md / project memory. Returns Markdown ready to embed in a subagent prompt. Use to keep subagent contexts small and on-topic — db-engineer gets DB sections, ui-ux-designer gets UI/UX sections, etc.
context: fork
argument-hint: "--for <role-name> [--max-tokens N]"
---

# /context-load — Per-Role Context Slice

Extract role-relevant excerpts from project documentation. Trim to a token budget. Wrap in `<untrusted_content>` envelope per G1. Output: paste-ready Markdown for subagent prompt assembly.

## When to use

- Inside an orchestrator about to spawn a subagent — load just the slice that role needs
- During `/feature-design` Wave 1 — feed each agent its targeted context (vs full project dump)
- Before any G7 spawn payload assembly — populates `state_slice.related_artefacts`

Reduces per-agent input tokens vs sending full CLAUDE.md to every subagent.

## Invocation

```
/context-load --for db-engineer
/context-load --for ui-ux-designer --max-tokens 2000
/context-load --for security-engineer --include-memory
```

## Arguments

| Flag | Default | Effect |
|---|---|---|
| `--for <role>` | required | One of the 26 plugin agent names |
| `--max-tokens N` | 2000 | Hard cap on output token count |
| `--include-memory` | off | Also include relevant L4 `learnings.md` excerpts |
| `--include-architecture` | on | Include `ARCHITECTURE.md` if exists |

## Behavior

1. Validate `--for <role>` matches one of `plugin/agents/<name>.md` (else error with list of valid roles).
2. Read source files (G1 wrap each per `untrusted-content-wrapping.md`):
   - `<repo>/CLAUDE.md` — extract sections matching role keywords
   - `<repo>/AGENTS.md` (if exists) — extract role-specific subsection
   - `<repo>/ARCHITECTURE.md` (if exists, `--include-architecture`) — extract role-relevant parts
   - L4 `learnings.md` (if `--include-memory`) — entries tagged with role or with role-domain keywords
3. Role-keyword extraction map (examples):
   - `db-engineer` → sections matching `database`, `schema`, `migration`, `query`, `index`, `transaction`
   - `frontend-engineer` → `frontend`, `UI`, `component`, `routing`, `bundler`, `accessibility`
   - `security-engineer` → `auth`, `authentication`, `authorization`, `secrets`, `encryption`, `vulnerability`, `OWASP`
   - `devops-engineer` → `deploy`, `docker`, `kubernetes`, `helm`, `terraform`, `CI`, `pipeline`
4. Trim to `--max-tokens`:
   - First trim: drop excerpts below relevance threshold
   - Second trim: truncate longest excerpts proportionally
   - Always preserve at least one snippet per source file (unless source had nothing role-relevant)
5. Format output:

```
# Project context for `<role>` (loaded by /context-load, ~N tokens)

## From CLAUDE.md
<wrapped excerpt>

## From AGENTS.md
<wrapped excerpt>

## From ARCHITECTURE.md
<wrapped excerpt>

## From L4 memory (if --include-memory)
<wrapped excerpt>

---
Sources: CLAUDE.md (lines X-Y), AGENTS.md (section "Z"), ARCHITECTURE.md (sections A,B), .ai-assets-memory/learnings.md (3 entries)
```

## Failure modes

- **Invalid role:** error with full list of 26 valid agent names
- **No source files exist:** return "No project context available — skipping context load" (not an error)
- **Token budget too small for any meaningful excerpt:** return shortest possible plus warning that budget was insufficient

## Memory writes

This skill is **read-only** — no memory writes.

## Integration

- **Reads**: `<repo>/CLAUDE.md`, `<repo>/AGENTS.md`, `<repo>/ARCHITECTURE.md`, L4 `learnings.md` (if `--include-memory`)
- **Validates against**: `plugin/agents/*.md` for role name lookup
- **Rules**: `untrusted-content-wrapping` (G1 wrap on every source excerpt)
- **Used by**: orchestrator skills (`/feature-design`, `/develop`, `/team-bugfix`) — feeds `state_slice` of G7 spawn payloads
- **Companion**: `/subagent-spawn` (constructs full G7 payload using context-load output)
