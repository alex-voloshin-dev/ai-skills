#!/usr/bin/env python3
"""parse_feedback_report.py — read a /feedback output and emit a normalized findings array.

Primary path: read the machine-readable JSON counterpart (`<stamp>.json`).
Fallback path (`--md`): reparse the Markdown report — brittle by design,
every emitted WP is tagged `provenance: md-fallback`.

Contract documented in plugin/skills/plugin-author/feedback-parser.md.
Until /feedback ships the .json companion (open contract dependency), the
--md path is the default in production; callers MUST set provenance.

Stdout: a single JSON object `{"meta": {...}, "findings": [...], "provenance": "json|md-fallback"}`.
Exit codes: 0 ok; 2 missing or unreadable input; 3 schema-validation failure; 4 markdown fallback could not parse.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "1"

REQUIRED_FINDING_FIELDS = (
    "finding_id",
    "severity",
    "source_kind",
    "source_identity",
    "signature",
    "count",
    "first_seen",
    "last_seen",
    "excerpts",
)

VALID_SEVERITIES = {"error", "warn", "info"}
VALID_SOURCE_KINDS = {"hook", "subagent", "skill", "command", "system"}


def die(msg: str, code: int) -> None:
    print(f"parse_feedback_report: {msg}", file=sys.stderr)
    sys.exit(code)


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        die(f"input file not found: {path}", 2)
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        die(f"JSON parse error in {path}: {exc}", 3)
        return {}


def validate_schema(payload: dict[str, Any]) -> None:
    if payload.get("schema_version") != SCHEMA_VERSION:
        die(
            f"unsupported schema_version: {payload.get('schema_version')!r} (expected {SCHEMA_VERSION!r})",
            3,
        )
    if "findings" not in payload or not isinstance(payload["findings"], list):
        die("payload missing required `findings[]`", 3)
    for idx, finding in enumerate(payload["findings"]):
        for field in REQUIRED_FINDING_FIELDS:
            if field not in finding:
                die(f"finding[{idx}] missing required field `{field}`", 3)
        if finding["severity"] not in VALID_SEVERITIES:
            die(
                f"finding[{idx}].severity={finding['severity']!r} not in {sorted(VALID_SEVERITIES)}",
                3,
            )
        if finding["source_kind"] not in VALID_SOURCE_KINDS:
            die(
                f"finding[{idx}].source_kind={finding['source_kind']!r} not in {sorted(VALID_SOURCE_KINDS)}",
                3,
            )


def resolve_asset_hint(finding: dict[str, Any]) -> str | None:
    """Best-effort resolver — keeps the contract from feedback-parser.md in one place."""
    if finding.get("asset_hint"):
        return finding["asset_hint"]
    kind = finding.get("source_kind")
    identity = finding.get("source_identity") or ""
    if not identity:
        return None
    if kind == "hook":
        return f"plugin/hooks/scripts/{identity}"
    if kind == "subagent":
        return f"plugin/agents/{identity}.md"
    if kind in {"skill", "command"}:
        name = identity.lstrip("/")
        return f"plugin/skills/{name}/SKILL.md"
    return None


def emit_from_json(path: Path) -> dict[str, Any]:
    payload = load_json(path)
    validate_schema(payload)
    out_findings: list[dict[str, Any]] = []
    for finding in payload["findings"]:
        finding = dict(finding)
        if not finding.get("asset_hint"):
            hint = resolve_asset_hint(finding)
            if hint:
                finding["asset_hint"] = hint
                finding["asset_hint_provenance"] = "resolved"
        out_findings.append(finding)
    return {
        "meta": payload.get("meta", {}),
        "verdict": payload.get("verdict"),
        "findings": out_findings,
        "provenance": "json",
    }


# --- Markdown fallback (degraded) ---------------------------------------------------------------
#
# The MD report is best-effort: we parse the Findings table by header + columns,
# attach excerpts by H3 anchors in the Evidence section. This path is intentionally
# minimal — the contract is that /feedback emits the JSON counterpart so this path
# is rarely needed. Every finding it produces is tagged provenance=md-fallback.

FINDING_TABLE_RE = re.compile(
    r"^\|\s*(?P<kind>[^|]+?)\s*\|\s*(?P<src>[^|]+?)\s*\|"
    r"\s*(?P<sig>[^|]+?)\s*\|\s*(?P<count>\d+)\s*\|\s*(?P<sev>[^|]+?)\s*\|"
    r"\s*(?P<first>[^|]+?)\s*\|\s*(?P<last>[^|]+?)\s*\|\s*$",
    re.MULTILINE,
)


def emit_from_md(path: Path) -> dict[str, Any]:
    if not path.exists():
        die(f"markdown input not found: {path}", 2)
    text = path.read_text(encoding="utf-8")
    findings: list[dict[str, Any]] = []
    for idx, m in enumerate(FINDING_TABLE_RE.finditer(text), start=1):
        sev = m.group("sev").strip().lower()
        kind = m.group("kind").strip().lower()
        if sev not in VALID_SEVERITIES:
            sev = "warn"
        if kind not in VALID_SOURCE_KINDS:
            kind = "system"
        finding = {
            "finding_id": f"md-{idx:03d}",
            "severity": sev,
            "source_kind": kind,
            "source_identity": m.group("src").strip(),
            "signature": m.group("sig").strip(),
            "count": int(m.group("count")),
            "first_seen": m.group("first").strip(),
            "last_seen": m.group("last").strip(),
            "excerpts": [],
            "provenance": "md-fallback",
        }
        hint = resolve_asset_hint(finding)
        if hint:
            finding["asset_hint"] = hint
            finding["asset_hint_provenance"] = "md-fallback-resolved"
        findings.append(finding)
    if not findings:
        die(
            "no findings could be parsed from markdown report — verify the table layout matches feedback/templates/extended-template.md",
            4,
        )
    return {
        "meta": {"source_md": str(path)},
        "verdict": None,
        "findings": findings,
        "provenance": "md-fallback",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument(
        "--from",
        dest="from_path",
        required=True,
        help="Path to feedback-YYYY-MM-DD-HHMM.json (preferred) or .md (fallback with --md).",
    )
    parser.add_argument(
        "--md",
        action="store_true",
        help="Force markdown fallback path. Degraded; every WP is tagged provenance: md-fallback.",
    )
    args = parser.parse_args(argv)

    path = Path(args.from_path)
    if args.md or path.suffix.lower() == ".md":
        result = emit_from_md(path)
    else:
        result = emit_from_json(path)
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
