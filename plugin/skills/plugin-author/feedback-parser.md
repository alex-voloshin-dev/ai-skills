# feedback-parser.md — `/feedback` JSON contract and finding-to-WP mapping

`/plugin-author fix-feedback --from <path>` reads a `/feedback` output and produces a work-package plan. This document defines (1) the JSON contract `/feedback` MUST emit, (2) the mapping rule from a `finding` to a WP, and (3) the fallback path when only Markdown is available.

## Contract: paired output files

Per project memory `project_feedback_parity_md_json.md`, every `/feedback` run writes two files with full parity:

```text
.ai-assets-memory/feedback/feedback-YYYY-MM-DD-HHMM.md     # existing human-readable
.ai-assets-memory/feedback/feedback-YYYY-MM-DD-HHMM.json   # new machine-readable counterpart
```

Both files MUST list the same `findings` (same set, same severities, same signatures, same counts). The MD is for humans + audit trails; the JSON is consumed by `/plugin-author fix-feedback`. Reparsing the MD with regex is forbidden as the primary path — it is only the degraded fallback.

## JSON schema (target: `plugin/skills/feedback/output-schema.json`)

The `/feedback` worker `scripts/collect_session_data.py` already emits a JSON object on stdout (`{"meta": {...}, "findings": [...], "groups": [...]}` per `feedback/SKILL.md` §Worker script). The contract `/plugin-author` requires is a small superset of that — the worker is the natural author. Required top-level shape:

```jsonc
{
  "schema_version": "1",
  "meta": {
    "ts": "2026-05-13T09:10:00Z",
    "tool_version": "ai-assets@0.3.11",
    "window_days": 7,
    "project_path": "/abs/path/to/project",
    "plugin_filter": "ai-assets",
    "sessions_scanned": 14,
    "malformed_lines": 0,
    "report_md_path": ".ai-assets-memory/feedback/feedback-2026-05-13-0910.md"
  },
  "verdict": "GREEN|YELLOW|RED|INSUFFICIENT_DATA",
  "findings": [
    {
      "finding_id": "f-001",
      "severity": "error|warn|info",
      "source_kind": "hook|subagent|skill|command|system",
      "source_identity": "subagent-depth-guard.py",
      "signature": "normalized error string with paths masked",
      "count": 4,
      "first_seen": "2026-05-08T11:22:00Z",
      "last_seen": "2026-05-12T18:04:00Z",
      "excerpts": [
        {"session_id": "...", "timestamp": "...", "excerpt": "verbatim ≤400 chars"},
        {"session_id": "...", "timestamp": "...", "excerpt": "..."}
      ],
      "asset_hint": "plugin/hooks/scripts/subagent-depth-guard.py",
      "suggested_action": "raise depth cap to 4 for /develop nested teams",
      "owner_role_hint": "python-engineer"
    }
  ],
  "groups": [
    {"by": "source_kind", "name": "hook", "finding_ids": ["f-001", "f-003"]}
  ]
}
```

Required fields per `finding`: `finding_id`, `severity`, `source_kind`, `source_identity`, `signature`, `count`, `first_seen`, `last_seen`, `excerpts[]`. Optional but strongly recommended: `asset_hint`, `suggested_action`, `owner_role_hint`.

If `/feedback` cannot determine `asset_hint`, `plugin-author` infers it from `source_kind` + `source_identity` (see resolver below).

## Finding → asset path resolver

```text
source_kind = "hook"      → plugin/hooks/scripts/<source_identity>
source_kind = "subagent"  → plugin/agents/<source_identity>.md
source_kind = "skill"     → plugin/skills/<source_identity>/SKILL.md
source_kind = "command"   → plugin/skills/<command-name>/SKILL.md  (slash → skill name)
source_kind = "system"    → no direct asset; assign owner_role_hint = "system-architect" and require root-cause investigation in DEV
```

The resolver runs before WP creation. If the resolved path does not exist on disk (e.g., a since-renamed hook), surface the mismatch as an INFO finding and skip the WP — never invent an asset.

## Finding → DEV-role mapping (recap, full table in `asset-to-role-map.md`)

