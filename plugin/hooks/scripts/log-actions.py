#!/usr/bin/env python3
"""
ai-skills plugin hook: log-actions
Event: PostToolUse (matcher: .* — covers all tool calls)
Exit code 0 = always allow.

Logs Claude tool activity to the target repo's L4 memory log for traceability.
Log file: .ai-skills-memory/agent-actions.log (cwd-relative, resolves to target repo).
Per 03-MEMORY-ARCHITECTURE.md L4 contract.

Per Round 13 MED-A: refactored from B2 inline _normalize_hook_input duplicate
to use the shared _lib module shipped in B8. PII filter integration added
(per memory-discipline.md long-pending requirement).
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _lib  # noqa: E402


LOG_FILE = os.path.join(".ai-skills-memory", "agent-actions.log")
MAX_LOG_SIZE = 10 * 1024 * 1024


def get_log_entry(data: dict) -> str:
    """Format a log entry from hook input data.

    Per Round 13 MED-A: details fragment is PII-filtered before formatting
    (was deferred per memory-discipline.md note; now closed with _lib import).
    """
    timestamp = data.get("timestamp", _lib.iso_now())
    action = data.get("agent_action_name", data.get("tool_name", "unknown"))
    session_id = data.get("session_id", "")
    execution_id = data.get("execution_id", "")
    tool_info = data.get("tool_info", {})

    details = ""
    # Modern Claude Code event names — match against tool_name OR legacy
    # agent_action_name carried for back-compat.
    name = action.lower() if isinstance(action, str) else ""
    if name in ("write", "edit") or "write_code" in name or "edit" in name:
        file_path = tool_info.get("file_path", "")
        edit_count = len(tool_info.get("edits", []))
        details = f"file={file_path} edits={edit_count}"
    elif name == "bash" or "run_command" in name:
        command = tool_info.get("command", "")
        if len(command) > 200:
            command = command[:200] + "..."
        details = f"cmd={command}"
    elif name == "read" or "read_code" in name:
        file_path = tool_info.get("file_path", "")
        details = f"file={file_path}"
    elif name.startswith("mcp__") or "mcp_tool_use" in name:
        server = tool_info.get("server_name", "")
        tool = tool_info.get("tool_name", "")
        details = f"server={server} tool={tool}"
    else:
        details = json.dumps(tool_info, ensure_ascii=False)[:200]

    # PII filter: redact common secret shapes from details before persisting.
    # Audit log is L4-tier sensitivity; this closes the deferred filter integration.
    redacted_details, _redactions = _lib.apply_pii_filter(details)

    return f"[{timestamp}] {action} | session={session_id} exec={execution_id} | {redacted_details}\n"


def rotate_if_needed(log_path: str) -> None:
    """Rotate log file if it exceeds MAX_LOG_SIZE."""
    try:
        if os.path.exists(log_path) and os.path.getsize(log_path) > MAX_LOG_SIZE:
            rotated = log_path + ".1"
            if os.path.exists(rotated):
                os.remove(rotated)
            os.rename(log_path, rotated)
    except OSError:
        pass


def main():
    data = _lib.read_stdin_json()
    data = _lib.normalize_hook_input(data)

    log_entry = get_log_entry(data)

    try:
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        rotate_if_needed(LOG_FILE)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_entry)
    except OSError:
        pass

    _lib.allow()


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        # Fail-open per failure-recovery rule: never let a buggy hook block all tool use.
        _lib.log_to(
            "hook-errors.log",
            {"ts": _lib.iso_now(), "hook": "log-actions", "error": str(exc)},
        )
        sys.exit(0)
