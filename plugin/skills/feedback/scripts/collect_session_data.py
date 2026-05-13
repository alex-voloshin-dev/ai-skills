#!/usr/bin/env python3
"""
collect_session_data.py — deterministic Claude Code session log parser
for /feedback.

Reads JSONL session transcripts from
  ~/.claude/projects/<sanitized-cwd>/*.jsonl
and emits a single JSON object on stdout:

  {
    "meta": {
      "window_days": 7,
      "project_path": "/home/u/repo/ai-assets",
      "log_dir": "/home/u/.claude/projects/-home-u-repo-ai-assets",
      "plugin_filter": "ai-assets",
      "severity_floor": "warn",
      "now": "<iso-utc>",
      "sessions_total": N,
      "sessions_scanned": M,
      "lines_parsed": K,
      "lines_skipped_malformed": J,
      "classifier_version": "1"
    },
    "findings": [ { ... } ],
    "groups":   [ { ... } ]
  }

Each finding has:

  {
    "id": "<finding-id>",
    "session_id": "<uuid>",
    "ts": "<iso>",
    "cwd": "<path>",
    "git_branch": "main",
    "cli_version": "2.1.132",
    "kind": "hook|subagent|skill|command|assistant|system",
    "source": "ralph-stop.py" | "develop" | "/feedback" | ...,
    "plugin_id": "ai-assets" | null,
    "severity": "error|warn|info",
    "signature": "<normalized-error-string>",
    "excerpt": "<<=400 chars verbatim with secrets redacted>",
    "lead_in": "<previous event summary>",
    "follow_up": "<next event summary>"
  }

Groups collapse findings with the same (kind, source, signature):

  {
    "kind": "hook",
    "source": "ralph-stop.py",
    "signature": "permission denied",
    "severity": "error",
    "count": 5,
    "first_seen": "<iso>",
    "last_seen": "<iso>",
    "evidence_ids": ["<finding-id>", ...]   # at most 3 most-recent
  }

Design constraints:
- Stream-parse: do not load whole files
- Mask anything matching the secret regex
- Skip malformed lines but count them
- Never modify session files; read-only
- English-only output
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Iterable, Iterator

CLASSIFIER_VERSION = "1"
MAX_EXCERPT_CHARS = 400
SECRET_RE = re.compile(
    r"(?i)(api[_-]?key|secret|token|password|credential)([\"'\s:=]+)([^\s\"']+)"
)
PATH_NUM_RE = re.compile(r"\b\d+\b")            # for signature normalization
ABS_PATH_RE = re.compile(r"/[A-Za-z0-9._/-]+")   # for signature normalization (masked to <path>)


# ------------- helpers -------------

def _redact(text: str) -> str:
    return SECRET_RE.sub(r"\1\2<redacted>", text)


def _sanitize_cwd(path: str) -> str:
    """Convert /home/u/repo → -home-u-repo (Claude Code project dir convention)."""
    return path.replace("/", "-")


def _resolve_log_dir(project_path: str, home: Path) -> Path:
    abs_p = str(Path(project_path).resolve())
    return home / ".claude" / "projects" / _sanitize_cwd(abs_p)


def _iter_session_files(log_dir: Path, days: int, max_sessions: int) -> list[Path]:
    if not log_dir.is_dir():
        return []
    files = [p for p in log_dir.glob("*.jsonl") if p.is_file()]
    if days > 0:
        cutoff = dt.datetime.now(dt.timezone.utc).timestamp() - days * 86400
        files = [p for p in files if p.stat().st_mtime >= cutoff]
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    if max_sessions > 0:
        files = files[:max_sessions]
    return files


def _stream_jsonl(path: Path) -> Iterator[tuple[int, dict | None]]:
    try:
        with path.open("r", encoding="utf-8", errors="replace") as f:
            for i, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    yield i, json.loads(line)
                except Exception:
                    yield i, None
    except OSError:
        return


def _excerpt(payload: Any) -> str:
    try:
        s = json.dumps(payload, ensure_ascii=False)
    except Exception:
        s = repr(payload)
    s = _redact(s)
    if len(s) > MAX_EXCERPT_CHARS:
        s = s[: MAX_EXCERPT_CHARS - 1] + "…"
    return s


def _signature(text: str) -> str:
    """Normalize an error string so similar failures collapse into one group."""
    if not text:
        return "<empty>"
    s = _redact(text)
    s = ABS_PATH_RE.sub("<path>", s)
    s = PATH_NUM_RE.sub("<n>", s)
    s = re.sub(r"\s+", " ", s).strip()
    if len(s) > 200:
        s = s[:199] + "…"
    return s


def _finding_id(session_id: str, line_no: int, kind: str) -> str:
    h = hashlib.sha1(f"{session_id}:{line_no}:{kind}".encode()).hexdigest()[:8]
    return f"f-{h}"


def _detect_plugin_id(text: str) -> str | None:
    # Match .../plugins/cache/<owner-or-name>/<plugin-name>/... or ${CLAUDE_PLUGIN_ROOT} hint.
    m = re.search(r"/plugins/cache/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)/", text)
    if m:
        return m.group(2)
    if "${CLAUDE_PLUGIN_ROOT}" in text:
        return "ai-assets"  # heuristic; not strict
    return None


def _source_from_payload(obj: dict, kind: str) -> str:
    """Best-effort source identity for a finding."""
    if kind == "hook":
        for info in obj.get("hookInfos", []) or []:
            cmd = info.get("command", "")
            m = re.search(r"hooks/scripts/([A-Za-z0-9_.-]+)", cmd)
            if m:
                return m.group(1)
            if cmd:
                return cmd.split()[-1][-60:]
        return "<unknown-hook>"
    if kind == "subagent":
        return obj.get("subagent_type") or obj.get("agent") or "<unknown-subagent>"
    if kind == "command":
        return obj.get("command", "<unknown-command>")
    if kind == "skill":
        return obj.get("skill", "<unknown-skill>")
    if kind == "assistant":
        return obj.get("message", {}).get("model", "assistant")
    return obj.get("subtype") or obj.get("type") or "system"


# ------------- classifiers -------------

def _classify(obj: dict) -> tuple[str, str, str] | None:
    """
    Returns (kind, severity, signature) if this event is a finding, else None.
    """
    if not isinstance(obj, dict):
        return None
    t = obj.get("type")
    subtype = obj.get("subtype")

    # 1. hook errors via stop_hook_summary
    if t == "system" and subtype == "stop_hook_summary":
        errs = obj.get("hookErrors") or []
        if errs:
            return "hook", "error", _signature(errs[0])

    # 2. system-level error/warning
    if t == "system":
        lvl = obj.get("level")
        if lvl in ("error", "warning"):
            sev = "error" if lvl == "error" else "warn"
            sig = _signature(json.dumps(obj.get("message") or obj.get("subtype") or obj))
            return "system", sev, sig

    # 3. assistant abnormal stops
    if t == "assistant":
        msg = obj.get("message") or {}
        stop = msg.get("stop_reason")
        if stop in ("tool_use_error", "max_tokens", "refusal"):
            return "assistant", "warn", _signature(f"stop_reason={stop}")

    # 4. task-notification failure inside a user event
    if t == "user":
        content = obj.get("message", {}).get("content", "")
        if isinstance(content, str) and "<task-notification>" in content:
            m = re.search(r"<status>([a-z]+)</status>", content)
            if m and m.group(1) in ("failed", "timeout", "cancelled", "error"):
                return "subagent", "error", _signature(f"task status={m.group(1)}")

    # 5. tool failure
    if t == "system" and subtype in ("tool_use_failure", "tool_error"):
        sig = _signature(json.dumps(obj.get("error") or obj))
        return "system", "error", sig

    return None


# ------------- pipeline -------------

def collect(
    project_path: str,
    days: int,
    plugin_filter: str,
    severity_floor: str,
    max_sessions: int,
    home: Path,
) -> dict:
    log_dir = _resolve_log_dir(project_path, home)
    files = _iter_session_files(log_dir, days, max_sessions)

    sev_order = {"info": 0, "warn": 1, "error": 2}
    floor = sev_order.get(severity_floor, 1)

    meta = {
        "window_days": days,
        "project_path": str(Path(project_path).resolve()),
        "log_dir": str(log_dir),
        "plugin_filter": plugin_filter,
        "severity_floor": severity_floor,
        "now": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "sessions_total": len(list(log_dir.glob("*.jsonl"))) if log_dir.is_dir() else 0,
        "sessions_scanned": len(files),
        "lines_parsed": 0,
        "lines_skipped_malformed": 0,
        "classifier_version": CLASSIFIER_VERSION,
    }

    findings: list[dict] = []

    for path in files:
        session_id = path.stem
        prev_summary = None
        window: list[dict] = []  # short tail of last 2 events for lead-in / follow-up
        # We need follow-up too — do a two-pass over a small ring.
        events = list(_stream_jsonl(path))
        meta["lines_parsed"] += len(events)
        for idx, (line_no, obj) in enumerate(events):
            if obj is None:
                meta["lines_skipped_malformed"] += 1
                continue
            classified = _classify(obj)
            if not classified:
                continue
            kind, sev, sig = classified
            if sev_order[sev] < floor:
                continue
            raw_excerpt = _excerpt(obj)
            plugin_id = _detect_plugin_id(raw_excerpt) or _detect_plugin_id(
                json.dumps(obj.get("hookInfos") or "", ensure_ascii=False)
            )
            if plugin_filter != "all":
                # If a plugin_id was extracted, gate on it.
                # If it was not extractable, keep the finding only when source path looks plugin-related.
                if plugin_id and plugin_id != plugin_filter:
                    continue

            lead_in = None
            for j in range(idx - 1, max(-1, idx - 3), -1):
                _, lo = events[j]
                if isinstance(lo, dict):
                    lead_in = f"{lo.get('type', '?')}/{lo.get('subtype', '')}".strip("/")
                    break
            follow_up = None
            for j in range(idx + 1, min(len(events), idx + 3)):
                _, fo = events[j]
                if isinstance(fo, dict):
                    follow_up = f"{fo.get('type', '?')}/{fo.get('subtype', '')}".strip("/")
                    break

            findings.append({
                "id": _finding_id(session_id, line_no, kind),
                "session_id": session_id,
                "line": line_no,
                "ts": obj.get("timestamp") or "",
                "cwd": obj.get("cwd") or "",
                "git_branch": obj.get("gitBranch") or "",
                "cli_version": obj.get("version") or "",
                "kind": kind,
                "source": _source_from_payload(obj, kind),
                "plugin_id": plugin_id,
                "severity": sev,
                "signature": sig,
                "excerpt": raw_excerpt,
                "lead_in": lead_in or "",
                "follow_up": follow_up or "",
            })

    # group
    groups: dict[tuple[str, str, str], dict] = {}
    for f in findings:
        key = (f["kind"], f["source"], f["signature"])
        g = groups.setdefault(key, {
            "kind": f["kind"],
            "source": f["source"],
            "signature": f["signature"],
            "severity": f["severity"],
            "count": 0,
            "first_seen": f["ts"] or "",
            "last_seen": f["ts"] or "",
            "evidence_ids": [],
        })
        g["count"] += 1
        if f["ts"]:
            if not g["first_seen"] or f["ts"] < g["first_seen"]:
                g["first_seen"] = f["ts"]
            if not g["last_seen"] or f["ts"] > g["last_seen"]:
                g["last_seen"] = f["ts"]
        if sev_order[f["severity"]] > sev_order[g["severity"]]:
            g["severity"] = f["severity"]
        if len(g["evidence_ids"]) < 3:
            g["evidence_ids"].append(f["id"])

    groups_list = sorted(
        groups.values(),
        key=lambda g: (-sev_order[g["severity"]], -g["count"], g["last_seen"]),
    )

    return {"meta": meta, "findings": findings, "groups": groups_list}


# ------------- canonical output (v0.3.13+) -------------
#
# The legacy `collect()` shape lists *raw event* findings plus an aggregated
# `groups` array. Canonical schema (`plugin/skills/feedback/output-schema.json`,
# schema_version="1") inverts that: `findings` are aggregated (one per unique
# tuple) with a `count`, `excerpts[]`, severity bands, and stable `f-NNN` ids;
# `groups` becomes a thin index of `finding_ids` per axis. This is the shape
# `/plugin-author fix-feedback` consumes as the JSON parity counterpart of the
# Markdown report.

SCHEMA_VERSION = "1"

SEVERITY_ORDER = ("info", "warn", "error")  # ascending


def _verdict(canonical_findings: list[dict], sessions_scanned: int) -> str:
    if not canonical_findings:
        return "INSUFFICIENT_DATA" if sessions_scanned == 0 else "GREEN"
    sev_set = {f["severity"] for f in canonical_findings}
    if "error" in sev_set:
        return "RED"
    if "warn" in sev_set:
        return "YELLOW"
    return "GREEN"


def to_canonical(
    legacy: dict,
    *,
    tool_version: str = "ai-assets@unknown",
    report_md_path: str = "",
) -> dict:
    """Project the legacy worker output into the canonical schema.

    Canonical `findings` are built from legacy `groups` (already aggregated)
    so count, first/last_seen, severity, and signature flow through cleanly.
    Excerpts are pulled from legacy `findings` by `evidence_ids` (up to 3 per
    finding, ≤ 400 chars each).
    """
    legacy_meta = legacy.get("meta", {})
    legacy_groups = legacy.get("groups", [])
    legacy_events = legacy.get("findings", [])
    events_by_id = {e["id"]: e for e in legacy_events if "id" in e}

    canonical_findings: list[dict] = []
    for idx, g in enumerate(legacy_groups, start=1):
        excerpts: list[dict] = []
        for ev_id in g.get("evidence_ids", []):
            ev = events_by_id.get(ev_id)
            if not ev:
                continue
            ex_text = ev.get("excerpt", "") or ""
            if len(ex_text) > 400:
                ex_text = ex_text[:400]
            excerpts.append({
                "session_id": ev.get("session_id", ""),
                "timestamp": ev.get("ts", "") or "",
                "excerpt": ex_text,
            })
        canonical_findings.append({
            "finding_id": f"f-{idx:03d}",
            "severity": g.get("severity", "warn"),
            "source_kind": g.get("kind", "system"),
            "source_identity": g.get("source", "") or "unknown",
            "signature": g.get("signature", "") or "unknown",
            "count": int(g.get("count", 1)),
            "first_seen": g.get("first_seen", "") or "",
            "last_seen": g.get("last_seen", "") or "",
            "excerpts": excerpts,
        })

    by_kind: dict[str, list[str]] = {}
    for f in canonical_findings:
        by_kind.setdefault(f["source_kind"], []).append(f["finding_id"])
    canonical_groups = [
        {"by": "source_kind", "name": k, "finding_ids": v}
        for k, v in sorted(by_kind.items())
    ]

    return {
        "schema_version": SCHEMA_VERSION,
        "meta": {
            "ts": legacy_meta.get("now", "") or "",
            "tool_version": tool_version,
            "window_days": int(legacy_meta.get("window_days", 0)),
            "project_path": legacy_meta.get("project_path", "") or "",
            "plugin_filter": legacy_meta.get("plugin_filter", "") or "",
            "sessions_scanned": int(legacy_meta.get("sessions_scanned", 0)),
            "malformed_lines": int(legacy_meta.get("lines_skipped_malformed", 0)),
            "classifier_version": legacy_meta.get("classifier_version", "unknown"),
            "report_md_path": report_md_path or "",
        },
        "verdict": _verdict(canonical_findings, int(legacy_meta.get("sessions_scanned", 0))),
        "findings": canonical_findings,
        "groups": canonical_groups,
    }


# ------------- cli -------------

def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Collect Claude Code session findings for /feedback.")
    p.add_argument("--days", type=int, default=7)
    p.add_argument("--project", type=str, default=os.getcwd())
    p.add_argument("--plugin", type=str, default="ai-assets")
    p.add_argument("--severity", choices=["all", "warn", "error"], default="warn")
    p.add_argument("--max-sessions", type=int, default=100)
    p.add_argument("--home", type=str, default=str(Path.home()))
    p.add_argument(
        "--out-json",
        type=str,
        default=None,
        help="If set, atomically write the canonical schema (see plugin/skills/feedback/output-schema.json) "
             "to this path. Paired with the Markdown report written by the skill.",
    )
    p.add_argument(
        "--report-md-path",
        type=str,
        default="",
        help="Absolute path of the paired Markdown report, embedded into the canonical JSON meta for traceability.",
    )
    p.add_argument(
        "--tool-version",
        type=str,
        default="ai-assets@unknown",
        help="Plugin version label, embedded into canonical JSON meta (e.g. `ai-assets@0.3.13`).",
    )
    p.add_argument(
        "--stdout",
        choices=["legacy", "canonical"],
        default="legacy",
        help="Shape to emit on stdout. `legacy` (default) preserves backward compat for the Markdown renderer. "
             "`canonical` emits the schema-validated shape — useful for `/plugin-author fix-feedback` pipes.",
    )
    return p.parse_args()


def _atomic_write_json(path_str: str, payload: dict) -> None:
    p = Path(path_str)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(p.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(p)


def main() -> int:
    args = _parse_args()
    sev_floor = {"all": "info", "warn": "warn", "error": "error"}[args.severity]
    legacy = collect(
        project_path=args.project,
        days=args.days,
        plugin_filter=args.plugin,
        severity_floor=sev_floor,
        max_sessions=args.max_sessions,
        home=Path(args.home),
    )

    canonical = to_canonical(
        legacy,
        tool_version=args.tool_version,
        report_md_path=args.report_md_path,
    )

    if args.out_json:
        _atomic_write_json(args.out_json, canonical)

    out = canonical if args.stdout == "canonical" else legacy
    json.dump(out, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
