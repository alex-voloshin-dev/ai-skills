---
name: feedback
description: Collect and analyze past Claude Code session logs for the ai-assets plugin to surface agent, subagent, skill, command, and hook errors, timeouts, unexpected exits, and other anomalies that point at plugin defects. Defaults to the last 7 days of sessions for the current project. Produces an extended Markdown report on disk plus a brief on-screen summary. Use when reviewing how the plugin behaved across recent runs, after a release to confirm reliability, before filing a plugin bug report, or when planning the next plugin improvement cycle.
context: fork
argument-hint: "[--days N] [--project PATH] [--plugin NAME] [--out PATH] [--severity all|warn|error]"
---

# /feedback — Plugin Session Feedback Analyzer

Mine Claude Code session JSONL transcripts for evidence of how the ai-assets plugin behaved across recent sessions. Produces:

1. An **extended report** saved to disk at a deterministic path.
2. A **brief on-screen report** following the same template skeleton so users can scan it in the terminal.
3. The on-disk path is the last line of the brief so the user can jump to the full document.

Both reports share section headings (Executive Summary → Findings → Evidence → Recommendations). The brief truncates each section; the file holds the full evidence with timestamps, session IDs, and verbatim excerpts.

## When to use

- Post-release reliability check ("did the new hooks misbehave on real sessions?")
- Triage before filing a plugin bug ("show me every place `subagent-depth-guard` exit-2 fired this week")
- Skill quality review ("which user-invocable skills failed silently in the last 7 days?")
- Planning next improvement cycle ("which 3 problems hit me most often?")
- Auditing a specific subagent or hook by name

Not for:

- Live tail of an active session (use the Claude Code transcript pane)
- Project-code bugs unrelated to the plugin (use `/bugfix`)
- Test-suite analysis (use `/qa` / `/eval`)

## Invocation

```text
/feedback                                   # last 7 days, current project, plugin = ai-assets
/feedback --days 14                         # last 14 days
/feedback --project /path/to/other/repo     # analyze a different project's sessions
/feedback --plugin ai-assets                # restrict findings to one plugin (default: ai-assets)
/feedback --severity error                  # only blocking/error-level findings
/feedback --out reports/feedback-2026-05.md # custom output path
```

## Arguments

| Flag | Default | Effect |
|---|---|---|
| `--days N` | `7` | Window of recent sessions to scan (mtime-based). `0` means "all sessions". |
| `--project PATH` | current `$PWD` | Project whose session logs to read. Resolved to `~/.claude/projects/<sanitized-path>/`. |
| `--plugin NAME` | `ai-assets` | Filter findings to events that mention this plugin name in hook paths, skill paths, or system events. `all` disables the filter. |
| `--severity LEVEL` | `warn` | One of `all`, `warn`, `error`. `warn` is the default — includes errors plus non-blocking warnings. |
| `--out PATH` | `.ai-assets-memory/feedback/feedback-<YYYY-MM-DD>-<HHMM>.md` | Override the on-disk report path. Parent dir is created if missing. |
| `--max-sessions N` | `100` | Cap on number of session files parsed (oldest first; newest always included). |

## Behavior

### 1. Resolve the session log directory

Translate `--project` (or `$PWD`) to the Claude Code log path:

```text
~/.claude/projects/<sanitized-cwd>/<session-id>.jsonl
```

`<sanitized-cwd>` is the absolute project path with `/` replaced by `-` and a leading `-`. Example: `/home/u/repo/ai-assets` → `-home-u-repo-ai-assets`. If the directory does not exist, fail with a clear message and suggest `--project`.

### 2. Filter session files by recency

List `*.jsonl` files; keep those with `mtime >= now - days` (or all if `--days 0`). Sort newest first; truncate to `--max-sessions`. Record the resolved window and file count in the report header.

### 3. Stream-parse each session file

Each line is a JSON object. Stream-parse (do not load whole file). For each line, classify:

