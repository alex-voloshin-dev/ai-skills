#!/usr/bin/env bash
# Thin wrapper: run the local validator from any cwd.
# Usage:  bash plugin/dev/check.sh [--quiet] [--json] [--strict]

set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$DIR/validate.py" "$@"
