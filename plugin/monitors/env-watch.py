#!/usr/bin/env python3
"""
ai-skills plugin monitor: env-watch (cross-platform Python rewrite)

Watches the local docker-compose stack and emits one JSON line per
service-state change to stdout, where Claude Code surfaces it as a
notification. Long-running daemon — exits cleanly on SIGTERM/SIGINT.

This file replaces the original bash-only `env-watch.sh` (which was
unusable on Windows hosts without WSL). Functionality is identical;
implementation is pure Python so it runs on Windows, Linux, and macOS
without a bash dependency. The sibling `env-watch.sh` is kept around as
a deprecated shim — `monitors/monitors.json` now points at this `.py`.

Behavior:
  1. Exits silently (rc=0) when the userConfig knob `env_watch_enabled` is not
     truthy. The knob is enabled when its value (after stripping whitespace and
     lowercasing) is one of: "true", "1", "yes", "on". Everything else —
     including absent, "false", "0", "no", "off", "" — keeps the monitor
     disabled. This is intentionally opt-in; the default userConfig value of
     false leaves the monitor off. Runtime env var: CLAUDE_PLUGIN_OPTION_env_watch_enabled
     (legacy fallback: CLAUDE_USER_CONFIG_env_watch_enabled).
  2. Exits silently (rc=0) when no docker-compose.yml / compose.yaml /
     docker-compose.yaml is present in cwd.
  3. Exits silently (rc=0) when `docker` CLI is not on PATH.
  4. Polls `docker compose ps --format json` every N seconds (default
     15, override via userConfig knob `env_watch_interval`; runtime env var:
     CLAUDE_PLUGIN_OPTION_env_watch_interval, legacy fallback:
     CLAUDE_USER_CONFIG_env_watch_interval; min 5).
  5. Diffs current snapshot against previous in-memory snapshot.
     Emits one JSON line per service whose State or Health changed.
  6. Honors SIGTERM (POSIX) and SIGINT (all platforms incl. Windows).

Output line shape (one per state change):
  {"ts":"<iso8601>","monitor":"env-watch","service":"<name>","from":{"state":"...","health":"..."},"to":{"state":"...","health":"..."}}

Failure-recovery rule: any unexpected error must NOT kill the loop.
A persistently broken Docker CLI will produce repeated stderr lines
but will never block the user's session.
"""

from __future__ import annotations

import datetime as _dt
import json
import os
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

COMPOSE_FILES = ("docker-compose.yml", "compose.yaml", "docker-compose.yaml")
MIN_INTERVAL_SEC = 5
DEFAULT_INTERVAL_SEC = 15
DOCKER_TIMEOUT_SEC = 10

# Truthy tokens accepted for the opt-in env var (case-insensitive, stripped).
_TRUTHY: frozenset[str] = frozenset({"true", "1", "yes", "on"})

# Prefix resolution order: canonical first, legacy fallback second.
_PLUGIN_OPTION_PREFIXES = ("CLAUDE_PLUGIN_OPTION_", "CLAUDE_USER_CONFIG_")


def _cfg(key: str, default: str = "") -> str:
    """Read a plugin userConfig knob by bare KEY (stdlib-only, no _lib import).

    Tries CLAUDE_PLUGIN_OPTION_<KEY> first, then CLAUDE_USER_CONFIG_<KEY>
    as a legacy fallback. Returns `default` when neither is set or the value
    is empty/whitespace.
    """
    for prefix in _PLUGIN_OPTION_PREFIXES:
        raw = os.environ.get(prefix + key)
        if raw is not None and raw.strip() != "":
            return raw
    return default


# ---------- Guards ----------

def _opt_in() -> bool:
    return _cfg("env_watch_enabled", "false").strip().lower() in _TRUTHY


def _has_compose_file(cwd: Path) -> bool:
    return any((cwd / f).exists() for f in COMPOSE_FILES)


def _has_docker() -> bool:
    return shutil.which("docker") is not None


