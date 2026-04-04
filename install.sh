#!/usr/bin/env bash

set -euo pipefail

HOME_DIR="${1:-${HOME:-}}"
if [ -z "$HOME_DIR" ]; then
  echo "Home directory is not set. Pass it as the first argument." >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

sync_dir() {
  local src="$1"
  local dst="$2"

  if [ ! -d "$src" ]; then
    echo "Source directory not found: $src" >&2
    exit 1
  fi

  mkdir -p "$dst"

  while IFS= read -r src_file; do
    rel="${src_file#"$src"/}"
    mkdir -p "$(dirname "$dst/$rel")"
    cp -f "$src_file" "$dst/$rel"
  done < <(find "$src" -type f \
    ! -path '*/__pycache__/*' \
    ! -name 'settings.local.json' \
    ! -name '*.pyc' \
    ! -name '*.pyo')

  while IFS= read -r dst_file; do
    rel="${dst_file#"$dst"/}"
    if [ ! -f "$src/$rel" ]; then
      case "$dst_file" in
        *.sqlite|*.sqlite-shm|*.sqlite-wal|*.log) continue ;;
      esac
      rm -f "$dst_file"
    fi
  done < <(find "$dst" -type f)

  find "$dst" -depth -type d -empty -exec rmdir {} \; 2>/dev/null || true
}

patch_claude_home_settings() {
  local claude_home="$1"
  local settings="$claude_home/settings.json"
  [ -f "$settings" ] || return 0

  python3 - "$claude_home" <<'PY'
import json
import sys
from pathlib import Path

claude_home = Path(sys.argv[1]).resolve()
script_dir = claude_home / "hooks" / "scripts"

command_map = {
    "log-actions.py": f'python3 "{script_dir.as_posix()}/log-actions.py"',
    "block-secrets-in-code.py": f'python3 "{script_dir.as_posix()}/block-secrets-in-code.py"',
    "block-dangerous-commands.py": f'python3 "{script_dir.as_posix()}/block-dangerous-commands.py"',
    "block-sensitive-files.py": f'python3 "{script_dir.as_posix()}/block-sensitive-files.py"',
}

def rewrite_commands(obj):
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key == "command" and isinstance(value, str):
                for needle, replacement in command_map.items():
                    if needle in value:
                        obj[key] = replacement
                        break
            else:
                rewrite_commands(value)
    elif isinstance(obj, list):
        for item in obj:
            rewrite_commands(item)

for relative in ("settings.json", "hooks/configs/logging-hooks.json", "hooks/configs/security-hooks.json"):
    path = claude_home / relative
    if not path.exists():
        continue
    data = json.loads(path.read_text(encoding="utf-8"))
    rewrite_commands(data)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
PY
}

echo "Installing AI assets into $HOME_DIR"

sync_dir "$SCRIPT_DIR/.claude" "$HOME_DIR/.claude"
echo "[ok] .claude -> $HOME_DIR/.claude"

sync_dir "$SCRIPT_DIR/.agents" "$HOME_DIR/.agents"
echo "[ok] .agents -> $HOME_DIR/.agents"

sync_dir "$SCRIPT_DIR/.codex" "$HOME_DIR/.codex"
echo "[ok] .codex -> $HOME_DIR/.codex"

sync_dir "$SCRIPT_DIR/.windsurf" "$HOME_DIR/.windsurf"
echo "[ok] .windsurf -> $HOME_DIR/.windsurf"

patch_claude_home_settings "$HOME_DIR/.claude"
echo "[ok] patched ~/.claude hook commands for global runtime"

echo "Done."