- `type=system, subtype=stop_hook_summary` with non-empty `hookErrors[]` → **hook error**
- `type=system, subtype=tool_use_failure` or any `type=system` with a `level: error` field → **tool/system error**
- `type=assistant` with `stop_reason` in {`tool_use_error`, `max_tokens`, `refusal`} → **assistant abnormal stop**
- `type=user` with content matching `<task-notification>` and `<status>failed|timeout|cancelled</status>` → **task/subagent failure**
- `type=system` with subtype mentioning `subagent` and `level` in {`warning`, `error`} → **subagent anomaly**
- `type=system` with `permissionMode=plan` toggles that contradict the user request → **permission-mode drift**
- Any line containing `${CLAUDE_PLUGIN_ROOT}` plus an error string → **plugin path/runtime error**

The classifier and event-extraction logic live in `scripts/collect_session_data.py` (see "Worker script" below). Edit the script when new event types appear in Claude Code releases.

### 4. Attribute each finding

For every classified event, attach:

- `sessionId`, `timestamp`, `cwd`, `gitBranch`, `version` (Claude Code version)
- `source`: agent / subagent name, skill name, hook name, or command name (parsed from the event payload)
- `pluginId`: derived from the path (e.g., `ai-assets` if the hook path contains `/plugins/cache/ai-assets/`)
- `severity`: `error` (blocking), `warn` (non-blocking), `info` (anomaly worth noting)
- `excerpt`: ≤ 400-char verbatim slice of the event payload (no full payload to keep the report compact)
- `surrounding_context`: previous and next 1 event in the same session (to show the lead-up and reaction)

### 5. Group findings

Group by:

1. **Source kind** — hook / subagent / skill / command / system
2. **Source identity** — e.g., `subagent-depth-guard.py`, `develop`, `/feedback`
3. **Failure signature** — normalized error string (file path masked, line numbers stripped) so recurring failures collapse into one finding with a count

Within each group, list 3 most-recent occurrences as evidence; collapse the rest into a count.

### 6. Render reports

Render both reports from the shared template in `templates/extended-template.md`:

- **Extended (file):** every group, every evidence excerpt, full recommendations table
- **Brief (stdout):** top 5 groups by occurrence count + top 3 recommendations + path to the extended report

#### 6a. Paired canonical JSON output (v0.3.13+)

Every `/feedback` run also writes a machine-readable counterpart of the Markdown report at the same stem, e.g. `feedback-2026-05-13-0910.json` next to `feedback-2026-05-13-0910.md`. The JSON conforms to `plugin/skills/feedback/output-schema.json` (schema_version `"1"`) and has **full parity** with the MD: every finding present in the Markdown appears in the JSON with the same severity, source kind, identity, signature, count, first/last seen, and up to 3 evidence excerpts (≤ 400 chars each). The JSON also carries `meta.report_md_path` pointing back at the paired MD for traceability.

Invocation contract: call the worker with `--out-json <stem>.json --report-md-path <stem>.md --tool-version <ai-assets@VERSION>`. The worker writes the JSON atomically (`*.tmp` + rename) so a half-written file is never visible to a downstream reader. Schema-validate using the bundled schema (`output-schema.json`) when `jsonschema` is available.

The JSON is the canonical contract for `/plugin-author fix-feedback --from <stem>.json`. Reparsing the Markdown is a degraded fallback only (per `plugin-author/feedback-parser.md`), and downstream consumers MUST prefer the JSON whenever it exists.

Sections in both:

1. **Executive Summary** — verdict (GREEN/YELLOW/RED), window, sessions analyzed, total findings, top failure signature
2. **Scope & Method** — `--days`, project path, plugin filter, file count, classifier version
3. **Findings** — grouped table: source kind | source | signature | count | severity | first/last seen
4. **Evidence** — per-group evidence blocks with timestamps and excerpts
5. **Sequence / Causal Chain** — for the top failure: ordered timeline of related events across sessions to show the lead-up
6. **Recommendations** — table: finding ref | suggested action | owner (skill / hook / agent file) | estimated effort
7. **Open Questions** — anything the data alone cannot answer (needs a human follow-up)

### 7. Memory write

Append one JSON-line summary to `.ai-assets-memory/feedback/feedback.log`:

```json
{"ts": "<iso>", "days": 7, "project": "<path>", "plugin": "ai-assets", "sessions_scanned": 14, "findings": 23, "verdict": "YELLOW", "report": ".ai-assets-memory/feedback/feedback-2026-05-13-0910.md"}
```

### 8. Print the brief

