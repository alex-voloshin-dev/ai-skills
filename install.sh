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

echo "Installing AI assets into $HOME_DIR"

# v0.2.0: .claude/ legacy package was removed. Claude Code users should
# install the plugin from ./plugin/ via:
#   claude --plugin-dir "$SCRIPT_DIR/plugin"
# or after publishing:
#   /plugin marketplace add alex-voloshin/ai-assets
#   /plugin install ai-assets@ai-assets
# See plugin/README.md for full install + usage.

sync_dir "$SCRIPT_DIR/.agents" "$HOME_DIR/.agents"
echo "[ok] .agents -> $HOME_DIR/.agents (shared by Codex + Windsurf)"

sync_dir "$SCRIPT_DIR/.codex" "$HOME_DIR/.codex"
echo "[ok] .codex -> $HOME_DIR/.codex"

sync_dir "$SCRIPT_DIR/.windsurf" "$HOME_DIR/.windsurf"
echo "[ok] .windsurf -> $HOME_DIR/.windsurf"

cat <<EONOTE

Note: Claude Code is no longer installed via this script (v0.2.0+).
Use the plugin layout instead:
  claude --plugin-dir "$SCRIPT_DIR/plugin"

EONOTE

echo "Done."
