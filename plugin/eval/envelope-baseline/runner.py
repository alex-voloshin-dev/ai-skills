#!/usr/bin/env python3
"""G7 envelope regression baseline runner (audit §WP-4.3).

For each *.json fixture in this directory, simulate a PreToolUse:Write hook
event carrying the envelope as `tool_input.content`. Pipe to
`plugin/hooks/scripts/block-secrets-in-code.py` and verify the hook exits 0
(allow). Any exit code 2 means the secrets regex is over-tightening and
re-introducing the audit §2.6 false-positive on valid G7 envelopes.

Each fixture is exercised twice:
1. Path inside `.ai-skills-memory/sessions/<sid>/team-envelopes/` — must pass
   via the ENVELOPE_PATH_PATTERNS allowlist.
2. Path outside the allowlist (`/tmp/scratch-G7.json`) — must pass via the
   content-level `looks_like_json_envelope` detector. This isolates the two
   guard paths and catches a regression where one of them is silently dropped.

Exit 0 = clean. Exit 1 = at least one envelope was blocked or scanned by a
secret pattern. Exit 2 = runner itself failed (IO / import / etc.) so the
caller can distinguish hook regression from runner bug.
"""
from __future__ import annotations

import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent
HOOK = ROOT.parent.parent / "hooks" / "scripts" / "block-secrets-in-code.py"


def run_hook(tool_input: dict) -> tuple[int, str, str]:
    stdin = json.dumps({
        "tool_name": "Write",
        "tool_input": tool_input,
        "session_id": "envelope-baseline-runner",
    })
    proc = subprocess.run(
        [sys.executable, str(HOOK)],
        input=stdin,
        text=True,
        capture_output=True,
        timeout=30,
    )
    return proc.returncode, proc.stdout, proc.stderr


def check_one(fixture: pathlib.Path) -> list[str]:
    """Return list of failure messages (empty list = pass)."""
    failures: list[str] = []
    try:
        envelope_text = fixture.read_text(encoding="utf-8")
        json.loads(envelope_text)  # syntax check
    except (OSError, json.JSONDecodeError) as exc:
        return [f"{fixture.name}: cannot parse — {exc}"]

    # Case 1: write to canonical team-envelopes path (path allowlist guard)
    rc, _, err = run_hook({
        "file_path": f".ai-skills-memory/sessions/abc/team-envelopes/G7-{fixture.stem}.json",
        "content": envelope_text,
    })
    if rc != 0:
        failures.append(
            f"{fixture.name}: BLOCKED on canonical team-envelopes path "
            f"(rc={rc}); ENVELOPE_PATH_PATTERNS allowlist regression. stderr: {err.strip()[:200]}"
        )

    # Case 2: write to off-allowlist path (content-level detector guard)
    rc, _, err = run_hook({
        "file_path": "/tmp/scratch-G7.json",
        "content": envelope_text,
    })
    if rc != 0:
        failures.append(
            f"{fixture.name}: BLOCKED on off-allowlist path "
            f"(rc={rc}); looks_like_json_envelope content-level guard regression. "
            f"stderr: {err.strip()[:200]}"
        )

    return failures


def main() -> int:
    if not HOOK.is_file():
        print(f"ERROR: hook not found at {HOOK}", file=sys.stderr)
        return 2

    fixtures = sorted(p for p in ROOT.glob("*.json"))
    if not fixtures:
        print(f"ERROR: no fixtures found in {ROOT}", file=sys.stderr)
        return 2

    all_failures: list[str] = []
    for fixture in fixtures:
        failures = check_one(fixture)
        if failures:
            all_failures.extend(failures)
            print(f"FAIL  {fixture.name}")
            for f in failures:
                print(f"        {f}")
        else:
            print(f"PASS  {fixture.name}  (both guards cleared)")

    print()
    if all_failures:
        print(f"Result: FAIL — {len(all_failures)} regression(s) across {len(fixtures)} envelopes.")
        return 1
    print(f"Result: PASS — {len(fixtures)}/{len(fixtures)} envelopes cleared both guards.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