| `asset_hint` pattern | DEV subagent |
|---|---|
| `plugin/skills/*/SKILL.md`, `plugin/agents/*.md`, `plugin/rules/*.md` | `ai-assets:prompt-engineer` |
| `plugin/hooks/scripts/*.py` | `ai-assets:python-engineer` |
| `plugin/schemas/*.json` | `ai-assets:system-architect` |
| `plugin/eval/judge-rubrics/*.md`, `plugin/eval/calibration/*` | `ai-assets:eval-judge` |
| `plugin/eval/config.json`, `plugin/eval/cases/*` | `ai-assets:system-architect` |
| No asset path (system) | `ai-assets:system-architect` |

Honor `owner_role_hint` if set; the mapping above is the default.

## Grouping and WP emission

1. Drop findings with `severity = "info"` unless the user passes `--include-info` (rare; opt-in).
2. Sort findings by severity (`error` > `warn`), then by `count` descending.
3. Group by `(asset_hint, owner_role)` so multiple findings against the same SKILL.md collapse into one WP that fixes them in a single DEV pass.
4. Emit one WP per group with this shape:

```text
WP-N <severity>: <signature short> @ <asset_hint>
  Findings:    [<finding_id> x<count>, ...]
  DEV role:    <ai-assets:role>
  Constraints: <verbatim suggested_action> + "<repair without changing public contract>" + per-asset standard clauses
  Acceptance:  /feedback re-run against the same window shows count drop to 0 for these finding_ids
```

5. Apply wave sizing per `team-protocols/lead-protocol.md` — if N > 6, split into waves of 3–6.

## Acceptance: closing a fix-cycle

A `fix-feedback` run is closed when:

1. Every WP cleared the HEAVY pipeline (DEV → REVIEW → QA + Lead-side post-checks).
2. The Lead writes `.ai-assets-memory/plugin-author/fix-cycles/<feedback-stamp>.json`:

```jsonc
{
  "feedback_report": "feedback-2026-05-13-0910.json",
  "started_at": "...",
  "finished_at": "...",
  "wps": [
    {"wp_id": "WP-1", "finding_ids": ["f-001", "f-003"], "status": "closed", "gate_results": {...}}
  ],
  "unfixed_findings": ["f-005"],   // findings that escalated; require human follow-up
  "follow_ups": [{"finding_id": "f-005", "reason": "max-cycles exceeded", "recommended_next": "..." }]
}
```

3. A re-run of `/feedback` against the same `--days N` window confirms `count: 0` for every closed finding signature. If re-counts > 0, the run is partially closed — keep open finding_ids in `unfixed_findings`.

## Markdown fallback (`--md`)

Used only when the `.json` counterpart is missing or unparseable. Worker: `scripts/parse_feedback_report.py --md <path>`.

Limitations:

- Severity parsed from the Findings table column.
- `signature` is the table cell verbatim — paths are not re-masked, so the asset-hint resolver may miss-match.
- `excerpts` are reconstructed from the Evidence section by H3 anchoring — count loss expected on prose drift.
- Every WP emitted from `--md` is tagged `provenance: md-fallback` in `fix-cycles/<stamp>.json`.

If the `--md` fallback is used more than once, the Lead surfaces a warning in the final summary: "Markdown fallback used. To eliminate parsing risk, ensure `/feedback` emits its paired `.json` (see project memory `feedback-parity-md-json`)."

## Worker script

`scripts/parse_feedback_report.py` is the single binary that:

1. Reads `<path>.json` (default), validates against `feedback/output-schema.json`, returns a normalized `findings[]`.
2. With `--md`, reads `<path>.md` and produces a best-effort `findings[]` flagged with `provenance: md-fallback`.
3. Prints `findings[]` as JSON on stdout for the Lead's WP plan builder.

Run from the plugin root:

```bash
python3 plugin/skills/plugin-author/scripts/parse_feedback_report.py \
  --from .ai-assets-memory/feedback/feedback-2026-05-13-0910.json
```

## Contract status

Live since v0.3.13. The worker `plugin/skills/feedback/scripts/collect_session_data.py` writes the canonical JSON next to the Markdown via `--out-json <stem>.json`; shape is validated against `plugin/skills/feedback/output-schema.json` (`schema_version: "1"`). `/plugin-author fix-feedback` prefers the `.json` companion by default; the `--md` path remains as a degraded fallback for legacy reports that pre-date v0.3.13.
