#!/usr/bin/env python3
"""
ai-assets plugin hook: pre-tool-use-committed-write (Round 8 CRIT-1)
Event: PreToolUse (matcher: Write|Edit)
Exit code 0 = allow; exit code 2 = block.

Per memory-discipline rule 6 + 03-MEMORY-ARCHITECTURE.md §8: enforces
allowlist on writes targeting `.ai-assets-memory/.committed/*`.

Allowlist source order:
1. ${CLAUDE_PLUGIN_ROOT}/memory/templates/committed-allowlist.txt (plugin defaults)
2. .ai-assets-memory/.committed/.allowlist-extensions.txt (project extension —
   itself in the default allowlist to bootstrap)

Match logic: glob patterns. Path matched against patterns; first match allows.

Writes outside .committed/ are NOT regulated by this hook (other hooks may
apply). Writes inside .committed/ that don't match allowlist are blocked.
"""

from __future__ import annotations

import fnmatch
import os
import pathlib
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _lib  # noqa: E402


COMMITTED_PREFIX = ".ai-assets-memory/.committed/"
DEFAULT_ALLOWLIST_PATH = "memory/templates/committed-allowlist.txt"
PROJECT_EXTENSION = ".ai-assets-memory/.committed/.allowlist-extensions.txt"


def load_allowlist() -> list[str]:
    """Concatenate plugin default + project extension allowlist patterns."""
    patterns: list[str] = []

    # Plugin defaults
    plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT")
    if plugin_root:
        plugin_path = pathlib.Path(plugin_root) / DEFAULT_ALLOWLIST_PATH
        patterns.extend(_parse_allowlist_file(plugin_path))

    # Project extension
    project_path = pathlib.Path.cwd() / PROJECT_EXTENSION
    patterns.extend(_parse_allowlist_file(project_path))

    return patterns


def _parse_allowlist_file(path: pathlib.Path) -> list[str]:
    """Parse one glob pattern per line; skip blanks and # comments."""
    if not path.exists():
        return []
    out: list[str] = []
    try:
        with path.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                out.append(line)
    except OSError:
        return []
    return out


def is_committed_write(file_path: str) -> bool:
    """True if the write target is under .ai-assets-memory/.committed/."""
    norm = file_path.replace("\\", "/")
    return COMMITTED_PREFIX in norm


def relative_committed_path(file_path: str) -> str:
    """Extract the part after .committed/ (so allowlist patterns match relative paths)."""
    norm = file_path.replace("\\", "/")
    idx = norm.find(COMMITTED_PREFIX)
    if idx < 0:
        return ""
    return norm[idx + len(COMMITTED_PREFIX):]


def matches_allowlist(rel_path: str, patterns: list[str]) -> bool:
    """True if rel_path matches any allowlist glob."""
    for pattern in patterns:
        if fnmatch.fnmatch(rel_path, pattern):
            return True
    return False


def main() -> None:
    data = _lib.read_stdin_json()
    data = _lib.normalize_hook_input(data)

    tool_name = data.get("tool_name", "")
    if tool_name not in ("Write", "Edit"):
        _lib.allow()

    tool_input = data.get("tool_input", {}) or {}
    file_path = tool_input.get("file_path", "")
    if not file_path:
        _lib.allow()

    if not is_committed_write(file_path):
        # Write outside .committed/ — this hook doesn't regulate it
        _lib.allow()

    rel = relative_committed_path(file_path)
    patterns = load_allowlist()

    if matches_allowlist(rel, patterns):
        _lib.allow()

    # Block with diagnostic
    _lib.log_to(
        "errors.log",
        {
            "ts": _lib.iso_now(),
            "severity": "ERROR",
            "hook": "pre-tool-use-committed-write",
            "issue": "committed_write_not_in_allowlist",
            "file_path": file_path,
            "rel_path": rel,
            "patterns_checked_count": len(patterns),
        },
    )
    _lib.block(
        f"BLOCKED: write to .committed/ path '{rel}' is not in the allowlist.\n"
        f"Allowlist patterns checked: {len(patterns)}\n"
        f"To permit this path, add a glob pattern to "
        f".ai-assets-memory/.committed/.allowlist-extensions.txt\n"
        f"Default allowlist: ${{CLAUDE_PLUGIN_ROOT}}/memory/templates/committed-allowlist.txt"
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        # Per failure-recovery: fail-open. Log the hook crash but don't block.
        _lib.log_to(
            "hook-errors.log",
            {"ts": _lib.iso_now(), "hook": "pre-tool-use-committed-write", "error": str(exc)},
        )
        sys.exit(0)
