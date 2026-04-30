#!/usr/bin/env python3
"""
ai-assets plugin hook: block-sensitive-files
Event: PreToolUse (matcher: Read)
Exit code 2 = block reading files that may contain secrets or credentials; 0 = allow.

Prevents the agent from reading files that are likely to contain secrets,
private keys, or credential material.

Per Round 13 MED-A: refactored from B2 inline _normalize_hook_input duplicate
to use the shared _lib module shipped in B8.
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _lib  # noqa: E402


BLOCKED_FILENAMES = {
    ".env",
    ".env.local",
    ".env.production",
    ".env.staging",
    ".env.development",
    ".env.prod",
    ".env.dev",
    ".env.stg",
    "credentials",
    "credentials.json",
    "service-account.json",
    "service-account-key.json",
    "keystore.jks",
    "truststore.jks",
    ".pgpass",
    ".my.cnf",
    ".netrc",
    ".npmrc",
    ".pypirc",
    ".docker/config.json",
    "gcloud-service-key.json",
}

BLOCKED_PATTERNS = [
    re.compile(r"^\.env\.", re.IGNORECASE),
    re.compile(r"id_rsa", re.IGNORECASE),
    re.compile(r"id_ed25519", re.IGNORECASE),
    re.compile(r"id_ecdsa", re.IGNORECASE),
    re.compile(r"id_dsa", re.IGNORECASE),
    re.compile(r"\.pem$", re.IGNORECASE),
    re.compile(r"\.key$", re.IGNORECASE),
    re.compile(r"\.p12$", re.IGNORECASE),
    re.compile(r"\.pfx$", re.IGNORECASE),
    re.compile(r"\.jks$", re.IGNORECASE),
    re.compile(r"secret[s]?\.ya?ml$", re.IGNORECASE),
    re.compile(r"vault\.ya?ml$", re.IGNORECASE),
    re.compile(r".*password.*\.txt$", re.IGNORECASE),
    re.compile(r".*credential.*", re.IGNORECASE),
    re.compile(r"\.htpasswd$", re.IGNORECASE),
]

BLOCKED_DIRS = {
    ".ssh",
    ".gnupg",
    ".aws",
    ".gcloud",
    ".azure",
    ".kube",
}

ALLOW_LIST = {
    ".env.example",
    ".env.sample",
    ".env.template",
    "credentials.example",
    "secrets.example.yaml",
    "secrets.example.yml",
}


def get_basename(file_path: str) -> str:
    return file_path.replace("\\", "/").rstrip("/").rsplit("/", 1)[-1]


def get_path_parts(file_path: str) -> list[str]:
    return file_path.replace("\\", "/").lower().split("/")


def should_block(file_path: str) -> str | None:
    basename = get_basename(file_path)
    basename_lower = basename.lower()
    path_parts = get_path_parts(file_path)

    if basename_lower in ALLOW_LIST:
        return None
    if basename_lower in {f.lower() for f in BLOCKED_FILENAMES}:
        return f"Sensitive file: {basename}"
    for pattern in BLOCKED_PATTERNS:
        if pattern.search(basename):
            return f"Matches sensitive pattern: {pattern.pattern}"
    for part in path_parts:
        if part in BLOCKED_DIRS:
            return f"Inside sensitive directory: {part}/"
    return None


def main():
    data = _lib.read_stdin_json()
    data = _lib.normalize_hook_input(data)

    file_path = data.get("tool_info", {}).get("file_path", "")
    if not file_path:
        _lib.allow()

    reason = should_block(file_path)
    if reason:
        msg = "BLOCKED: Cannot read sensitive file.\n"
        msg += f"  File: {file_path}\n"
        msg += f"  Reason: {reason}\n\n"
        msg += "This file may contain secrets or credentials. Access is restricted."
        print(msg, file=sys.stderr)
        _lib.log_to(
            "errors.log",
            {
                "ts": _lib.iso_now(),
                "severity": "ERROR",
                "hook": "block-sensitive-files",
                "issue": "sensitive_file_read_blocked",
                "file_path": file_path,
                "reason": reason,
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
            {"ts": _lib.iso_now(), "hook": "block-sensitive-files", "error": str(exc)},
        )
        sys.exit(0)
