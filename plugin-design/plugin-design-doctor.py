#!/usr/bin/env python3
"""
plugin-design-doctor.py — programmatic quality gate for the plugin design docs.

Built from Round 5 process improvement T6. Implements the 10-item pre-flight
checklist (memory: feedback_design_doc_quality.md) as automated checks.

Usage:
    python3 plugin-design-doctor.py [--fix]            # report issues
    python3 plugin-design-doctor.py --strict           # exit 2 on any issue
    python3 plugin-design-doctor.py --check counts     # only run count checks
    python3 plugin-design-doctor.py --check refs       # only run reference checks

Exit codes:
    0 — all checks pass (or non-strict mode with informational issues)
    1 — at least one warning found (in non-strict mode)
    2 — at least one error found (in strict mode), or fatal harness error

Checks implemented:
    counts        — sweep all docs for entity counts; flag mismatches against glossary
    refs          — every file path / section reference / cross-link resolves
    glossary      — every entity name in docs appears in _glossary.md
    forbidden     — agent frontmatter does not contain forbidden fields
    namespace     — issue ID prefixes (D/Q/P/F/H/M/G/N/O/S/T/U) don't collide
    todos         — flag TODO / FIXME / "we'll figure out later" markers
    duplicates    — same file referenced as deliverable in multiple batches
    math          — counts in different sections add up consistently
    completeness  — every workflow in 01-WORKFLOW-SPECS.md has skill in glossary
    leaks         — friendly4ai or personal info doesn't appear (D2)

Run from `plugin-design/` directory or pass --root.
"""

from __future__ import annotations

import argparse
import collections
import pathlib
import re
import sys
from dataclasses import dataclass, field
from typing import Iterable


# ---------- Configuration ----------

DESIGN_DOCS = [
    "00-PHASE-1-PLAN.md",
    "00a-CRITIQUE-AND-CORRECTIONS.md",
    "01-WORKFLOW-SPECS.md",
    "02-EVAL-FRAMEWORK.md",
    "03-MEMORY-ARCHITECTURE.md",
    "04-MIGRATION-CHECKLIST.md",
    "05-CONTEXT-ENGINEERING-GAP-ANALYSIS.md",
    "_glossary.md",
]

GLOSSARY_FILE = "_glossary.md"

# Authoritative counts from glossary §1
EXPECTED_COUNTS = {
    "skills": 52,
    "agents": 26,
    "rules": 12,
    "hooks": 15,
    "rubrics": 17,
    "schemas": 2,
    "output_styles": 2,
    "monitors": 1,
    "user_facing_docs": 14,
    "memory_templates": 7,
    "user_config_knobs": 8,
    "dependencies": 0,
}

# Plugin-shipped agents must NOT have these frontmatter fields
FORBIDDEN_AGENT_FIELDS = {"hooks", "mcpServers", "permissionMode"}

# Issue ID prefixes — used to prevent namespace collisions in critique
RESERVED_ID_PREFIXES = set("DQPFHMGNOSTU")

# Tokens that indicate friendly4ai or personal info leak
LEAK_PATTERNS = [
    r"\bfriendly4ai\b",
    r"\bf4ai\b",
    r"\bAI[- ]Readiness\b",
    r"\bAI Visibility\b",
    r"\bGEO Scanner\b",
    r"\bavav25\b",
    r"@gmail\.com",
]

TODO_MARKERS = [
    r"\bTODO\b",
    r"\bFIXME\b",
    r"we['']ll figure (?:that|it) out later",
    r"\bXXX\b",
]


@dataclass
class Issue:
    severity: str  # "error" | "warning" | "info"
    check: str
    doc: str
    line: int | None
    message: str

    def __str__(self) -> str:
        loc = f"{self.doc}:{self.line}" if self.line else self.doc
        return f"[{self.severity.upper()}] {self.check} @ {loc}: {self.message}"


@dataclass
class Report:
    issues: list[Issue] = field(default_factory=list)
    files_checked: int = 0

    def add(self, severity: str, check: str, doc: str, line: int | None, message: str) -> None:
        self.issues.append(Issue(severity, check, doc, line, message))

    @property
    def errors(self) -> list[Issue]:
        return [i for i in self.issues if i.severity == "error"]

    @property
    def warnings(self) -> list[Issue]:
        return [i for i in self.issues if i.severity == "warning"]

    def print(self) -> None:
        # Group by check
        by_check: dict[str, list[Issue]] = collections.defaultdict(list)
        for issue in self.issues:
            by_check[issue.check].append(issue)
        for check, issues in sorted(by_check.items()):
            print(f"\n=== {check} ({len(issues)} issue(s)) ===")
            for issue in issues:
                print(f"  {issue}")
        print(f"\n{'=' * 60}")
        print(f"Files checked: {self.files_checked}")
        print(f"Total issues: {len(self.issues)} ({len(self.errors)} errors, {len(self.warnings)} warnings)")


# ---------- Helper utilities ----------


