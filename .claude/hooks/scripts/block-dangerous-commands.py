#!/usr/bin/env python3
"""
Claude hook: block-dangerous-commands
Event: pre_run_command
Exit code 2 = block the command if it matches a dangerous pattern.

Prevents accidental execution of destructive commands like rm -rf /,
DROP DATABASE, terraform destroy, kubectl delete namespace, and similar actions.
"""

import json
import re
import sys


def _normalize_hook_input(data: dict) -> dict:
    """Normalize Claude hook payloads into a single internal shape."""
    if "tool_name" in data and "tool_info" not in data:
        tool_input = data.get("tool_input", {})
        tool_info = {}
        if "file_path" in tool_input:
            tool_info["file_path"] = tool_input["file_path"]
        if "command" in tool_input:
            tool_info["command"] = tool_input["command"]
        if "old_string" in tool_input or "new_string" in tool_input:
            tool_info["file_path"] = tool_input.get("file_path", "")
            tool_info["edits"] = [{"new_string": tool_input.get("new_string", "")}]
        if "content" in tool_input:
            tool_info["file_path"] = tool_input.get("file_path", "")
            tool_info["edits"] = [{"new_string": tool_input.get("content", "")}]
        data["tool_info"] = tool_info
        data["agent_action_name"] = data.get("hook_event_name", data.get("tool_name", ""))
    return data


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
    try:
        data = json.load(sys.stdin)
        data = _normalize_hook_input(data)
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    command = data.get("tool_info", {}).get("command", "")
    if not command:
        sys.exit(0)

    findings = check_command(command)
    if findings:
        msg = "BLOCKED: Dangerous command detected:\n"
        msg += f"  Command: {command[:200]}\n\n"
        msg += "  Reasons:\n"
        for category, description in findings:
            msg += f"    - [{category}] {description}\n"
        msg += "\nThis command may cause irreversible damage. Review and run manually if intended."
        print(msg, file=sys.stderr)
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()