#!/usr/bin/env python3
"""Recent-errors dashboard for `/plugin-doctor --show-recent-errors` (audit
§WP-4.2).

Reads `.ai-skills-memory/errors.log` from the current project and prints a
top-N summary of hooks ranked by ERROR + WARNING count over the last N days.

Usage:
    python3 plugin/dev/recent-errors.py [--days 7] [--top 5] [--json]

The errors.log format is one JSON object per line, written by plugin hooks via
`_lib.log_to('errors.log', {...})`. Expected fields per entry: `ts`, `severity`
(WARNING | ERROR | INFO), `hook` (script basename), `issue`. Extra fields are
preserved in the report's `recent_examples` array (one per hook).

Fail-open: any IO / parse failure produces a "no data" report with exit 0.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone


def _parse_ts(raw: str | None) -> datetime | None:
    if not raw:
        return None
    try:
        # Hook timestamps are ISO 8601 ending in Z (UTC).
        s = raw.rstrip("Z")
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except (TypeError, ValueError):
        return None


def load_entries(path: pathlib.Path) -> list[dict]:
    entries: list[dict] = []
    try:
        with path.open(encoding="utf-8") as f:
            for raw in f:
                raw = raw.strip()
                if not raw:
                    continue
                try:
                    entries.append(json.loads(raw))
                except json.JSONDecodeError:
                    continue
    except OSError:
        return []
    return entries


def summarize(entries: list[dict], since: datetime, top: int) -> dict:
    counts: dict[str, dict[str, int]] = defaultdict(lambda: {"ERROR": 0, "WARNING": 0, "INFO": 0})
    issues_by_hook: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    last_example: dict[str, dict] = {}
    total_in_window = 0
    for entry in entries:
        ts = _parse_ts(entry.get("ts"))
        if ts is None or ts < since:
            continue
        severity = (entry.get("severity") or "INFO").upper()
        if severity not in ("ERROR", "WARNING", "INFO"):
            severity = "INFO"
        hook = entry.get("hook") or entry.get("source") or "unknown"
        counts[hook][severity] += 1
        issue = entry.get("issue")
        if issue:
            issues_by_hook[hook][issue] += 1
        last_example[hook] = entry
        total_in_window += 1

    ranked = sorted(
        counts.items(),
        key=lambda kv: (kv[1]["ERROR"] * 10 + kv[1]["WARNING"], kv[1]["ERROR"]),
        reverse=True,
    )

    top_rows = []
    for hook, sev in ranked[:top]:
        top_issues = sorted(issues_by_hook[hook].items(), key=lambda kv: kv[1], reverse=True)[:3]
        top_rows.append({
            "hook": hook,
            "error_count": sev["ERROR"],
            "warning_count": sev["WARNING"],
            "info_count": sev["INFO"],
            "top_issues": [{"issue": iss, "count": c} for iss, c in top_issues],
            "last_example_ts": last_example.get(hook, {}).get("ts"),
        })

    return {
        "since": since.isoformat(),
        "total_in_window": total_in_window,
        "distinct_hooks": len(counts),
        "top": top_rows,
    }


def render_human(report: dict, days: int) -> str:
    lines = [
        f"Recent errors — last {days} day(s) (since {report['since']})",
        f"  Total events: {report['total_in_window']}",
        f"  Distinct hooks: {report['distinct_hooks']}",
        "",
    ]
    if not report["top"]:
        lines.append("No WARNING/ERROR entries in window.")
        return "\n".join(lines)

    lines.append(f"Top {len(report['top'])} hooks by severity (ERROR weighted 10x):")
    for i, row in enumerate(report["top"], 1):
        lines.append(
            f"  {i}. {row['hook']:<32}  "
            f"ERR={row['error_count']:<4} WARN={row['warning_count']:<4} INFO={row['info_count']}"
        )
        for iss in row["top_issues"]:
            lines.append(f"       └ {iss['issue']:<40} x {iss['count']}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Top hooks by recent error/warning count")
    parser.add_argument("--days", type=int, default=7, help="Window size in days (default 7)")
    parser.add_argument("--top", type=int, default=5, help="Number of hooks to surface (default 5)")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    parser.add_argument(
        "--errors-log",
        default=".ai-skills-memory/errors.log",
        help="Path to errors.log (default: <cwd>/.ai-skills-memory/errors.log)",
    )
    args = parser.parse_args()

    path = pathlib.Path(args.errors_log).expanduser()
    if not path.is_file():
        msg = f"errors.log not found at {path} — no history yet. Use /ai-skills-init in this repo."
        if args.json:
            print(json.dumps({"error": "not_found", "path": str(path)}, indent=2))
        else:
            print(msg)
        return 0

    entries = load_entries(path)
    since = datetime.now(timezone.utc) - timedelta(days=max(1, args.days))
    report = summarize(entries, since, max(1, args.top))

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(render_human(report, args.days))
    return 0


if __name__ == "__main__":
    sys.exit(main())
