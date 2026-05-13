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


# Sandbox paths where forced-recursive delete is allowed. v0.3.12 (closes
# audits/2026-05-13 §2.7). Without these, `rm -rf /tmp/hook-test/...`
# inside the plugin's own self-tests gets blocked, forcing the user to fall
# out of the agent into a shell. We still block `rm -rf /` and any path that
# does not start with one of the sandbox prefixes below.
SANDBOX_PATH_PATTERNS = [
    # Match the sandbox root directory OR a path inside it.
    # `/tmp`, `/tmp/`, `/tmp/foo`, `/tmp/foo/bar` all match. `/tmpfoo` doesn't.
    re.compile(r"(?:^|\s)/tmp(?:/[^\s]*)?(?:\s|$)", re.IGNORECASE),
    re.compile(r"(?:^|\s)/var/tmp(?:/[^\s]*)?(?:\s|$)", re.IGNORECASE),
    re.compile(r"(?:^|\s)\$\{?TMPDIR\}?(?:/[^\s]*)?(?:\s|$)", re.IGNORECASE),
    re.compile(r"(?:^|\s)~/\.cache(?:/[^\s]*)?(?:\s|$)"),
    re.compile(r"(?:^|\s)\$HOME/\.cache(?:/[^\s]*)?(?:\s|$)"),
]


def _target_is_sandbox(target: str, sandbox_cwd: str | None) -> bool:
    """Check whether a single rm target resolves to a sandbox path.

    `sandbox_cwd` is the cwd inferred from any preceding `cd <path>` in the
    same shell chain (None if no `cd` was seen, or the cd target was not
    itself a sandbox path). A relative rm target with a sandbox cwd counts
    as a sandbox target — that's the common pattern in the audit:
    `cd /tmp && rm -rf hook-test`.
    """
    # Pad with both leading and trailing space so SANDBOX_PATH_PATTERNS
    # (which anchor on whitespace boundaries) match an isolated target.
    candidate = " " + target + " "
    if any(p.search(candidate) for p in SANDBOX_PATH_PATTERNS):
        return True
    # Relative target inheriting a sandbox cwd
    if sandbox_cwd is not None and not target.startswith("/") and not target.startswith("~"):
        return True
    return False


def _rm_targets_only_sandbox(command: str) -> bool:
    """Return True if every non-flag argument to `rm` lives under a sandbox
    path. Used to gate the Filesystem dangerous-delete findings.

    Tracks `cd <path>` segments in the same shell chain so relative rm
    targets after `cd /tmp` are recognised as sandbox-resident.
    """
    import shlex
    try:
        tokens = shlex.split(command, posix=True)
    except ValueError:
        return False

    sandbox_cwd: str | None = None
    seen_rm = False
    targets: list[str] = []
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        # Reset cwd at shell separator
        if tok in {"&&", "||", ";", "|"}:
            if seen_rm:
                # Multiple rm's separated — only check the first rm's targets.
                break
            i += 1
            continue
        if not seen_rm:
            if tok == "cd" and i + 1 < len(tokens):
                next_tok = tokens[i + 1]
                if any(p.search(" " + next_tok) for p in SANDBOX_PATH_PATTERNS):
                    sandbox_cwd = next_tok
                else:
                    sandbox_cwd = None
                i += 2
                continue
            if tok == "rm" or tok.endswith("/rm"):
                seen_rm = True
            i += 1
            continue
        # collecting rm targets
        if tok.startswith("-"):
            i += 1
            continue
        targets.append(tok)
        i += 1

    if not targets:
        return False
    for tgt in targets:
        if not _target_is_sandbox(tgt, sandbox_cwd):
            return False
    return True


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


RM_SUPPRESSIBLE_DESCRIPTIONS = {
    "Forced recursive delete",
    "Recursive delete from root",  # over-fires on /tmp/x (the (?!\S*\.) quirk)
}


def check_command(command: str) -> list[tuple[str, str]]:
    findings = []
    sandbox_only_rm = _rm_targets_only_sandbox(command)
    for category, pattern, description in DANGEROUS_PATTERNS:
        if not pattern.search(command):
            continue
        # v0.3.12 §2.7: suppress rm-finding when every target is under a
        # sandbox path (/tmp, /var/tmp, ~/.cache, $TMPDIR) — or under a
        # `cd <sandbox>` cwd in the same shell chain. Truly dangerous
        # rm's (no sandbox prefix, no cd prelude) stay blocked.
        if description in RM_SUPPRESSIBLE_DESCRIPTIONS and sandbox_only_rm:
            continue
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
