#!/usr/bin/env python3
"""
ai-assets plugin — local validator + structural test runner.

This is the closest thing to `claude plugin validate ./plugin` that exists
today (no such CLI command ships with Claude Code as of April 2026 per
docs.claude.com). It runs every check we can perform without needing Claude
Code itself:

  1. JSON syntax for every .json file in the plugin
  2. Python syntax (ast.parse) for every .py file
  3. Bash syntax (bash -n) for monitors/env-watch.sh, when bash is on PATH
  4. Manifest required fields per Anthropic plugin spec
  5. Manifest userConfig shape — every entry must have type/title/description/default
  6. Structural counts cross-checked against README claims
     (agents=26, skills=52, rules=12, hooks=16, events=13, rubrics=17,
      calibration samples=102, commands=10, user docs=14, schemas=2,
      output styles=2, userConfig knobs=12)
  7. Agent frontmatter — required `name` + `description`; FORBIDDEN
     fields per Anthropic security boundary: `permissionMode`, `hooks`,
     `mcpServers`
  8. Skill frontmatter — required `name` + `description`; description is
     a string; name is lowercase + hyphens
  9. Hook scripts — every script under hooks/scripts/ (except _lib.py)
     imports _lib
 10. hooks.json — every command path resolves to an existing script;
     every event is one of the 13 canonical lifecycle events; pure JSON
     (no $schema-comment leftover)
 11. eval/calibration counts per rubric — 3 good + 3 bad

Real validation (manifest schema enforcement, hook ABI conformance) only
happens when you actually install the plugin into Claude Code via
`/plugin marketplace add <local-path>` then `/plugin install ai-assets`.
This script catches everything you can catch BEFORE that step.

Usage (from repo root):
    python plugin/dev/validate.py
    python plugin/dev/validate.py --quiet      # only failures + summary
    python plugin/dev/validate.py --json       # machine-readable report
    python plugin/dev/validate.py --strict     # warnings become failures

Exit code:
    0 = all checks pass
    1 = at least one check failed
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = PLUGIN_ROOT / ".claude-plugin" / "plugin.json"

CANONICAL_EVENTS = {
    "SessionStart",
    "InstructionsLoaded",
    "PreToolUse",
    "PostToolUse",
    "PostToolUseFailure",
    "StopFailure",
    "SubagentStart",
    "SubagentStop",
    "TaskCreated",
    "TaskCompleted",
    "Stop",
    "PreCompact",
    "SessionEnd",
}

FORBIDDEN_AGENT_FIELDS = {"permissionMode", "hooks", "mcpServers"}

EXPECTED_COUNTS = {
    "agents": 26,
    "skills": 52,
    "rules": 12,
    "hooks": 16,                 # excludes _lib.py
    "events": 13,
    "rubrics": 17,
    "calibration_samples": 102,  # 6 per rubric × 17
    "user_invocable_skills": 28, # skills with `context: fork` frontmatter
                                 # (10 primary workflows + 9 named companion +
                                 #  12 extended; this plugin uses
                                 #  skills-as-commands convention rather than
                                 #  commands/*.md)
    "user_docs": 14,
    "schemas": 2,
    "output_styles": 2,
    "userConfig_knobs": 12,
}


# ---------- Result accumulator ----------

@dataclass
class Result:
    name: str
    status: str              # "pass" | "warn" | "fail"
    detail: str = ""

@dataclass
class Report:
    results: list[Result] = field(default_factory=list)

    def add(self, name: str, status: str, detail: str = "") -> None:
        self.results.append(Result(name, status, detail))

    def passed(self) -> int:
        return sum(1 for r in self.results if r.status == "pass")

    def warned(self) -> int:
        return sum(1 for r in self.results if r.status == "warn")

    def failed(self) -> int:
        return sum(1 for r in self.results if r.status == "fail")

    def ok(self, strict: bool = False) -> bool:
        if self.failed() > 0:
            return False
        if strict and self.warned() > 0:
            return False
        return True


# ---------- File discovery helpers ----------

def _glob(rel_pattern: str) -> list[Path]:
    return sorted((PLUGIN_ROOT).glob(rel_pattern))


def _read_yaml_frontmatter(md_path: Path) -> dict | None:
    """Crude single-doc YAML frontmatter parser. Returns dict or None."""
    try:
        text = md_path.read_text(encoding="utf-8")
    except OSError:
        return None
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    block = text[3:end].strip("\n")
    out: dict = {}
    current_key: str | None = None
    current_list: list[str] | None = None
    for raw_line in block.splitlines():
        if not raw_line.strip() or raw_line.strip().startswith("#"):
            continue
        if raw_line.startswith("  - ") and current_list is not None:
            current_list.append(raw_line[4:].strip())
            continue
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*)\s*:\s*(.*)$", raw_line)
        if not m:
            continue
        key, value = m.group(1), m.group(2).rstrip()
        if value == "":
            current_key = key
            current_list = []
            out[key] = current_list
        else:
            current_key = None
            current_list = None
            # Strip surrounding quotes if present
            if (value.startswith('"') and value.endswith('"')) or (
                value.startswith("'") and value.endswith("'")
            ):
                value = value[1:-1]
            out[key] = value
    return out


# ---------- Individual checks ----------

def check_json_syntax(report: Report) -> None:
    files = _glob("**/*.json")
    bad = []
    for p in files:
        try:
            json.loads(p.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            bad.append(f"{p.relative_to(PLUGIN_ROOT)}: {e}")
    if bad:
        report.add("json_syntax", "fail", "; ".join(bad))
    else:
        report.add("json_syntax", "pass", f"{len(files)} json files OK")


def check_python_syntax(report: Report) -> None:
    files = _glob("**/*.py")
    bad = []
    for p in files:
        try:
            ast.parse(p.read_text(encoding="utf-8"), filename=str(p))
        except (OSError, SyntaxError) as e:
            bad.append(f"{p.relative_to(PLUGIN_ROOT)}: {e}")
    if bad:
        report.add("python_syntax", "fail", "; ".join(bad))
    else:
        report.add("python_syntax", "pass", f"{len(files)} py files OK")


def check_monitor_present(report: Report) -> None:
    """Verify the canonical Python monitor exists and parses.

    Since alpha.19 the monitor is `monitors/env-watch.py` (cross-platform
    Python). The legacy `env-watch.sh` is a deprecated shim — its bash
    syntax is no longer in scope for this validator (was a Windows
    pain-point). Python syntax of env-watch.py is already covered by
    `check_python_syntax`; this check just asserts presence + monitors.json
    points at it.
    """
    py = PLUGIN_ROOT / "monitors" / "env-watch.py"
    if not py.exists():
        report.add("monitor_present", "fail", "monitors/env-watch.py missing")
        return

    monitors_json = PLUGIN_ROOT / "monitors" / "monitors.json"
    if not monitors_json.exists():
        report.add("monitor_present", "fail", "monitors/monitors.json missing")
        return
    try:
        data = json.loads(monitors_json.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        report.add("monitor_present", "fail", f"monitors.json parse: {e}")
        return
    if not isinstance(data, list) or not data:
        report.add("monitor_present", "fail", "monitors.json must be a non-empty array")
        return

    cmd = (data[0] or {}).get("command", "")
    if "env-watch.py" not in cmd:
        report.add(
            "monitor_present",
            "fail",
            f"monitors.json command does not reference env-watch.py: {cmd!r}",
        )
        return
    report.add("monitor_present", "pass", "env-watch.py registered + present")


def check_manifest(report: Report) -> dict | None:
    if not MANIFEST_PATH.exists():
        report.add("manifest_present", "fail", str(MANIFEST_PATH))
        return None
    try:
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        report.add("manifest_parse", "fail", str(e))
        return None
    report.add("manifest_present", "pass", str(MANIFEST_PATH.relative_to(PLUGIN_ROOT)))

    required = ["name", "version", "description", "author"]
    missing = [k for k in required if k not in manifest]
    if missing:
        report.add("manifest_required_fields", "fail", f"missing: {missing}")
    else:
        report.add("manifest_required_fields", "pass", "name/version/description/author present")

    # name lowercase + hyphens
    name = manifest.get("name", "")
    if not re.fullmatch(r"[a-z][a-z0-9-]*", name):
        report.add("manifest_name_format", "fail", f"bad name: {name!r}")
    else:
        report.add("manifest_name_format", "pass", name)

    # semver
    ver = manifest.get("version", "")
    if not re.fullmatch(r"\d+\.\d+\.\d+(-[A-Za-z0-9.-]+)?", ver):
        report.add("manifest_version", "fail", f"not semver: {ver!r}")
    else:
        report.add("manifest_version", "pass", ver)

    # author
    author = manifest.get("author", {})
    if not (isinstance(author, dict) and author.get("name") and author.get("email")):
        report.add("manifest_author", "fail", f"author missing name/email: {author!r}")
    else:
        report.add("manifest_author", "pass", f"{author.get('name')} <{author.get('email')}>")

    # keywords
    keywords = manifest.get("keywords", [])
    if not isinstance(keywords, list) or not all(isinstance(k, str) for k in keywords):
        report.add("manifest_keywords", "fail", "keywords must be list of strings")
    else:
        bad_kw = [k for k in keywords if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", k)]
        if bad_kw:
            report.add("manifest_keywords", "fail", f"bad keyword chars: {bad_kw}")
        else:
            report.add("manifest_keywords", "pass", f"{len(keywords)} keywords")

    # userConfig shape
    uc = manifest.get("userConfig", {})
    if not isinstance(uc, dict):
        report.add("manifest_userConfig_shape", "fail", "userConfig must be object")
    else:
        bad_uc = []
        for key, entry in uc.items():
            if not isinstance(entry, dict):
                bad_uc.append(f"{key}: not an object")
                continue
            for req in ("type", "title", "description"):
                if req not in entry:
                    bad_uc.append(f"{key}: missing {req}")
            if "default" not in entry:
                bad_uc.append(f"{key}: missing default")
            if entry.get("type") not in {"number", "boolean", "string"}:
                bad_uc.append(f"{key}: unsupported type {entry.get('type')!r}")
        if bad_uc:
            report.add("manifest_userConfig_shape", "fail", "; ".join(bad_uc))
        else:
            report.add("manifest_userConfig_shape", "pass", f"{len(uc)} knobs OK")

    return manifest


def check_marketplace(report: Report) -> None:
    """Verify .claude-plugin/marketplace.json is present and well-formed.

    Required by Claude Code's `/plugin marketplace add <path>` command —
    without this file, install fails with "Marketplace file not found".
    Validates: file exists, valid JSON, has name/owner/plugins fields,
    plugins array references the plugin manifest correctly.
    """
    # Since alpha.22, the canonical marketplace.json lives ONE LEVEL UP
    # from the plugin (at ai-assets/.claude-plugin/marketplace.json) and
    # references the plugin via `source: "./plugin"`. The same-directory
    # layout (marketplace.json + plugin.json in plugin/.claude-plugin/)
    # was rejected by Claude Code v2.1.122 — kept as deprecated stub
    # with empty plugins[] so it does no harm if anyone uses the old
    # install path.
    # Marketplace.json is OPTIONAL — only needed for distribution via
    # `/plugin marketplace add`. Local development uses
    # `claude --plugin-dir <path>` per official Anthropic docs and does
    # NOT touch marketplace.json. So missing marketplace.json is WARN
    # (informational), not FAIL.
    repo_root = PLUGIN_ROOT.parent
    mp_path = repo_root / ".claude-plugin" / "marketplace.json"
    if not mp_path.exists():
        report.add(
            "marketplace_present",
            "warn",
            f"{mp_path} not found — local-dev install via `claude --plugin-dir` "
            "will work, but distribution via `/plugin marketplace add` won't.",
        )
        return
    try:
        data = json.loads(mp_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        report.add("marketplace_present", "fail", f"parse: {e}")
        return

    issues = []
    if not isinstance(data, dict):
        report.add("marketplace_present", "fail", "marketplace.json must be an object")
        return
    if not data.get("name"):
        issues.append("missing name")
    owner = data.get("owner")
    if not (isinstance(owner, dict) and owner.get("name")):
        issues.append("owner missing or has no name")
    plugins = data.get("plugins")
    if not (isinstance(plugins, list) and plugins):
        issues.append("plugins must be non-empty array")
    else:
        for i, plugin in enumerate(plugins):
            if not isinstance(plugin, dict):
                issues.append(f"plugins[{i}] not an object")
                continue
            if not plugin.get("name"):
                issues.append(f"plugins[{i}] missing name")
            src = plugin.get("source")
            if src is None:
                issues.append(f"plugins[{i}] missing source")
            # Per Anthropic marketplace.json convention used in
            # anthropics/skills and anthropics/claude-plugins-official,
            # local-path source MUST be a string shorthand like "./" or
            # "./plugins/<name>". Object form { "source": "local", ... }
            # is the SDK API shape, NOT marketplace.json — Claude Code
            # rejects it with "source type your Claude Code version does
            # not support". Catch that mistake here.
            elif isinstance(src, dict) and src.get("source") == "local":
                issues.append(
                    f"plugins[{i}] source uses SDK object form "
                    "{source:'local',path:...}; use string shorthand "
                    "(e.g., './plugin') in marketplace.json"
                )
            elif isinstance(src, str):
                # Resolve the source path relative to the marketplace dir
                # (one level up from .claude-plugin/) and verify it
                # actually contains a plugin manifest.
                marketplace_dir = mp_path.parent.parent
                target_dir = (marketplace_dir / src).resolve()
                target_manifest = target_dir / ".claude-plugin" / "plugin.json"
                if not target_manifest.exists():
                    issues.append(
                        f"plugins[{i}] source {src!r} does not resolve to a "
                        f"plugin: expected {target_manifest} to exist"
                    )

    if issues:
        report.add("marketplace_present", "fail", "; ".join(issues))
    else:
        report.add(
            "marketplace_present",
            "pass",
            f"marketplace {data.get('name')!r} with {len(plugins)} plugin(s)",
        )


def check_no_schema_comment(report: Report) -> None:
    """Per HIGH-B option 3: no `$schema-comment` field in any JSON manifest."""
    bad = []
    for p in _glob("**/*.json"):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(data, dict) and "$schema-comment" in data:
            bad.append(str(p.relative_to(PLUGIN_ROOT)))
    if bad:
        report.add("no_schema_comment", "fail", f"$schema-comment leftover in: {bad}")
    else:
        report.add("no_schema_comment", "pass", "no $schema-comment fields")


def check_counts(report: Report, manifest: dict | None) -> None:
    # Count user-invocable skills by scanning each skill's frontmatter for
    # `context: fork`. This plugin uses skills-as-commands convention rather
    # than the commands/*.md directory, so this is the canonical signal.
    user_invocable = 0
    for skill_md in _glob("skills/*/SKILL.md"):
        fm = _read_yaml_frontmatter(skill_md)
        if fm and fm.get("context") == "fork":
            user_invocable += 1

    counted = {
        "agents": len(_glob("agents/*.md")),
        "skills": len(_glob("skills/*/SKILL.md")),
        "rules": len(_glob("rules/*.md")),
        "hooks": len([p for p in _glob("hooks/scripts/*.py") if p.name != "_lib.py"]),
        "rubrics": len(_glob("eval/judge-rubrics/*.md")),
        "calibration_samples": len(_glob("eval/calibration/*/*/*.md")),
        "user_invocable_skills": user_invocable,
        "user_docs": len(_glob("docs/**/*.md")),
        "schemas": len(_glob("schemas/*.json")),
        "output_styles": len(_glob("output-styles/*.md")),
    }

    # Hook events from hooks.json
    hooks_path = PLUGIN_ROOT / "hooks" / "hooks.json"
    events_count = 0
    bad_events = []
    if hooks_path.exists():
        try:
            hooks_data = json.loads(hooks_path.read_text(encoding="utf-8"))
            events = hooks_data.get("hooks", {})
            events_count = len(events)
            for ev in events:
                if ev not in CANONICAL_EVENTS:
                    bad_events.append(ev)
        except (OSError, json.JSONDecodeError):
            pass
    counted["events"] = events_count

    # userConfig knobs
    if isinstance(manifest, dict):
        counted["userConfig_knobs"] = len(manifest.get("userConfig", {}))

    mismatches = []
    for k, expected in EXPECTED_COUNTS.items():
        actual = counted.get(k)
        if actual is None:
            continue
        if actual != expected:
            mismatches.append(f"{k}: expected {expected}, got {actual}")
    if bad_events:
        mismatches.append(f"non-canonical events in hooks.json: {bad_events}")

    if mismatches:
        report.add("structural_counts", "fail", "; ".join(mismatches))
    else:
        report.add(
            "structural_counts",
            "pass",
            ", ".join(f"{k}={v}" for k, v in counted.items()),
        )


def check_agent_frontmatter(report: Report) -> None:
    files = _glob("agents/*.md")
    fail = []
    warn = []
    for p in files:
        fm = _read_yaml_frontmatter(p)
        if fm is None:
            fail.append(f"{p.name}: no frontmatter")
            continue
        if not fm.get("name"):
            fail.append(f"{p.name}: missing name")
        if not fm.get("description"):
            fail.append(f"{p.name}: missing description")
        for forbidden in FORBIDDEN_AGENT_FIELDS:
            if forbidden in fm:
                fail.append(f"{p.name}: FORBIDDEN field {forbidden}")
        # Soft check: name should match filename stem
        if fm.get("name") and fm.get("name") != p.stem:
            warn.append(f"{p.name}: name {fm.get('name')!r} != filename stem")
    if fail:
        report.add("agent_frontmatter", "fail", "; ".join(fail))
    elif warn:
        report.add("agent_frontmatter", "warn", "; ".join(warn))
    else:
        report.add("agent_frontmatter", "pass", f"{len(files)} agents OK")


def check_skill_frontmatter(report: Report) -> None:
    files = _glob("skills/*/SKILL.md")
    fail = []
    for p in files:
        fm = _read_yaml_frontmatter(p)
        if fm is None:
            fail.append(f"{p.parent.name}: no frontmatter")
            continue
        name = fm.get("name") or ""
        if not name:
            fail.append(f"{p.parent.name}: missing name")
        elif not re.fullmatch(r"[a-z][a-z0-9-]*", name):
            fail.append(f"{p.parent.name}: bad name format {name!r}")
        elif name != p.parent.name:
            fail.append(f"{p.parent.name}: name {name!r} != folder name")
        if not fm.get("description"):
            fail.append(f"{p.parent.name}: missing description")
    if fail:
        report.add("skill_frontmatter", "fail", "; ".join(fail))
    else:
        report.add("skill_frontmatter", "pass", f"{len(files)} skills OK")


def check_orchestration_dual_path(report: Report) -> None:
    """Per alpha.26: orchestration skills must support both Subagents (default)
    and Agent Teams (when CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1) paths. Verify
    each orchestration skill body contains the detection bash block + both Path
    A and Path B sections."""
    ORCHESTRATION_SKILLS = {"develop", "team-bugfix", "feature-design"}
    issues = []
    for name in ORCHESTRATION_SKILLS:
        p = PLUGIN_ROOT / "skills" / name / "SKILL.md"
        if not p.exists():
            continue
        text = p.read_text(encoding="utf-8")
        missing = []
        if "Path A" not in text:
            missing.append("Path A (Subagents) section")
        if "Path B" not in text:
            missing.append("Path B (Agent Teams) section")
        # alpha.27: hard-rule against rationalised silent fallback
        if "no silent fallback" not in text.lower():
            missing.append("alpha.27 hard-rule against silent fallback")
        # alpha.29: must NOT contain the literal Bash command pattern
        # `echo "TEAMS_FLAG=${CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS:-0}"`
        # (the explicit detection trigger). Prose mentioning the env var
        # in negative instructions ("Do NOT run echo $...") is fine and
        # will not match this pattern.
        if 'echo "TEAMS_FLAG=' in text or 'echo \'TEAMS_FLAG=' in text:
            missing.append(
                "alpha.29 violation: explicit `echo \"TEAMS_FLAG=...\"` Bash "
                "command still present — should detect Path B availability "
                "implicitly via attempted team-create"
            )
        if missing:
            issues.append(f"{name}/SKILL.md missing: {', '.join(missing)}")
    if issues:
        report.add("orchestration_dual_path", "fail", "; ".join(issues))
    else:
        report.add(
            "orchestration_dual_path",
            "pass",
            f"{len(ORCHESTRATION_SKILLS)} orchestration skills declare both paths",
        )


def check_orchestration_skills_no_fork(report: Report) -> None:
    """Per Anthropic docs: subagents cannot spawn other subagents. Orchestration
    skills (those that spawn DEV/REVIEW/QA subagents via the Agent tool) MUST
    NOT have `context: fork` — that would run them in a forked subagent where
    the Agent tool is unavailable. Confirmed alpha.25 failure mode.
    """
    ORCHESTRATION_SKILLS = {"develop", "team-bugfix", "feature-design"}
    issues = []
    for name in ORCHESTRATION_SKILLS:
        p = PLUGIN_ROOT / "skills" / name / "SKILL.md"
        if not p.exists():
            continue
        fm = _read_yaml_frontmatter(p)
        if fm and fm.get("context") == "fork":
            issues.append(
                f"{name}/SKILL.md has `context: fork` — orchestration skills "
                "MUST run in main thread to retain Agent tool access. Remove "
                "the field. (Subagents cannot spawn other subagents per "
                "Anthropic docs.)"
            )
    if issues:
        report.add("orchestration_no_fork", "fail", "; ".join(issues))
    else:
        report.add(
            "orchestration_no_fork",
            "pass",
            f"{len(ORCHESTRATION_SKILLS)} orchestration skills run in main thread",
        )


def check_hook_imports_lib(report: Report) -> None:
    files = [p for p in _glob("hooks/scripts/*.py") if p.name != "_lib.py"]
    bad = []
    for p in files:
        text = p.read_text(encoding="utf-8")
        if "import _lib" not in text:
            bad.append(p.name)
    if bad:
        report.add("hook_lib_import", "fail", f"hooks NOT importing _lib: {bad}")
    else:
        report.add("hook_lib_import", "pass", f"{len(files)} hooks import _lib")


def check_hooks_json_paths(report: Report) -> None:
    hooks_path = PLUGIN_ROOT / "hooks" / "hooks.json"
    if not hooks_path.exists():
        report.add("hooks_json_paths", "fail", "hooks/hooks.json missing")
        return
    try:
        data = json.loads(hooks_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        report.add("hooks_json_paths", "fail", f"parse error: {e}")
        return

    bad = []
    total = 0
    for event_name, matchers in data.get("hooks", {}).items():
        for matcher in matchers:
            for hk in matcher.get("hooks", []):
                cmd = hk.get("command", "")
                rel = cmd.replace("${CLAUDE_PLUGIN_ROOT}/", "")
                total += 1
                target = PLUGIN_ROOT / rel
                if not target.exists():
                    bad.append(f"{event_name} -> {rel}")
    if bad:
        report.add("hooks_json_paths", "fail", "; ".join(bad))
    else:
        report.add("hooks_json_paths", "pass", f"{total} hook commands resolve")


def check_calibration_per_rubric(report: Report) -> None:
    rubrics = sorted(p.stem for p in _glob("eval/judge-rubrics/*.md"))
    issues = []
    for rubric in rubrics:
        good = _glob(f"eval/calibration/{rubric}/good/*.md")
        bad = _glob(f"eval/calibration/{rubric}/bad/*.md")
        if len(good) != 3:
            issues.append(f"{rubric}: good={len(good)} (expected 3)")
        if len(bad) != 3:
            issues.append(f"{rubric}: bad={len(bad)} (expected 3)")
    if issues:
        report.add("calibration_per_rubric", "fail", "; ".join(issues))
    else:
        report.add(
            "calibration_per_rubric",
            "pass",
            f"{len(rubrics)} rubrics × (3 good + 3 bad)",
        )


def check_eval_runner_present(report: Report) -> None:
    p = PLUGIN_ROOT / "eval" / "runner.py"
    if not p.exists():
        report.add("eval_runner_present", "fail", "eval/runner.py missing")
        return
    try:
        ast.parse(p.read_text(encoding="utf-8"))
    except SyntaxError as e:
        report.add("eval_runner_present", "fail", f"syntax: {e}")
        return
    report.add("eval_runner_present", "pass", "eval/runner.py parses")


# ---------- Main ----------

CHECKS = [
    check_json_syntax,
    check_python_syntax,
    check_monitor_present,
    check_marketplace,
    # check_manifest is special — returns the manifest for downstream checks
    check_no_schema_comment,
    check_agent_frontmatter,
    check_skill_frontmatter,
    check_orchestration_skills_no_fork,
    check_orchestration_dual_path,
    check_hook_imports_lib,
    check_hooks_json_paths,
    check_calibration_per_rubric,
    check_eval_runner_present,
]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="ai-assets plugin local validator",
    )
    parser.add_argument("--quiet", action="store_true", help="Only show failures + summary")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON report")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as failures")
    args = parser.parse_args()

    if not PLUGIN_ROOT.exists():
        print(f"ERROR: plugin root not found: {PLUGIN_ROOT}", file=sys.stderr)
        return 1

    report = Report()

    manifest = check_manifest(report)
    check_counts(report, manifest)
    for check in CHECKS:
        try:
            check(report)
        except Exception as e:
            report.add(check.__name__, "fail", f"check raised: {e!r}")

    if args.json:
        out = {
            "summary": {
                "passed": report.passed(),
                "warned": report.warned(),
                "failed": report.failed(),
                "ok": report.ok(strict=args.strict),
            },
            "results": [
                {"name": r.name, "status": r.status, "detail": r.detail}
                for r in report.results
            ],
        }
        print(json.dumps(out, indent=2, ensure_ascii=False))
    else:
        for r in report.results:
            if args.quiet and r.status == "pass":
                continue
            badge = {"pass": "OK  ", "warn": "WARN", "fail": "FAIL"}[r.status]
            line = f"  [{badge}] {r.name}"
            if r.detail and (r.status != "pass" or not args.quiet):
                line += f" -- {r.detail}"
            print(line)
        print("")
        print(f"Summary: {report.passed()} pass, {report.warned()} warn, {report.failed()} fail")
        if report.ok(strict=args.strict):
            print("Result: PASS")
        else:
            print("Result: FAIL")

    return 0 if report.ok(strict=args.strict) else 1


if __name__ == "__main__":
    sys.exit(main())
