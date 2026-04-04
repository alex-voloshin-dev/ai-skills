#!/usr/bin/env python3
"""
Claude hook: block-sensitive-files
Event: pre_read_code
Exit code 2 = block reading files that may contain secrets or credentials.

Prevents the agent from reading files that are likely to contain secrets,
private keys, or credential material.
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
    try:
        data = json.load(sys.stdin)
        data = _normalize_hook_input(data)
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    file_path = data.get("tool_info", {}).get("file_path", "")
    if not file_path:
        sys.exit(0)

    reason = should_block(file_path)
    if reason:
        msg = "BLOCKED: Cannot read sensitive file.\n"
        msg += f"  File: {file_path}\n"
        msg += f"  Reason: {reason}\n\n"
        msg += "This file may contain secrets or credentials. Access is restricted."
        print(msg, file=sys.stderr)
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
