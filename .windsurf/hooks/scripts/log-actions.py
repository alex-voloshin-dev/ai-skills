#!/usr/bin/env python3
"""
Windsurf hook: log-actions
Events: post_write_code, post_run_command, post_read_code, post_mcp_tool_use
Exit code 0 = always allow.

Logs Cascade tool activity to a local audit log file for traceability.
Log file: .windsurf/agent-actions.log.
"""

import json
import os
import sys
from datetime import datetime, timezone


def _normalize_hook_input(data: dict) -> dict:
    """Normalize Windsurf hook payloads into a single internal shape."""
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


LOG_FILE = os.path.join(".windsurf", "agent-actions.log")
MAX_LOG_SIZE = 10 * 1024 * 1024


def get_log_entry(data: dict) -> str:
    """Format a log entry from hook input data."""
    timestamp = data.get("timestamp", datetime.now(timezone.utc).isoformat())
    action = data.get("agent_action_name", data.get("tool_name", "unknown"))
    session_id = data.get("session_id", "")
    execution_id = data.get("execution_id", "")
    tool_info = data.get("tool_info", {})

    details = ""
    if "write_code" in action:
        file_path = tool_info.get("file_path", "")
        edit_count = len(tool_info.get("edits", []))
        details = f"file={file_path} edits={edit_count}"
    elif "run_command" in action:
        command = tool_info.get("command", "")
        if len(command) > 200:
            command = command[:200] + "..."
        details = f"cmd={command}"
    elif "read_code" in action:
        file_path = tool_info.get("file_path", "")
        details = f"file={file_path}"
    elif "mcp_tool_use" in action:
        server = tool_info.get("server_name", "")
        tool = tool_info.get("tool_name", "")
        details = f"server={server} tool={tool}"
    else:
        details = json.dumps(tool_info, ensure_ascii=False)[:200]

    return f"[{timestamp}] {action} | session={session_id} exec={execution_id} | {details}\n"


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
    try:
        data = json.load(sys.stdin)
        data = _normalize_hook_input(data)
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    log_entry = get_log_entry(data)

    try:
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        rotate_if_needed(LOG_FILE)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_entry)
    except OSError:
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
