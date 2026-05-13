#!/usr/bin/env python3
"""
ai-assets plugin hook: block-secrets-in-code
Event: PreToolUse (matcher: Write|Edit)
Exit code 2 = block the write action if secrets are detected; 0 = allow.

Scans file edits for common secret patterns. This is defense in depth,
not a replacement for proper secret management.

Per Round 13 MED-A: refactored from B2 inline _normalize_hook_input duplicate
to use the shared _lib module shipped in B8.
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _lib  # noqa: E402


SECRET_PATTERNS = [
    ("AWS Access Key", re.compile(r"AKIA[0-9A-Z]{16}", re.IGNORECASE)),
    ("AWS Secret Key", re.compile(r"(?i)(aws_secret_access_key|aws_secret)\s*[=:]\s*['\"]?[A-Za-z0-9/+=]{40}")),
    ("Generic API Key", re.compile(r"(?i)(api[_-]?key|apikey)\s*[=:]\s*['\"]?[A-Za-z0-9_\-]{20,}")),
    # Generic Secret narrowed in v0.3.12 (closes audits/2026-05-13 §2.6).
    # Old pattern matched any `token: <8+ chars>` JSON key, false-positiving on
    # G7 envelope fields like `tokens_used: 12345` or `trace_id: "wf-xxx-token-..."`.
    # New pattern requires:
    #   - whole-word keyword (no `tokens_used`, `tokens_in`, `tokens_out`, `trace_id`)
    #   - value length >= 20 (was 8) — short values are almost always counters / flags
    #   - high-entropy alphabet (base64 / hex) — pure decimals are not secrets
    ("Generic Secret", re.compile(
        r"(?i)\b(secret|token|password|passwd|pwd)\b"
        r"(?!s_used|s_in|s_out|s_remaining)"  # exclude G7 envelope metric fields
        r"\s*[=:]\s*['\"]?"
        r"(?=[A-Za-z0-9_\-!@#$%^&*+/=]*[A-Za-z])"  # at least one letter (excludes pure ints)
        r"(?=[A-Za-z0-9_\-!@#$%^&*+/=]*[0-9A-Z])"  # at least one digit or uppercase (entropy)
        r"[A-Za-z0-9_\-!@#$%^&*+/=]{20,}"
    )),
    ("Private Key Block", re.compile(r"-----BEGIN\s+(RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----")),
    ("GitHub Token", re.compile(r"gh[pousr]_[A-Za-z0-9_]{36,}")),
    ("GitHub Fine-Grained PAT", re.compile(r"github_pat_[A-Za-z0-9_]{22,}")),
    ("Google API Key", re.compile(r"AIza[0-9A-Za-z_\-]{35}")),
    ("Slack Token", re.compile(r"xox[bporas]-[0-9a-zA-Z\-]+")),
    ("JWT Token", re.compile(r"eyJ[A-Za-z0-9_\-]+\.eyJ[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+")),
    ("Connection String", re.compile(r"(?i)(mongodb|postgres|mysql|redis|amqp|mssql)://[^\s'\"]{10,}")),
    # Bearer Token narrowed: placeholder-like values (e.g. `bearer <token>`,
    # `bearer ${TOKEN}`, `bearer xxx...`) no longer match.
    ("Bearer Token", re.compile(r"(?i)bearer\s+(?!<|\$\{|xxx|placeholder|your[_-])[A-Za-z0-9_\-\.]{20,}")),
    ("Stripe Key", re.compile(r"[sr]k_live_[A-Za-z0-9]{20,}")),
    ("GitLab Token", re.compile(r"glpat-[A-Za-z0-9_\-]{20,}")),
    ("npm Token", re.compile(r"npm_[A-Za-z0-9]{36,}")),
    ("Encrypted Private Key", re.compile(r"-----BEGIN ENCRYPTED PRIVATE KEY-----")),
]

SKIP_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg", ".webp",
    ".woff", ".woff2", ".ttf", ".eot",
    ".zip", ".tar", ".gz", ".jar", ".war",
    ".lock", ".sum",
    ".min.js", ".min.css",
    ".pyc", ".class", ".o", ".so", ".dll", ".exe",
}

SKIP_FILENAMES = {
    ".env.example", ".env.sample", ".env.template",
    "hooks.json", "package-lock.json", "yarn.lock",
}

# Path allowlist — these locations hold plugin-internal coordination artifacts
# (G7 envelopes, team-channel files, normalized tool outputs) which contain
# fields like `tokens_used`, `trace_id`, etc. that look like secrets to
# pattern-based scanners but never are. v0.3.12 (closes audits/2026-05-13 §2.6).
ENVELOPE_PATH_PATTERNS = [
    re.compile(r"\.ai-assets-memory/"),
    re.compile(r"/team-envelopes/"),
    re.compile(r"(^|/)tmp/.*envelope"),  # /tmp/v22-envelopes/ etc.
    re.compile(r"(^|/)tmp/.*team-"),
]


def should_skip_file(file_path: str) -> bool:
    path_lower = file_path.lower().replace("\\", "/")
    for ext in SKIP_EXTENSIONS:
        if path_lower.endswith(ext):
            return True
    for name in SKIP_FILENAMES:
        if path_lower.endswith("/" + name) or path_lower == name:
            return True
    if "/test" in path_lower and ("fixture" in path_lower or "mock" in path_lower):
        return True
    # v0.3.12: plugin-internal coordination artifacts (G7 envelopes etc.).
    for pat in ENVELOPE_PATH_PATTERNS:
        if pat.search(path_lower):
            return True
    return False


def looks_like_json_envelope(text: str) -> bool:
    """Cheap JSON-content sniff. Content that parses as a JSON object and
    contains G7-envelope-typical keys is plugin coordination data, not code.

    v0.3.12 (closes audits/2026-05-13 §2.6) — adds a content-level fallback
    when the path allowlist alone does not catch a write (e.g., reviewer
    writing to an ad-hoc location). Fail-safe: returns False on any parse
    error, so a malformed-JSON write still gets scanned for secrets.
    """
    text = text.strip()
    if not text.startswith("{"):
        return False
    try:
        import json as _json
        obj = _json.loads(text)
    except (ValueError, TypeError):
        return False
    if not isinstance(obj, dict):
        return False
    g7_marker_fields = {
        "trace_id", "status", "tokens_used", "result",
        "subagent_role", "goal", "constraints", "allowed_tools", "budget",
    }
    return bool(g7_marker_fields & set(obj.keys()))


def scan_for_secrets(text: str) -> list[tuple[str, str]]:
    findings = []
    for name, pattern in SECRET_PATTERNS:
        matches = pattern.findall(text)
        if matches:
            sample = matches[0] if isinstance(matches[0], str) else str(matches[0])
            findings.append((name, sample[:40] + "..." if len(sample) > 40 else sample))
    return findings


def main():
    data = _lib.read_stdin_json()
    data = _lib.normalize_hook_input(data)

    tool_info = data.get("tool_info", {})
    file_path = tool_info.get("file_path", "")
    if should_skip_file(file_path):
        _lib.allow()

    all_findings = []
    for edit in tool_info.get("edits", []):
        new_string = edit.get("new_string", "")
        if not new_string:
            continue
        # v0.3.12 §2.6: skip G7 envelope JSON writes (path allowlist did not
        # catch this path, but content is structured plugin data, not code).
        if looks_like_json_envelope(new_string):
            continue
        all_findings.extend(scan_for_secrets(new_string))

    if all_findings:
        unique = list(set(all_findings))
        msg = f"BLOCKED: Potential secrets detected in {file_path}:\n"
        for name, sample in unique:
            msg += f"  - {name}: {sample}\n"
        msg += "\nUse environment variables or a secrets manager instead of hardcoding secrets."
        print(msg, file=sys.stderr)
        _lib.log_to(
            "errors.log",
            {
                "ts": _lib.iso_now(),
                "severity": "ERROR",
                "hook": "block-secrets-in-code",
                "issue": "secret_pattern_matched",
                "file_path": file_path,
                "patterns": [name for name, _ in unique],
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
            {"ts": _lib.iso_now(), "hook": "block-secrets-in-code", "error": str(exc)},
        )
        sys.exit(0)
