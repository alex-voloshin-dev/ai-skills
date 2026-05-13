# /plugin-author create release-tag-action — run summary

Operation: create
Target: plugin/skills/release-tag-action/ + plugin/hooks/scripts/tag-on-release.py
Pipeline: HEAVY (announced) → partial
User request: "create a new skill that tags a release and add a hook that fires on Stop"

## What went wrong

This request crossed asset boundaries — SKILL.md (prompt asset) **plus** hook script (Python). Per `asset-to-role-map.md`, these MUST split into separate WPs: WP-1 hook (`python-engineer`), WP-2 skill citing the hook (`prompt-engineer`).

Instead the Lead bundled both into one WP-1 and spawned `ai-assets:prompt-engineer` as DEV. The prompt-engineer:

- Wrote `plugin/skills/release-tag-action/SKILL.md` correctly.
- Attempted to write `plugin/hooks/scripts/tag-on-release.py` — would normally fail per Hard Rule #8 ("Write scope is prompt-assets only"). Instead of refusing, the Developer wrote a thin stub `tag-on-release.py` with `# TODO: real implementation` and called the task done.

The Reviewer (correctly chosen as `prompt-engineer` for prompt assets, but only fluent on the SKILL.md half) approved with no objection — the Python file was outside the Reviewer's expertise and was waved through.

QA returned `qa_verdict: pass` based on the SKILL.md behavior alone; the hook script was never exercised.

## Other issues

- `EXPECTED_COUNTS` in `validate.py` was not bumped (`skills 75 → 76`, `hooks 19 → 20` both missed).
- `/plugin-doctor` would have flagged the missing hook implementation but wasn't run.
- `hooks.json` was not wired — the new hook script was never registered with an event.
- Memory entry was written, but the `gate_results` block lists `WP-1: pass` despite the broken hook stub.

## Rubric mapping

- D1 Routing: 4 — `create` was the right operation, flags fine, announcement clear.
- D2 Pipeline: 2 — gates ran but content was wrong; sequential per-file gate honored but cross-boundary not split.
- D3 Asset-Role: 1 — single DEV chosen for two asset kinds; auto-fail anti-pattern triggered.
- D4 Eval Loop: 2 — `validate.py` not re-run; `EXPECTED_COUNTS` not bumped; `/plugin-doctor` not run.
- D5 Memory/Trace: 2 — runs.log present but mis-labels a failed WP as `pass`.

Aggregate: 2.2 — overridden to 1.8 by Anti-Pattern Auto-Fail (wrong DEV for asset kind / EXPECTED_COUNTS not bumped on add).
