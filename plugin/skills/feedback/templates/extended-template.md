# Plugin Feedback Report

> Generated: `{{generated_at}}` · Plugin: `{{plugin_filter}}` · Window: last `{{window_days}}` day(s)
> Project: `{{project_path}}`
> Log directory: `{{log_dir}}`

## 1. Executive Summary

- Verdict: **{{verdict}}**   (GREEN = no error-level findings · YELLOW = ≥1 error-level finding or recurring warn · RED = blocking or recurring error in ≥3 sessions)
- Sessions in window: **{{sessions_scanned}} / {{sessions_total}}**
- Lines parsed: **{{lines_parsed}}** (malformed skipped: {{lines_skipped_malformed}})
- Total findings: **{{findings_total}}** across **{{groups_total}}** distinct failure signatures
- Top failure signature: `{{top_signature}}` ({{top_signature_count}}×, severity `{{top_signature_severity}}`)
- Classifier version: `{{classifier_version}}`

If verdict is GREEN, the rest of this document is empty by design — skim §7 for any open questions.

## 2. Scope and Method

| Field | Value |
|---|---|
| Project path | `{{project_path}}` |
| Plugin filter | `{{plugin_filter}}` |
| Severity floor | `{{severity_floor}}` |
| Days scanned | `{{window_days}}` |
| Max sessions cap | `{{max_sessions}}` |
| Sessions actually scanned | `{{sessions_scanned}}` |
| Classifier event types | `hook`, `subagent`, `skill`, `command`, `assistant`, `system` |
| Redaction applied | API keys, secrets, tokens, passwords, credentials → `<redacted>` |

Method: the worker `scripts/collect_session_data.py` stream-parses every JSONL line, classifies events that match the failure rules in `SKILL.md` §3, attributes them, and groups by `(kind, source, normalized-signature)`. See SKILL body for the full rule list.

## 3. Findings (grouped)

| # | Severity | Kind | Source | Signature | Count | First seen | Last seen |
|---|---|---|---|---|---:|---|---|
{{findings_table_rows}}

Severity legend: `error` = blocking or non-zero exit · `warn` = non-blocking anomaly · `info` = observation worth noting.

## 4. Evidence

Per-group evidence (up to 3 most-recent occurrences). Excerpts are verbatim slices of the originating event, truncated to 400 characters and redacted.

{{evidence_blocks}}

Each evidence block follows this shape:

```text
### [{{finding_id}}] {{kind}} :: {{source}} :: {{signature}}

- session: {{session_id}}
- timestamp: {{ts}}
- cwd: {{cwd}}
- git branch: {{git_branch}}
- cli version: {{cli_version}}
- plugin id: {{plugin_id}}
- lead-in event: {{lead_in}}
- follow-up event: {{follow_up}}

Excerpt:

    {{excerpt}}
```

## 5. Sequence / Causal Chain (top finding)

Ordered timeline of related events across sessions for the highest-impact group. Use this to see what triggered the failure and what the system did next.

{{causal_chain}}

If only one occurrence was recorded, the chain shows the single session's surrounding context (prev event → finding → next event).

## 6. Recommendations

| # | Finding ref | Suggested action | Owner (file path) | Effort |
|---|---|---|---|---|
{{recommendations_table_rows}}

Owner paths are relative to repo root and point at the most likely fix site (skill body, hook script, agent file, or rubric). Effort is `S` (≤1h), `M` (≤4h), or `L` (>4h, design needed).

## 7. Open Questions

Items the session data alone cannot resolve. Each should become a follow-up task or be closed after a human investigation.

{{open_questions_list}}

## 8. Re-run Hints

To reproduce or refine this analysis:

```text
/feedback --days {{window_days}} --project {{project_path}} --plugin {{plugin_filter}} --severity {{severity_floor}}
```

To inspect one finding in raw form:

```text
jq -c 'select(.sessionId == "<session-id>")' {{log_dir}}/<session-id>.jsonl | sed -n '<line>p'
```

---

_Saved to:_ `{{report_path}}`
