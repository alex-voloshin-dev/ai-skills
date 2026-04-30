#!/usr/bin/env python3
"""
ai-assets plugin hook: block-dangerous-commands
Event: PreToolUse (matcher: Bash)
Exit code 2 = block the command if it matches a dangerous pattern; 0 = allow.

Prevents accidental execution of destructive commands like rm -rf /,
DROP DATABASE, terraform destroy, kubectl delete namespace, and similar actions.

Per Round 13 MED-A: refactored from B2 inline _normalize_hook_input duplicate
to use the shared _lib module shipped in B8.
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _lib  # noqa: E402


DANGEROUS_PATTERNS = [
    ("Filesystem", re.compile(r"\brm\s+(-[a-zA-Z]*f[a-zA-Z]*\s+)?(-[a-zA-Z]*r[a-zA-Z]*\s+)?/(?!\S*\.)", re.IGNORECASE), "Recursive delete from root"),
    ("Filesystem", re.compile(r"\brm\s+-[a-zA-Z]*r[a-zA-Z]*f[a-zA-Z]*\s", re.IGNORECASE), "Forced recursive delete"),
    ("Filesystem", re.compile(r"\brmdir\s+/s\s+/q\s", re.IGNORECASE), "Windows forced recursive delete"),
    ("Filesystem", re.compile(r"Remove-Item\s+.*-Recurse.*-Force", re.IGNORECASE), "PowerShell forced recursive delete"),
    ("Database", re.compile(r"\bDROP\s+(DATABASE|SCHEMA|TABLE)\b", re.IGNORECASE), "Drop database/schema/table"),
    ("Database", re.compile(r"\bTRUNCATE\s+TABLE\b", re.IGNORECASE), "Truncate table"),
    ("Database", re.compile(r"\bDELETE\s+FROM\s+\w+\s*;?\s*$", re.IGNORECASE | re.MULTILINE), "Delete all rows (no WHERE clause)"),
    ("Infrastructure", re.compile(r"\bterraform\s+destroy\b", re.IGNORECASE), "Terraform destroy"),
    ("Infrastructure", re.compile(r"\bkubectl\s+delete\s+(namespace|ns)\b", re.IGNORECASE), "Delete Kubernetes namespace"),
    ("Infrastructure", re.compile(r"\bkubectl\s+delete\s+.*--all\b", re.IGNORECASE), "Delete all Kubernetes resources"),
    ("Infrastructure", re.compile(r"\bhelm\s+uninstall\b", re.IGNORECASE), "Helm uninstall release"),
    ("Git", re.compile(r"\bgit\s+push\s+.*--force\b", re.IGNORECASE), "Force push (rewrite remote history)"),
    ("Git", re.compile(r"\bgit\s+reset\s+--hard\b", re.IGNORECASE), "Hard reset (discard all changes)"),
    ("Git", re.compile(r"\bgit\s+clean\s+-[a-zA-Z]*f[a-zA-Z]*d", re.IGNORECASE), "Clean untracked files and directories"),
    ("System", re.compile(r"\bchmod\s+-R\s+777\b"), "World-writable permissions recursively"),
    ("System", re.compile(r"\bmkfs\b", re.IGNORECASE), "Format filesystem"),
    ("System", re.compile(r"\bdd\s+.*of=/dev/", re.IGNORECASE), "Direct disk write"),
    ("Docker", re.compile(r"\bdocker\s+system\s+prune\s+-a", re.IGNORECASE), "Prune all Docker data"),
    ("Docker", re.compile(r"\bdocker\s+rm\s+-f\s+\$\(docker\s+ps", re.IGNORECASE), "Force remove all containers"),
]


def check_command(command: str) -> list[tuple[str, str]]:
    findings = []
    for category, pattern, description in DANGEROUS_PATTERNS:
        if pattern.search(command):
            findings.append((category, description))
    return findings


def main():
    data = _lib.read_stdin_json()
    data = _lib.normalize_hook_input(data)

    command = data.get("tool_info", {}).get("command", "")
    if not command:
        _lib.allow()

    findings = check_command(command)
    if findings:
        msg = "BLOCKED: Dangerous command detected:\n"
        msg += f"  Command: {command[:200]}\n\n"
        msg += "  Reasons:\n"
        for category, description in findings:
            msg += f"    - [{category}] {description}\n"
        msg += "\nThis command may cause irreversible damage. Review and run manually if intended."
        print(msg, file=sys.stderr)
        _lib.log_to(
            "errors.log",
            {
                "ts": _lib.iso_now(),
                "severity": "ERROR",
                "hook": "block-dangerous-commands",
                "issue": "dangerous_command_blocked",
                "command_excerpt": command[:200],
                "findings": [{"category": c, "description": d} for c, d in findings],
            },
        )
        _lib.block(msg)

    _lib.allow()


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        # Fail-open per failure-recovery rule: never let a buggy hook block all tool use.
        _lib.log_to(
            "hook-errors.log",
            {"ts": _lib.iso_now(), "hook": "block-dangerous-commands", "error": str(exc)},
        )
        sys.exit(0)
