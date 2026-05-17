# Feedback Skill Rubric

## Overview

Evaluates `/feedback` output — the post-hoc plugin session analyzer that mines `~/.claude/projects/<sanitized-cwd>/*.jsonl` for hook errors, subagent failures, abnormal stops, and other anomalies attributable to the ai-skills plugin. Five dimensions × five levels. Pass threshold 3.6 (workflow skill with deterministic worker — output shape matters more than novel reasoning).

## Dimensions

### Dimension 1: Session Sourcing Correctness
Resolves `--project` (or `$PWD`) to the correct `~/.claude/projects/<sanitized-cwd>/` directory, lists `*.jsonl` files, honors `--days` mtime window and `--max-sessions` cap, and reports `sessions_scanned / sessions_total` in the header.

- **Level 1:** Reads from the wrong directory or invents a path; sessions_scanned not reported
- **Level 2:** Correct directory; `--days` window applied wrong (off by one or ignored) or `--max-sessions` ignored
- **Level 3:** Correct directory, correct mtime window, correct cap; header reports counts
- **Level 4:** All of L3 + handles missing directory with a clear error and `--project` suggestion
- **Level 5:** All of L4 + lists "nearby candidate" log directories when the resolved path is empty

### Dimension 2: Anomaly Classification Coverage
The classifier covers all six event kinds from the SKILL body: `hook` (stop_hook_summary.hookErrors), `system` (level=error/warning, tool_use_failure), `assistant` (abnormal stop_reason), `subagent` (task-notification with failed/timeout/cancelled), `skill`, and `command`. Each finding carries `kind`, `source`, `severity`, `signature`, and an excerpt ≤ 400 chars.

- **Level 1:** Only one or two event kinds detected; rest silently dropped
- **Level 2:** Most kinds detected; missing one (typically subagent task-notification failures)
- **Level 3:** All six kinds detected; each finding has the five required attributes
- **Level 4:** All of L3 + plugin_id extracted from path when present; severity assigned per the rule list
- **Level 5:** All of L4 + classifier_version surfaced so report consumers can tell which ruleset produced the findings

### Dimension 3: Grouping and Evidence Quality
Findings group by `(kind, source, normalized-signature)` so recurring failures collapse. Each group lists at most 3 most-recent evidence entries with session_id, timestamp, cli_version, lead-in event, and follow-up event. Secrets are redacted.

- **Level 1:** No grouping; raw event dump
- **Level 2:** Grouping present but no normalization (same error appears 5× with 5 different signatures because of path/line variability)
- **Level 3:** Grouping + signature normalization; evidence cap of 3 honored
- **Level 4:** All of L3 + lead-in + follow-up event summary present per evidence row
- **Level 5:** All of L4 + secret-redaction applied verifiably (no api_key/token/password leaked through the excerpt)

### Dimension 4: Report Template Compliance
Extended report on disk follows the section order: Executive Summary → Scope & Method → Findings (grouped table) → Evidence → Sequence/Causal Chain → Recommendations → Open Questions → Re-run Hints. Brief report on stdout uses the same skeleton, truncated to top 5 groups + top 3 recommendations. Last stdout line is the absolute path to the extended report.

- **Level 1:** Sections missing or out of order; no causal chain; brief and extended diverge in shape
- **Level 2:** Sections present but causal chain skipped; brief misses top-N truncation
- **Level 3:** All eight sections present in both reports; brief truncates correctly
- **Level 4:** All of L3 + last stdout line is the extended-report absolute path with no trailing content
- **Level 5:** All of L4 + verdict (GREEN/YELLOW/RED) computed per the SKILL definition and consistent across both reports

### Dimension 5: Memory and Path Discipline
Writes one JSON-line entry to `.ai-skills-memory/feedback/feedback.log` per run; default report path is `.ai-skills-memory/feedback/feedback-<YYYY-MM-DD>-<HHMM>.md` and re-runs do not overwrite each other; `--out` override respected; falls back to `/tmp/...` on permission denied with a warning; never writes outside repo or `$HOME` unless `--out` says so.

- **Level 1:** No memory write; default path overwrites previous run
- **Level 2:** Memory write present but missing required keys (verdict, report path, findings count)
- **Level 3:** Memory write has all required keys; default path is timestamped so re-runs do not collide
- **Level 4:** All of L3 + `--out` override honored exactly; parent dir created if missing
- **Level 5:** All of L4 + permission-denied fallback to `/tmp/...` with a clear warn line

## Scoring Logic

- **Aggregate:** average of D1–D5
- **Pass threshold:** 3.6
- **Judge model:** Haiku (deterministic — output shape over novelty)

## Anti-Patterns (Auto-Fail)

- Reads or modifies session JSONL files (must be read-only)
- Leaks a secret matching the redaction regex (api_key, secret, token, password, credential) into the report
- Last stdout line is NOT the extended-report absolute path
- Default report path overwrites a previous run (no timestamp in filename)
- Falsely reports verdict=GREEN while at least one error-severity finding exists
- Invents findings the worker did not emit (hallucinated session_id, timestamp, or excerpt)
- Writes the report to an absolute user-machine path baked into the template (must be runtime-substituted)

## Calibration Reference

- **Known-good:** `plugin/eval/calibration/feedback/good/*`
- **Known-bad:** `plugin/eval/calibration/feedback/bad/*`