Last line of stdout is always `Extended report: <absolute-path-to-on-disk-report>`. This is the contract the caller relies on.

## Worker script

`scripts/collect_session_data.py` is the deterministic parser. By default it emits the legacy aggregation shape on stdout (`{"meta": ..., "findings": [raw events], "groups": [aggregated]}`) for the Markdown renderer. With `--stdout canonical` it emits the canonical schema (schema_version `"1"`) instead. With `--out-json <path>` it atomically writes the canonical JSON to a file in addition to whatever it streams on stdout. The skill body always passes `--out-json` and `--report-md-path` so the paired `.json` lands next to the `.md` per the parity contract above.

The worker MUST:

- Stream-parse line by line (sessions can be hundreds of MB)
- Skip malformed JSON lines but increment a counter; surface counter in the report header (and in `meta.malformed_lines` of the canonical JSON)
- Mask any value matching `(?i)(api[_-]?key|secret|token|password|credential)[\"'\s:=]+[^\s\"']+` → `<redacted>`
- Be invocable as `python3 plugin/skills/feedback/scripts/collect_session_data.py --days 7 --project <abs-path> --out-json <stem>.json --report-md-path <stem>.md --tool-version 'ai-assets@<ver>'` from the plugin tree

## Templates

- `templates/extended-template.md` — extended on-disk skeleton (used for the saved Markdown document)
- `templates/brief-template.md` — brief on-screen skeleton (≤ 60 lines)

Both files include placeholders the skill substitutes at render time.

## Hard rules

- **Read-only** — never modify session JSONL files
- **Never echo secrets** — apply the redaction regex above before printing or writing
- **Deterministic output path** — when `--out` is not given, use `.ai-assets-memory/feedback/feedback-<YYYY-MM-DD>-<HHMM>.md` so re-runs do not overwrite each other
- **Paired JSON parity** — every MD write MUST be paired with a JSON write at the same stem. If the JSON write fails, surface the error to the user; do not silently leave a MD-only report (downstream `/plugin-author fix-feedback` would fall back to degraded MD parsing)
- **English-only** per repo CLAUDE.md
- **No absolute user-machine paths in templates** — substitute at runtime only
- **Last stdout line is the report path** — never print anything after it
- **Plugin scope only by default** — when `--plugin ai-assets`, exclude events whose `source` is clearly user-code (e.g., bash commands, project test runs that are not invoked by plugin hooks)

## Failure modes

- **Session dir missing:** report the resolved path, list nearby candidates, suggest `--project`
- **Zero sessions in window:** still write a report with verdict `INSUFFICIENT_DATA`; brief is one line + path
- **Malformed JSONL line:** count it, continue; surface counter in report header
- **Permission denied on `.ai-assets-memory/feedback/`:** fall back to `/tmp/feedback-<ts>.md` and warn the user that the canonical path was unreachable
- **Worker crash:** print the worker traceback, exit 1, do NOT print a fake report-path line

## Memory writes

| Layer | When | Shape |
|---|---|---|
| L4 | End of every run | Append one JSON line to `.ai-assets-memory/feedback/feedback.log` — timestamp, window, sessions scanned, finding count, verdict, report path |

## Integration

- **Reads**: `~/.claude/projects/<sanitized-cwd>/*.jsonl`
- **Writes**: paired Markdown + canonical JSON reports at the same stem (e.g. `feedback-2026-05-13-0910.{md,json}`), plus a one-line summary append to `.ai-assets-memory/feedback/feedback.log`
- **Downstream consumer**: `/plugin-author fix-feedback --from <report>.json` ingests the canonical JSON and produces a fix-cycle (one WP per finding, DEV → REVIEW → QA pipeline) — see `plugin/skills/plugin-author/feedback-parser.md` for the consumed shape. Markdown reparse via `--md` is degraded fallback only.
- **Companion**: `/plugin-doctor` (live plugin diagnostic), `/eval` (rubric-based skill quality), `/bugfix` (file a fix once a finding is confirmed)
- **Schema**: `plugin/skills/feedback/output-schema.json` (JSON Schema 2020-12, `schema_version: "1"`). The worker validates against it implicitly by construction; downstream consumers SHOULD validate via `jsonschema` when available.
- **Hooks**: none required; `/feedback` is read-only and runs in the main thread