def _interval_seconds() -> int:
    raw = _cfg("env_watch_interval", "")
    try:
        n = int(raw) if raw else DEFAULT_INTERVAL_SEC
    except (TypeError, ValueError):
        n = DEFAULT_INTERVAL_SEC
    return max(MIN_INTERVAL_SEC, n)


# ---------- Snapshot ----------

def _iso_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _snapshot() -> dict[str, tuple[str, str]]:
    """Return {service_name: (state, health)} from `docker compose ps`.

    Handles both `docker compose ps --format json` output shapes:
      * a single JSON array (newer docker compose v2)
      * one JSON object per line (older docker compose v2)
    Returns an empty dict on any failure (caller will retry on next tick).
    """
    try:
        proc = subprocess.run(
            ["docker", "compose", "ps", "--format", "json"],
            capture_output=True,
            text=True,
            timeout=DOCKER_TIMEOUT_SEC,
        )
    except (subprocess.SubprocessError, OSError):
        return {}
    if proc.returncode != 0:
        return {}

    raw = (proc.stdout or "").strip()
    if not raw:
        return {}

    items: list[dict] = []
    try:
        parsed = json.loads(raw)
        items = parsed if isinstance(parsed, list) else [parsed]
    except json.JSONDecodeError:
        for line in raw.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                items.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    out: dict[str, tuple[str, str]] = {}
    for it in items:
        if not isinstance(it, dict):
            continue
        name = it.get("Service") or it.get("Name") or ""
        if not name:
            continue
        state = it.get("State") or ""
        health = it.get("Health") or ""
        out[str(name)] = (str(state), str(health))
    return out


def _emit_diffs(prev: dict[str, tuple[str, str]], curr: dict[str, tuple[str, str]]) -> None:
    ts = _iso_now()
    names = sorted(set(prev) | set(curr))
    for name in names:
        p = prev.get(name, ("", ""))
        c = curr.get(name, ("", ""))
        if p == c:
            continue
        event = {
            "ts": ts,
            "monitor": "env-watch",
            "service": name,
            "from": {"state": p[0], "health": p[1]},
            "to": {"state": c[0], "health": c[1]},
        }
        # One JSON line per change. flush so Claude Code sees it immediately.
        sys.stdout.write(json.dumps(event, ensure_ascii=False) + "\n")
        sys.stdout.flush()


# ---------- Signal handling ----------

_should_stop = False


def _request_stop(signum, frame) -> None:  # noqa: ARG001
    global _should_stop
    _should_stop = True


def _install_signal_handlers() -> None:
    # SIGINT works on all platforms incl. Windows.
    try:
        signal.signal(signal.SIGINT, _request_stop)
    except (ValueError, OSError):
        pass
    # SIGTERM is POSIX-only; on Windows this raises and is harmless.
    try:
        signal.signal(signal.SIGTERM, _request_stop)
    except (AttributeError, ValueError, OSError):
        pass


# ---------- Main loop ----------

def main() -> int:
    cwd = Path.cwd()

    if not _opt_in():
        return 0
    if not _has_compose_file(cwd):
        return 0
    if not _has_docker():
        return 0

    interval = _interval_seconds()
    _install_signal_handlers()

    # Seed the previous snapshot so the first poll only emits genuine
    # changes, not the entire initial state.
    prev = _snapshot()

    while not _should_stop:
        # Sleep in 1-second slices so SIGINT / SIGTERM responsiveness stays
        # snappy even with a 60-second interval.
        for _ in range(interval):
            if _should_stop:
                return 0
            time.sleep(1)
        try:
            curr = _snapshot()
            _emit_diffs(prev, curr)
            prev = curr
        except Exception as exc:  # noqa: BLE001
            # Failure-recovery rule: log to stderr, keep the loop alive.
            sys.stderr.write(
                f"env-watch: poll error: {exc!r}\n"
            )
            sys.stderr.flush()

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as exc:  # noqa: BLE001
        # Fail-open: never let the monitor blow up the whole session.
        sys.stderr.write(f"env-watch: fatal: {exc!r}\n")
        sys.exit(0)
