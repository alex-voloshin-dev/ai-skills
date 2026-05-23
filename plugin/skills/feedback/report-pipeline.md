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
- `type` in {`user`, `queue-operation`, `attachment`, `assistant`} carrying a `<task-notification>` with `<status>failed|timeout|cancelled|canceled|error|killed</status>` → **task/subagent failure** (classifier v2 — see note below)
- `type=system` with subtype mentioning `subagent` and `level` in {`warning`, `error`} → **subagent anomaly**
- `type=system` with `permissionMode=plan` toggles that contradict the user request → **permission-mode drift**
- Any line containing `${CLAUDE_PLUGIN_ROOT}` plus an error string → **plugin path/runtime error**

The classifier and event-extraction logic live in
`scripts/collect_session_data.py` (see "Worker script" below). Edit the script
when new event types appear in Claude Code releases.

### 3a. Task-notification classifier (v2 — R1)

Earlier classifiers matched task-notifications **only** on `type=user` with a
string `message.content`. Real logs deliver the same notification on
`type=queue-operation` and `type=attachment` events too — and on those the
markup is **not** in `message.content` (it is `null`), so a `content`-only match
silently dropped them. v2 therefore (a) searches the **whole serialized event**
when `message.content` is not a usable string, (b) accepts the `queue-operation`
/ `attachment` / `assistant` event types, and (c) adds `killed` (SIGKILL'd
background tasks) and `canceled` to the failure-status set. To avoid inflating
counts when one failure is delivered on several event types, findings are
**deduped per session by `(task-id, status)`** so the count reflects distinct
failures, not raw deliveries.

### 3b. Team-envelope reliability scan (v2 — primary subagent-reliability source)

The dominant `/develop` failure mode — a Path B teammate going **silent-idle
before returning its G7 envelope** — leaves almost no trace in the JSONL
transcript: a truncated assistant turn carries no `max_tokens`/`refusal`/error
`stop_reason`, so the rule above never fires. The transcript is the **wrong
source** for this failure. The ai-skills `team-gate-reconciliation` hook,
however, records every such transition to

```text
<project>/.ai-skills-memory/sessions/<sid>/team-envelopes/<event>-*.json
```

with `teammate_quiesced: true`. The worker scans that directory (within the same
`--days` window; gated on the plugin filter admitting `ai-skills`, since these
envelopes are ai-skills-owned) and emits:

- **Silent-idle** — `TeammateIdle-*.json` / `idle_notification-*.json` with
  `teammate_quiesced: true` → **warn** finding `teammate silent-idle quiesced via
  <event> (bus_state_absent=<bool>)`. Individually recoverable (the Lead re-sends
  r2), so it is `warn`, not `error` — but the **count** is the signal, and
  `bus_state_absent=true` (bus dead too) groups separately as the worse case.
- **Interrupted writes** — an orphan `*.json.tmp` with **no** sibling final →
  **error** (`interrupted envelope write: orphan .tmp, no final`). When the
  final `.json` IS present the `.tmp` is a recovered/cosmetic leftover →
  **info** (filtered at the default warn floor, so recovered orphans never
  inflate the report — they are not data loss).

`meta.team_envelopes_scanned` records how many envelopes were inspected. Clean
transitions (`TaskCompleted`, `shutdown_response`, G7 finals) are counted as
scanned context but are not findings.

### 3c. Verdict softening for transient upstream-API errors (v2 — R3)

A **single-occurrence** transient upstream-API error (e.g. Anthropic HTTP 529
"overloaded", 429 rate-limit) is retried by the runtime and is not a plugin
defect, so it must not force a RED verdict on its own. The verdict treats such a
finding (`count == 1`, source/signature matching `overloaded` / `api_error` /
`rate limit` / `service unavailable` / `http <n>`) as **warn for the verdict
only** — the finding itself keeps `severity: error` for traceability. A
**recurring** upstream error (`count ≥ 2`) still escalates to RED.

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
