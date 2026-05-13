# Plugin Feedback — Brief

- Verdict: **{{verdict}}** · Window: {{window_days}}d · Sessions: {{sessions_scanned}}/{{sessions_total}} · Findings: {{findings_total}} ({{groups_total}} signatures)
- Plugin: `{{plugin_filter}}` · Project: `{{project_path}}`

## Top 5 failure signatures

| # | Sev | Kind | Source | Signature | Count |
|---|---|---|---|---|---:|
{{top_groups_table}}

## Top 3 recommendations

{{top_recommendations_list}}

## What to do next

- For full evidence + sequence chains + per-finding context, open the extended report.
- To narrow scope: `/feedback --plugin <name> --severity error --days <n>`.
- To dive into a specific session: `~/.claude/projects/{{log_dir_basename}}/<session-id>.jsonl`.

---

_Saved to:_ `{{report_path}}`
