# Hooks — wiring reference

This directory wires the ai-skills plugin into Claude Code's hook lifecycle. The wiring lives in `hooks.json` (pure standard JSON, no comments). This file is the human-readable companion that explains **what** each hook does, **why** it exists, and **what order** matters when multiple hooks fire on the same event.

> `hooks.json` is pure standard JSON with no comments. All wiring documentation lives in this file and is referenced from the manifest implicitly via co-location.

## At a glance

| Count | What |
|---|---|
| 18 | hook scripts in `hooks/scripts/` (excluding `_lib.py`) |
| 13 | distinct lifecycle events wired |
| 1 | shared helper module — `hooks/scripts/_lib.py` |
| 1 | PII pattern file — `hooks/scripts/pii-patterns.txt` |

The 13 lifecycle events: `SessionStart`, `InstructionsLoaded`, `PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `StopFailure`, `SubagentStart`, `SubagentStop`, `TaskCreated`, `TaskCompleted`, `Stop`, `PreCompact`, `SessionEnd`.

Provenance: 4 carried hooks + 12 new hooks (including the `.committed/` allowlist enforcement `pre-tool-use-committed-write`) + `ralph-iter-meter.py` (v0.1.6) + `subagent-depth-guard.py` (v0.1.7) = 18 total.

## Per-event wiring

### SessionStart
- `session-start-context.py` — read up to 8 KB of CLAUDE.md / AGENTS.md / ARCHITECTURE.md / marketing/MARKETING.md, PII-filter, wrap in `<untrusted_content>` envelope (G1), inject as session context. Initialize session token meter at `.ai-skills-memory/sessions/<sid>/token-meter.json`. Detect locale.

### InstructionsLoaded
- `instructions-loaded-augment.py` — append L4 `.committed/conventions.md` to the loaded instructions when present.

### PreToolUse — matcher `Bash`
- `block-dangerous-commands.py` — block destructive shell commands (`rm -rf /`, `curl … | sh`, etc.). Exit 2 on block.

### PreToolUse — matcher `Write|Edit`
- `block-secrets-in-code.py` — block writes that contain secrets matching `pii-patterns.txt`. Exit 2 on block.
- `pre-tool-use-committed-write.py` — enforce the `.committed/` allowlist. Writes outside allowlisted paths are blocked. Exit 2 on block.

### PreToolUse — matcher `Read`
- `block-sensitive-files.py` — block reads of `.env`, `.ssh/`, `.aws/`, credentials files. Exit 2 on block.

### PostToolUse — matcher `.*`
- `log-actions.py` — append a structured audit line to `.ai-skills-memory/agent-actions.log` for every tool call. PII-filter is applied before persistence. Rotates at 10 MB.

### PostToolUse — matcher `Read|Bash`
**Order matters here:** the two hooks fire as a fixed pair, in this order.

1. `tool-output-wrap.py` (G1) — wrap tool stdout in `<untrusted_content>` envelope, emit a wrap marker.
2. `tool-output-normalize.py` (G2) — read the wrap marker (this hook asserts the marker is present, which makes the order self-enforcing), extract envelope metadata, update `injected_tokens_from_tools` in the session token meter. Stops at metadata today; the Haiku-summarize step is deferred to a later hardening pass.

If `tool-output-wrap.py` did not run first, `tool-output-normalize.py` logs a wrap-marker-missing error and proceeds (fail-open).

### PostToolUseFailure
- `tool-failure-log.py` — append the failure to `.ai-skills-memory/errors.log`.

### StopFailure
- `tool-failure-log.py` — same script reused; logs Stop-event failures.

### SubagentStart
- `subagent-start-budget.py` — enforce subagent-isolation rules; check that the spawn payload conforms to `schemas/spawn-payload.schema.json`; charge against session token meter.

### SubagentStop
- `subagent-stop-learnings.py` — when `userConfig.subagent_learnings_enabled` is true, capture the subagent's structured return for memory-curator review. Validates against `schemas/return-contract.schema.json`. Updates session token meter.

### TaskCreated
- `task-event-log.py` — append task-created event to `.ai-skills-memory/sessions/<sid>/runs.jsonl`.

### TaskCompleted
- `task-event-log.py` — same script reused; appends task-completed event.

### Stop
- `ralph-stop.py` — RALF iteration controller. If `.ai-skills-memory/ralph/<run-id>/active.lock` exists:
  - Runs the oracle (`oracle-pass` SUCCESS marker + `same-error-repeats:N`).
  - Checks per-workflow caps (`max_iterations` from `config.json`).
  - Checks session-aggregate caps from `CLAUDE_USER_CONFIG_ralph_session_max_iter`, `CLAUDE_USER_CONFIG_ralph_session_token_budget`, and `CLAUDE_USER_CONFIG_ralph_session_time_cap_minutes`. Compares against the session meter (`ralf_iter_total`, `ralf_tokens_total`, elapsed minutes from `ralf_started_at`).
  - On terminal state → writes `budget.json`, releases the lock, allows Stop (exit 0).
  - Otherwise → writes the `iter-NNN/prompt.md` continuation and blocks Stop (exit 2 with re-injection prompt).
  - Never blocks Stop because of an internal hook bug (`__main__` wraps `main()` and exits 0 on exception).

### PreCompact
- `pre-compact-memory-flush.py` — invoke memory-curator to flush session-resident learnings to L4 `learnings.md` before context compaction discards them.

### SessionEnd
- `session-end-finalize.py` — finalize session — archive `runs.jsonl`, append RALF totals to `ralf-history.jsonl`, log final token meter.

## Shared helper — `_lib.py`

All 18 hook scripts import `_lib`. Public API:

- `read_stdin_json() -> dict` — read and parse the hook event payload from stdin.
- `normalize_hook_input(data) -> dict` — bridge legacy `agent_action_name` and modern `tool_name` shapes.
- `apply_pii_filter(text) -> (redacted, count)` — apply patterns from `pii-patterns.txt`.
- `wrap_untrusted(content, source) -> str` — produce a canonical `<untrusted_content>` envelope.
- `emit_wrap_marker()` / `read_wrap_marker(stderr)` — wrap-marker for the G1/G2 self-enforcing order.
- `read_token_meter(session_dir) -> dict` / `update_token_meter(session_dir, delta) -> dict` — atomic-ish meter increments.
- `log_to(filename, entry, root=None)` — append-JSONL to `.ai-skills-memory/<filename>`.
- `iso_now() -> str` — UTC ISO-8601 timestamp helper.
- `block(reason)` — exit 2 with reason on stderr.
- `allow()` — exit 0.
- `memory_root() -> Path` — `.ai-skills-memory/` under cwd.

## Failure-recovery rule

Every hook script's `__main__` wraps `main()` in a `try/except Exception`, logs to `hook-errors.log`, and `sys.exit(0)`. A buggy hook never blocks all tool use. This is contractual per `rules/failure-recovery.md`.

## Permission ordering

Per Anthropic's documented order: PreToolUse Hook → Deny Rules → Allow Rules → Ask Rules → Permission Mode → canUseTool → PostToolUse Hook. Plugin hooks are the FIRST authority on PreToolUse and the LAST observer on PostToolUse.

## Testing the wiring

There is no `claude plugin validate` CLI in Claude Code as of 2026-04. Use the local validator + install-time check instead:

```bash
# Local validator (pure Python, no Claude Code needed) — checks JSON/Python/bash
# syntax, manifest fields, structural counts, hook _lib imports, hooks.json paths
python plugin/dev/validate.py

# Install into Claude Code as a local marketplace, then install the plugin —
# the install path is the de-facto manifest schema check
#   /plugin marketplace add C:\Users\avav2\dev\code\ai-skills\plugin
#   /plugin install ai-skills

# Once installed, tail the audit log to confirm log-actions.py is firing
tail -f .ai-skills-memory/agent-actions.log

# Tail errors.log to confirm hook errors are non-fatal (fail-open contract)
tail -f .ai-skills-memory/hook-errors.log
```

## Adding a new hook

1. Drop the script into `hooks/scripts/<name>.py`.
2. Import `_lib` at the top: `sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import _lib`.
3. Use `_lib.read_stdin_json()`, `_lib.normalize_hook_input()`, `_lib.allow()` / `_lib.block()`.
4. Wrap `main()` in `__main__` exception handler that calls `_lib.log_to("hook-errors.log", ...)` + `sys.exit(0)`.
5. Wire the script into the appropriate event in `hooks.json`.
6. Update this README's per-event section.
7. Update the at-a-glance counter at the top of this file and in the root `plugin/README.md`.
