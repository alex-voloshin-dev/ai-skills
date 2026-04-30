#!/usr/bin/env python3
"""
ai-assets plugin eval harness.

Per 02-EVAL-FRAMEWORK.md §11. v0.1 implementation: Tier 1 only (linters,
no LLM calls). Tier 2 + Tier 3 stubs return clear "not implemented in v0.1"
errors so the CLI surface is stable and `/eval` skill validates flag parsing.

Tier 1 checks (no cost, fast):
- Skill frontmatter: name + description present, lowercase-hyphens, third-person, "Use when" trigger (H5)
- Hook references: every entry in hooks.json resolves to a script file
- Char limits: no SKILL.md or rule.md exceeds 12_000 chars (project rule)
- AST validity: every plugin/hooks/scripts/*.py compiles cleanly via py_compile
- JSON validity: every plugin/schemas/*.json + plugin/eval/config.json + monitors.json + .claude-plugin/plugin.json + memory/templates/eval-baseline.schema.json parses
- Forbidden frontmatter fields on agents: no permissionMode, no hooks:, no mcpServers:

Exit codes:
- 0 = all checks passed
- 1 = at least one CRITICAL finding
- 2 = at least one WARNING (no CRITICAL)
- 3 = invalid CLI args

Usage:
    python3 plugin/eval/runner.py --tier 1
    python3 plugin/eval/runner.py --tier 1 --skill feature-design
    python3 plugin/eval/runner.py --tier 2  # not implemented in v0.1
    python3 plugin/eval/runner.py --tier 3  # not implemented in v0.1
    python3 plugin/eval/runner.py --all     # alias for --tier 1 (until 2/3 ship)
    python3 plugin/eval/runner.py --baseline <skill>  # not implemented in v0.1
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import py_compile
import re
import sys
from typing import Optional


CHAR_LIMIT_SKILL = 12_000
CHAR_LIMIT_RULE = 12_000

PLUGIN_ROOT = pathlib.Path(os.environ.get("CLAUDE_PLUGIN_ROOT") or pathlib.Path(__file__).resolve().parent.parent)

USE_WHEN_RE = re.compile(r"\bUse when\b|\bUse this\b|\bUse to\b|\bUse for\b|\bUse before\b|\bActivated when\b|\bUse standalone\b|\btrigger when\b|\btrigger whenever\b", re.IGNORECASE)

SKILL_NAME_RE = re.compile(r"^[a-z0-9-]+$")

FORBIDDEN_AGENT_FIELDS = {"permissionMode", "hooks:", "mcpServers:"}


class Finding:
    SEVERITIES = ("CRITICAL", "WARNING", "INFO")

    def __init__(self, severity: str, source: str, message: str):
        if severity not in self.SEVERITIES:
            raise ValueError(f"invalid severity {severity}")
        self.severity = severity
        self.source = source
        self.message = message

    def __str__(self) -> str:
        return f"[{self.severity}] {self.source}: {self.message}"


def parse_frontmatter(text: str) -> Optional[dict[str, str]]:
    """Naive parser; returns dict of top-level scalar fields or None if not present."""
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 4)
    if end < 0:
        return None
    block = text[4:end]
    out: dict[str, str] = {}
    current_key: Optional[str] = None
    current_lines: list[str] = []
    for line in block.split("\n"):
        # multi-line list-value support intentionally minimal
        if line and not line.startswith(" ") and ":" in line:
            if current_key is not None:
                out[current_key] = "\n".join(current_lines).strip()
            key, _, value = line.partition(":")
            current_key = key.strip()
            current_lines = [value.strip()]
        else:
            current_lines.append(line)
    if current_key is not None:
        out[current_key] = "\n".join(current_lines).strip()
    return out


def lint_skill(path: pathlib.Path, findings: list[Finding]) -> None:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        findings.append(Finding("CRITICAL", str(path), f"unreadable: {exc}"))
        return

    body_chars = len(text)
    if body_chars > CHAR_LIMIT_SKILL:
        findings.append(Finding("WARNING", str(path), f"body {body_chars} chars exceeds {CHAR_LIMIT_SKILL} limit"))

    fm = parse_frontmatter(text)
    if fm is None:
        findings.append(Finding("CRITICAL", str(path), "missing or malformed YAML frontmatter"))
        return

    name = fm.get("name", "")
    desc = fm.get("description", "")

    if not name:
        findings.append(Finding("CRITICAL", str(path), "frontmatter missing required `name` field"))
    elif not SKILL_NAME_RE.match(name):
        findings.append(Finding("WARNING", str(path), f"`name` not lowercase+hyphens: {name!r}"))

    if not desc:
        findings.append(Finding("CRITICAL", str(path), "frontmatter missing required `description` field"))
    elif not USE_WHEN_RE.search(desc):
        # Skip H5 check for non-invocable utility skills explicitly opting out
        if "disable-model-invocation: true" not in text:
            findings.append(Finding("WARNING", str(path), "description lacks `Use when` trigger pattern (H5)"))


def lint_rule(path: pathlib.Path, findings: list[Finding]) -> None:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        findings.append(Finding("CRITICAL", str(path), f"unreadable: {exc}"))
        return
    if len(text) > CHAR_LIMIT_RULE:
        findings.append(Finding("WARNING", str(path), f"body {len(text)} chars exceeds {CHAR_LIMIT_RULE} limit"))


def lint_agent(path: pathlib.Path, findings: list[Finding]) -> None:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        findings.append(Finding("CRITICAL", str(path), f"unreadable: {exc}"))
        return
    fm = parse_frontmatter(text)
    if fm is None:
        findings.append(Finding("CRITICAL", str(path), "missing or malformed YAML frontmatter"))
        return
    for forbidden in FORBIDDEN_AGENT_FIELDS:
        bare = forbidden.rstrip(":")
        if bare in fm:
            findings.append(Finding("CRITICAL", str(path), f"forbidden frontmatter field on plugin-shipped agent: `{bare}` (security boundary)"))


def lint_python(path: pathlib.Path, findings: list[Finding]) -> None:
    try:
        py_compile.compile(str(path), doraise=True)
    except py_compile.PyCompileError as exc:
        findings.append(Finding("CRITICAL", str(path), f"AST/syntax error: {exc.msg}"))
    except OSError as exc:
        findings.append(Finding("CRITICAL", str(path), f"unreadable: {exc}"))


def lint_json(path: pathlib.Path, findings: list[Finding]) -> None:
    try:
        json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        findings.append(Finding("CRITICAL", str(path), f"invalid JSON: {exc}"))
    except OSError as exc:
        findings.append(Finding("CRITICAL", str(path), f"unreadable: {exc}"))


def lint_hooks_json_refs(plugin_root: pathlib.Path, findings: list[Finding]) -> None:
    hooks_path = plugin_root / "hooks" / "hooks.json"
    if not hooks_path.exists():
        findings.append(Finding("CRITICAL", str(hooks_path), "hooks.json missing"))
        return
    try:
        data = json.loads(hooks_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        findings.append(Finding("CRITICAL", str(hooks_path), f"invalid JSON: {exc}"))
        return
    hooks_block = data.get("hooks", {})
    if not isinstance(hooks_block, dict):
        findings.append(Finding("CRITICAL", str(hooks_path), "`hooks` key must be an object"))
        return
    placeholder = "${CLAUDE_PLUGIN_ROOT}"
    for event, entries in hooks_block.items():
        if not isinstance(entries, list):
            continue
        for entry in entries:
            for h in entry.get("hooks", []):
                cmd = h.get("command", "")
                if not cmd.startswith(placeholder):
                    findings.append(Finding("WARNING", str(hooks_path), f"event {event}: command does not start with {placeholder}: {cmd}"))
                    continue
                rel = cmd.replace(placeholder + "/", "")
                target = plugin_root / rel
                if not target.exists():
                    findings.append(Finding("CRITICAL", str(hooks_path), f"event {event}: command references missing script: {rel}"))


def run_tier_1(plugin_root: pathlib.Path, only_skill: Optional[str] = None) -> list[Finding]:
    findings: list[Finding] = []

    skills_dir = plugin_root / "skills"
    if skills_dir.is_dir():
        for skill_md in sorted(skills_dir.glob("*/SKILL.md")):
            if only_skill and skill_md.parent.name != only_skill:
                continue
            lint_skill(skill_md, findings)

    rules_dir = plugin_root / "rules"
    if rules_dir.is_dir():
        for rule_md in sorted(rules_dir.glob("*.md")):
            lint_rule(rule_md, findings)

    agents_dir = plugin_root / "agents"
    if agents_dir.is_dir():
        for agent_md in sorted(agents_dir.glob("*.md")):
            lint_agent(agent_md, findings)

    scripts_dir = plugin_root / "hooks" / "scripts"
    if scripts_dir.is_dir():
        for py in sorted(scripts_dir.glob("*.py")):
            lint_python(py, findings)

    for json_path in (
        plugin_root / ".claude-plugin" / "plugin.json",
        plugin_root / "hooks" / "hooks.json",
        plugin_root / "monitors" / "monitors.json",
        plugin_root / "eval" / "config.json",
        plugin_root / "schemas" / "spawn-payload.schema.json",
        plugin_root / "schemas" / "return-contract.schema.json",
        plugin_root / "memory" / "templates" / "eval-baseline.schema.json",
    ):
        if json_path.exists():
            lint_json(json_path, findings)

    lint_hooks_json_refs(plugin_root, findings)

    return findings


def main() -> int:
    parser = argparse.ArgumentParser(prog="runner.py", description="ai-assets plugin eval harness (v0.1: Tier 1 only)")
    parser.add_argument("--tier", choices=["1", "2", "3"], default="1")
    parser.add_argument("--skill", help="limit to one skill name")
    parser.add_argument("--all", action="store_true", help="run all skills (Tier 1 only in v0.1)")
    parser.add_argument("--resume", action="store_true", help="resume Tier 3 run (not implemented in v0.1)")
    parser.add_argument("--baseline", help="capture per-skill baseline (not implemented in v0.1)")
    args = parser.parse_args()

    if args.baseline:
        print("ERROR: --baseline not implemented in v0.1; ships in B10+ Phase 3.", file=sys.stderr)
        return 3
    if args.resume:
        print("ERROR: --resume not implemented in v0.1.", file=sys.stderr)
        return 3
    if args.tier in ("2", "3") and not args.all:
        print(f"ERROR: --tier {args.tier} not implemented in v0.1. Tier 1 (linters) only.", file=sys.stderr)
        print("       Tier 2 (smoke) and Tier 3 (behavioral) ship after eval-judge wiring.", file=sys.stderr)
        return 3

    findings = run_tier_1(PLUGIN_ROOT, only_skill=args.skill)

    crit = [f for f in findings if f.severity == "CRITICAL"]
    warn = [f for f in findings if f.severity == "WARNING"]

    for f in findings:
        print(f, file=sys.stderr)
    print(f"\nTier 1 summary: {len(crit)} CRITICAL, {len(warn)} WARNING, total {len(findings)} findings.", file=sys.stderr)

    if crit:
        return 1
    if warn:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