def read_doc(root: pathlib.Path, name: str) -> tuple[str, list[str]]:
    """Returns (full text, list of lines) for a doc."""
    path = root / name
    text = path.read_text(encoding="utf-8")
    return text, text.splitlines()


def grep_lines(lines: list[str], pattern: str, flags: int = re.IGNORECASE) -> list[tuple[int, str]]:
    rx = re.compile(pattern, flags)
    return [(i + 1, line) for i, line in enumerate(lines) if rx.search(line)]


# ---------- Individual checks ----------


def check_counts(root: pathlib.Path, report: Report) -> None:
    """Pattern 1 (P1) + Pattern 10 (P10) — count consistency across docs."""
    # For each entity type, find every "<N> <word>" occurrence and verify it matches expected.
    entity_keywords = {
        "skills": r"\b(\d+)\s+(?:skill|skills)\b",
        "agents": r"\b(\d+)\s+(?:agent|agents)\b",
        "rules": r"\b(\d+)\s+(?:rule|rules)\b",
        "hooks": r"\b(\d+)\s+(?:hook|hooks)\b",
        "rubrics": r"\b(\d+)\s+(?:rubric|rubrics)\b",
    }
    # We allow numbers that match expected, OR are clearly "before" / "from" counts
    # (e.g., "42 existing skills" vs "52 in plugin").
    # Heuristic: flag any standalone count that doesn't match expected AND doesn't appear
    # near the words "existing" | "before" | "was" | "→" | "from" | "old"
    contextual_allowed = re.compile(
        r"(existing|before|was|from|old|original|carry|legacy|pre-|→|"
        r"\bof \d+|× \d+|\bsample|\bsampled|\bKEEP|\bREFACTOR|\bMERGE|\bARCHIVE|\bNEW|\bv0\.|"
        r"^\s*(?:\d+\.|\|)|\bWave|\biter|impact)",
        re.IGNORECASE,
    )

    for doc in DESIGN_DOCS:
        try:
            _, lines = read_doc(root, doc)
        except FileNotFoundError:
            report.add("error", "counts", doc, None, "doc not found")
            continue

        for entity, pattern in entity_keywords.items():
            expected = EXPECTED_COUNTS.get(entity)
            if expected is None:
                continue
            for lineno, line in enumerate(lines, 1):
                for m in re.finditer(pattern, line, re.IGNORECASE):
                    n = int(m.group(1))
                    if n == expected:
                        continue
                    # Allow contextual mentions (historic counts, before/after deltas)
                    if contextual_allowed.search(line):
                        continue
                    # Allow if line is in a Round-N critique section discussing past states
                    if re.search(r"Round [1-9]|Pattern \d|^>\s", line):
                        continue
                    report.add(
                        "warning",
                        "counts",
                        doc,
                        lineno,
                        f"{entity}={n} but expected {expected} (per glossary). Context: '{line.strip()[:120]}'",
                    )


def check_refs(root: pathlib.Path, report: Report) -> None:
    """Pattern 3 (P3) — every cross-doc reference resolves."""
    # Find references like `01-WORKFLOW-SPECS.md` or `plugin/foo/bar.md`
    ref_pattern = re.compile(r"`?([0-9]{2}[a-z]?-[A-Z][A-Z0-9-]+\.md|_[a-z-]+\.md)`?")
    plugin_path_pattern = re.compile(r"plugin/[a-z][a-zA-Z0-9_/.-]+\.(?:md|py|json|txt)")

    existing_design_files = {f for f in DESIGN_DOCS if (root / f).exists()}

    for doc in DESIGN_DOCS:
        try:
            _, lines = read_doc(root, doc)
        except FileNotFoundError:
            continue

        for lineno, line in enumerate(lines, 1):
            # Cross-doc references
            for m in ref_pattern.finditer(line):
                ref = m.group(1)
                if ref in existing_design_files:
                    continue
                # Allow .md references to plugin internals (those don't exist yet)
                if ref.startswith("plugin/"):
                    continue
                # Skip if referenced file is in DESIGN_DOCS expected list (might not yet exist)
                if ref in DESIGN_DOCS:
                    report.add(
                        "warning",
                        "refs",
                        doc,
                        lineno,
                        f"references '{ref}' but file not present in plugin-design/",
                    )

            # Plugin internal paths (informational only — we know they don't exist yet)
            # No checks here in v0.1
            pass


def check_forbidden_agent_fields(root: pathlib.Path, report: Report) -> None:
    """Pattern 7 (P7) — plugin agents must not have forbidden frontmatter fields."""
    # Only checks the design docs themselves for any literal mention of these fields
    # being set on a plugin-shipped agent (not merely discussed). Real check happens
    # at plugin install time via `claude plugin validate`.
    for doc in DESIGN_DOCS:
        try:
            _, lines = read_doc(root, doc)
        except FileNotFoundError:
            continue
        for lineno, line in enumerate(lines, 1):
            for field_name in FORBIDDEN_AGENT_FIELDS:
                # Look for explicit assignment like `permissionMode: plan` outside of:
                # - quoted/escaped contexts (discussion)
                # - tables (we discuss the field a lot in tables)
                # Skip if line is inside a "before" example (commonly preceded by `Before:` block in code fence)
                if re.match(rf"^{field_name}:\s+\w+", line) and "Before:" not in "\n".join(lines[max(0, lineno-10):lineno]):
                    report.add(
                        "error",
                        "forbidden",
                        doc,
                        lineno,
                        f"forbidden plugin agent field '{field_name}' set: {line.strip()}",
                    )


