# /feedback — Parse · Attribute · Group · Render Pipeline

Detailed mechanics for `/feedback` Behavior steps 3–6 and the worker-script
contract. `SKILL.md` keeps the step list and the report-section output
contract; this file keeps the executable detail. **Read this file and apply
steps 3–6 + the worker contract verbatim** when running `/feedback` — these
rules are mandatory, not optional reference. Behavior is identical to the
prior single-file form.

## 3. Stream-parse each session file

Each line is a JSON object. Stream-parse (do not load whole file). For each
line, classify:

- `type=system, subtype=stop_hook_summary` with non-empty `hookErrors[]` → **hook error**
- `type=system, subtype=tool_use_failure` or any `type=system` with a `level: error` field → **tool/system error**
- `type=assistant` with `stop_reason` in {`tool_use_error`, `max_tokens`, `refusal`} → **assistant abnormal stop**
- `type=user` with content matching `<task-notification>` and `<status>failed|timeout|cancelled</status>` → **task/subagent failure**
- `type=system` with subtype mentioning `subagent` and `level` in {`warning`, `error`} → **subagent anomaly**
- `type=system` with `permissionMode=plan` toggles that contradict the user request → **permission-mode drift**
- Any line containing `${CLAUDE_PLUGIN_ROOT}` plus an error string → **plugin path/runtime error**

The classifier and event-extraction logic live in
`scripts/collect_session_data.py` (see "Worker script" below). Edit the script
when new event types appear in Claude Code releases.

## 4. Attribute each finding

For every classified event, attach:

- `sessionId`, `timestamp`, `cwd`, `gitBranch`, `version` (Claude Code version)
- `source`: agent / subagent name, skill name, hook name, or command name (parsed from the event payload)
- `pluginId`: derived from the path (e.g., `ai-skills` if the hook path contains `/plugins/cache/ai-skills/`)
- `severity`: `error` (blocking), `warn` (non-blocking), `info` (anomaly worth noting)
- `excerpt`: ≤ 400-char verbatim slice of the event payload (no full payload to keep the report compact)
- `surrounding_context`: previous and next 1 event in the same session (to show the lead-up and reaction)

## 5. Group findings

Group by:

1. **Source kind** — hook / subagent / skill / command / system
2. **Source identity** — e.g., `subagent-depth-guard.py`, `develop`, `/feedback`
3. **Failure signature** — normalized error string (file path masked, line numbers stripped) so recurring failures collapse into one finding with a count

Within each group, list 3 most-recent occurrences as evidence; collapse the
rest into a count.

## 6. Render reports

Render both reports from the shared template in
`templates/extended-template.md`:

- **Extended (file):** every group, every evidence excerpt, full recommendations table
- **Brief (stdout):** top 5 groups by occurrence count + top 3 recommendations + path to the extended report

### 6a. Paired canonical JSON output (v0.3.13+)

Every `/feedback` run also writes a machine-readable counterpart of the
Markdown report at the same stem, e.g. `feedback-2026-05-13-0910.json` next to
`feedback-2026-05-13-0910.md`. The JSON conforms to
`plugin/skills/feedback/output-schema.json` (schema_version `"1"`) and has
**full parity** with the MD: every finding present in the Markdown appears in
the JSON with the same severity, source kind, identity, signature, count,
first/last seen, and up to 3 evidence excerpts (≤ 400 chars each). The JSON
also carries `meta.report_md_path` pointing back at the paired MD for
traceability.

Invocation contract: call the worker with `--out-json <stem>.json
--report-md-path <stem>.md --tool-version <ai-skills@VERSION>`. The worker
writes the JSON atomically (`*.tmp` + rename) so a half-written file is never
visible to a downstream reader. Schema-validate using the bundled schema
(`output-schema.json`) when `jsonschema` is available.

The JSON is the canonical contract for `/plugin-author fix-feedback --from
<stem>.json`. Reparsing the Markdown is a degraded fallback only (per
`plugin-author/feedback-parser.md`), and downstream consumers MUST prefer the
JSON whenever it exists.

## Worker script

`scripts/collect_session_data.py` is the deterministic parser. By default it
emits the legacy aggregation shape on stdout (`{"meta": ..., "findings": [raw
events], "groups": [aggregated]}`) for the Markdown renderer. With `--stdout
canonical` it emits the canonical schema (schema_version `"1"`) instead. With
`--out-json <path>` it atomically writes the canonical JSON to a file in
addition to whatever it streams on stdout. The skill body always passes
`--out-json` and `--report-md-path` so the paired `.json` lands next to the
`.md` per the parity contract above.

The worker MUST:

- Stream-parse line by line (sessions can be hundreds of MB)
- Skip malformed JSON lines but increment a counter; surface counter in the report header (and in `meta.malformed_lines` of the canonical JSON)
- Mask any value matching `(?i)(api[_-]?key|secret|token|password|credential)[\"'\s:=]+[^\s\"']+` → `<redacted>`
- Be invocable as `python3 plugin/skills/feedback/scripts/collect_session_data.py --days 7 --project <abs-path> --out-json <stem>.json --report-md-path <stem>.md --tool-version 'ai-skills@<ver>'` from the plugin tree
