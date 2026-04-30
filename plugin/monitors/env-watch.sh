#!/usr/bin/env bash
# DEPRECATED — kept only for users who explicitly want a POSIX-shell
# version of the monitor (e.g., minimal Linux containers without Python).
#
# The canonical monitor since alpha.19 is monitors/env-watch.py
# (cross-platform Python; Windows-, Linux-, and macOS-compatible).
# `monitors/monitors.json` points at the .py implementation.
#
# This shim does nothing on its own — `monitors.json` will not invoke it.
# To switch back to the bash version, edit `monitors.json` and replace
# the `command` field with: ${CLAUDE_PLUGIN_ROOT}/monitors/env-watch.sh
# (Note: requires real bash on PATH; on Windows this means Git Bash or
# WSL2, NOT the WSL stub that ships with Windows by default.)
#
# The original implementation lives in this file's git history (alpha.16).

set -euo pipefail
exec python3 "$(dirname "$0")/env-watch.py" "$@"