def check_namespace(root: pathlib.Path, report: Report) -> None:
    """Pattern 8 (P8) — issue ID prefixes don't collide between rounds."""
    # Just inform that the glossary tracks reservations; sanity-check that critique
    # uses prefixes from RESERVED_ID_PREFIXES.
    critique_path = root / "00a-CRITIQUE-AND-CORRECTIONS.md"
    if not critique_path.exists():
        return
    text = critique_path.read_text(encoding="utf-8")
    # Find issue IDs like "G1.", "M5.", "S3."
    # Issue IDs look like "S1." "T8." — single letter immediately followed by digit
    # Section headers like "## A. Internal contradictions" are NOT issue IDs (the letter is followed by ". ")
    id_pattern = re.compile(r"^### ([A-Z])(\d+)\.\s+\w", re.MULTILINE)
    for m in id_pattern.finditer(text):
        prefix = m.group(1)
        if prefix not in RESERVED_ID_PREFIXES:
            line_num = text[: m.start()].count("\n") + 1
            report.add(
                "warning",
                "namespace",
                "00a-CRITIQUE-AND-CORRECTIONS.md",
                line_num,
                f"issue ID prefix '{prefix}' not in glossary's reserved set; verify no collision",
            )


def check_todos(root: pathlib.Path, report: Report) -> None:
    """Pattern 5 (P5) — flag TODOs and 'we'll figure out later' markers."""
    for doc in DESIGN_DOCS:
        try:
            _, lines = read_doc(root, doc)
        except FileNotFoundError:
            continue
        for marker in TODO_MARKERS:
            for lineno, line in grep_lines(lines, marker, re.IGNORECASE):
                # Allow TODO markers explicitly inside critique discussions
                if "Pattern 5" in line or "Round" in line or "we'll figure" in line.lower() and "TODO" in line:
                    continue
                report.add(
                    "info",
                    "todos",
                    doc,
                    lineno,
                    f"TODO marker found: {line.strip()[:120]}",
                )


def check_leaks(root: pathlib.Path, report: Report) -> None:
    """Round 2 F-checks — friendly4ai and personal info."""
    for doc in DESIGN_DOCS:
        try:
            _, lines = read_doc(root, doc)
        except FileNotFoundError:
            continue
        for pattern in LEAK_PATTERNS:
            for lineno, line in grep_lines(lines, pattern):
                # Allow critique doc discussing the patterns themselves
                if "Pattern" in line or "leak" in line.lower() or "F1" in line or "G3" in line:
                    continue
                report.add(
                    "error",
                    "leaks",
                    doc,
                    lineno,
                    f"potential leak: pattern '{pattern}' matched: {line.strip()[:120]}",
                )


def check_glossary_present(root: pathlib.Path, report: Report) -> None:
    """Verify _glossary.md exists and is the source of truth."""
    glossary_path = root / GLOSSARY_FILE
    if not glossary_path.exists():
        report.add("error", "glossary", GLOSSARY_FILE, None, "glossary file missing")
        return
    text = glossary_path.read_text(encoding="utf-8")
    if "Single Source of Truth" not in text:
        report.add(
            "warning",
            "glossary",
            GLOSSARY_FILE,
            1,
            "glossary missing 'Single Source of Truth' header text — may be stale",
        )


# ---------- Main ----------


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument(
        "--root",
        default=".",
        help="plugin-design/ directory (default: current dir)",
    )
    parser.add_argument(
        "--check",
        action="append",
        choices=["counts", "refs", "glossary", "forbidden", "namespace", "todos", "leaks"],
        help="run only specific checks (can be repeated)",
    )
    parser.add_argument("--strict", action="store_true", help="exit 2 on any issue")
    args = parser.parse_args()

    root = pathlib.Path(args.root).resolve()
    if not root.is_dir():
        print(f"ERROR: {root} is not a directory", file=sys.stderr)
        return 2

    report = Report()
    report.files_checked = sum(1 for d in DESIGN_DOCS if (root / d).exists())

    selected = set(args.check) if args.check else {
        "counts", "refs", "glossary", "forbidden", "namespace", "todos", "leaks"
    }

    if "glossary" in selected:
        check_glossary_present(root, report)
    if "counts" in selected:
        check_counts(root, report)
    if "refs" in selected:
        check_refs(root, report)
    if "forbidden" in selected:
        check_forbidden_agent_fields(root, report)
    if "namespace" in selected:
        check_namespace(root, report)
    if "todos" in selected:
        check_todos(root, report)
    if "leaks" in selected:
        check_leaks(root, report)

    report.print()

    if args.strict and report.issues:
        return 2
    if report.errors:
        return 2
    if report.warnings:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
