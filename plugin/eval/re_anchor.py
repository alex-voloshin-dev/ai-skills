#!/usr/bin/env python3
"""
ai-assets plugin eval — calibration re-anchor utility.

Phase 4 follow-up to Tier 2 v0.1.3. Re-scores all 102 calibration samples
using the current Haiku judge as ground truth, generates a rename plan,
and (with `--apply`) renames `.score-X.X.md` filenames to match actual
judge output.

After re-anchor:
- Tier 2 with tight +/-0.5 tolerance becomes a precise regression detector
  against current judge state.
- Filenames stop being human-aspirational and become judge-anchored.

## Workflow

    # Step 1 — generate rename plan (~$0.30 Haiku, ~5 min for 102 samples)
    python plugin/eval/re_anchor.py --plan-out eval/baselines/re-anchor-2026-04-30.json

    # Step 2 — review the JSON (look for unexpected deltas, judge errors)

    # Step 3 — dry-run apply
    python plugin/eval/re_anchor.py --apply <plan> --dry-run

    # Step 4 — actually rename, skipping direction-flips for manual review
    python plugin/eval/re_anchor.py --apply <plan> --safe-only

## Cost & determinism

- ~102 calls x ~3K tokens each = ~306K tokens total (~$0.30 on Haiku)
- temperature=0 for deterministic scoring
- ~0.5s sleep between calls to avoid rate limits — full pass takes ~5 min
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import pathlib
import re
import sys
import time
from typing import Optional


PLUGIN_ROOT = pathlib.Path(
    os.environ.get("CLAUDE_PLUGIN_ROOT")
    or pathlib.Path(__file__).resolve().parent.parent
)

sys.path.insert(0, str(PLUGIN_ROOT / "eval"))
import tier2  # noqa: E402

SCORE_RE = re.compile(r"\.score-(\d+\.\d+)\.md$")


def _new_filename(old: str, new_score: float) -> str:
    return SCORE_RE.sub(f".score-{new_score:.1f}.md", old)


def run_plan(throttle_sec: float = 0.5) -> Optional[dict]:
    client, model_or_reason = tier2._try_anthropic_client()
    if client is None:
        print(f"ERROR: API unavailable: {model_or_reason}", file=sys.stderr)
        return None
    model = model_or_reason

    rubrics = tier2._list_rubrics(PLUGIN_ROOT)
    plan: dict = {
        "version": 1,
        "ts": _dt.datetime.now(_dt.timezone.utc).isoformat(),
        "model": model,
        "temperature": 0.0,
        "tolerance_after_anchor": 0.5,
        "rubrics_total": len(rubrics),
        "samples_total": 0,
        "renames": [],
        "noops": [],
        "skipped": [],
        "tokens_used_total": 0,
    }

    print(f"Re-anchoring with model={model} temp=0.0 across {len(rubrics)} rubrics", file=sys.stderr)
    print("This will cost ~$0.30 in Haiku credits and take ~5 min.\n", file=sys.stderr)

    for rubric in rubrics:
        rubric_path = PLUGIN_ROOT / "eval" / "judge-rubrics" / f"{rubric}.md"
        if not rubric_path.exists():
            continue
        rubric_text = rubric_path.read_text(encoding="utf-8")

        for kind in ("good", "bad"):
            samples = tier2._list_calibration(PLUGIN_ROOT, rubric, kind)
            for sample_path in samples:
                plan["samples_total"] += 1
                old_score = tier2._parse_score(sample_path.name)
                if old_score is None:
                    plan["skipped"].append({
                        "rubric": rubric, "kind": kind,
                        "filename": sample_path.name,
                        "reason": "filename score not parseable",
                    })
                    continue

                sample_text = sample_path.read_text(encoding="utf-8")
                actual, tokens, error = tier2._call_judge(
                    client, model, rubric_text, sample_text, temperature=0.0
                )
                plan["tokens_used_total"] += tokens

                if error or actual is None:
                    plan["skipped"].append({
                        "rubric": rubric, "kind": kind,
                        "filename": sample_path.name,
                        "reason": error or "judge returned None",
                        "tokens": tokens,
                    })
                    print(
                        f"  [SKIP] {rubric:30s}/{kind:5s} {sample_path.name}: {error}",
                        file=sys.stderr,
                    )
                    time.sleep(throttle_sec)
                    continue

                new_score = round(actual, 1)
                new_filename = _new_filename(sample_path.name, new_score)
                delta = round(new_score - old_score, 2)

                entry = {
                    "rubric": rubric,
                    "kind": kind,
                    "old_filename": sample_path.name,
                    "new_filename": new_filename,
                    "old_score": old_score,
                    "new_score": new_score,
                    "delta": delta,
                    "tokens": tokens,
                }

                if new_filename == sample_path.name:
                    plan["noops"].append(entry)
                    badge = "OK   "
                else:
                    plan["renames"].append(entry)
                    badge = "RENAM"

                print(
                    f"  [{badge}] {rubric:30s}/{kind:5s} {sample_path.name} "
                    f"({old_score:.1f} -> {new_score:.1f}, d {delta:+.2f})",
                    file=sys.stderr,
                )
                time.sleep(throttle_sec)

    return plan


def _is_direction_flip(r: dict) -> bool:
    """Sample crossed bands: good->(<3.0) or bad->(>2.5)."""
    return (r["kind"] == "good" and r["new_score"] < 3.0) or (
        r["kind"] == "bad" and r["new_score"] > 2.5
    )


def apply_plan(
    plan_path: pathlib.Path,
    dry_run: bool = False,
    safe_only: bool = False,
) -> int:
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    all_renames = plan.get("renames", [])

    flipped = [r for r in all_renames if _is_direction_flip(r)]
    safe_renames = [r for r in all_renames if not _is_direction_flip(r)]

    if safe_only:
        renames_to_apply = safe_renames
        print(
            f"Applying {len(safe_renames)} SAFE renames "
            f"(skipping {len(flipped)} direction-flips) from {plan_path.name} "
            f"(dry_run={dry_run})\n",
            file=sys.stderr,
        )
        if flipped:
            print("  Direction-flips deferred (review + replace samples manually):", file=sys.stderr)
            for r in flipped:
                print(
                    f"    {r['rubric']}/{r['kind']}/{r['old_filename']} "
                    f"({r['old_score']:.1f} -> {r['new_score']:.1f})",
                    file=sys.stderr,
                )
            print("", file=sys.stderr)
    else:
        renames_to_apply = all_renames
        print(
            f"Applying {len(all_renames)} renames from {plan_path.name} (dry_run={dry_run})\n",
            file=sys.stderr,
        )

    success, failed = 0, 0
    for r in renames_to_apply:
        rubric, kind = r["rubric"], r["kind"]
        old = PLUGIN_ROOT / "eval" / "calibration" / rubric / kind / r["old_filename"]
        new = PLUGIN_ROOT / "eval" / "calibration" / rubric / kind / r["new_filename"]

        if not old.exists():
            print(f"  [MISS] {old}", file=sys.stderr)
            failed += 1
            continue
        if new.exists() and old.resolve() != new.resolve():
            print(f"  [COLLIDE] target exists: {new}", file=sys.stderr)
            failed += 1
            continue

        if dry_run:
            print(f"  [WOULD] {rubric}/{kind}/{old.name} -> {new.name}", file=sys.stderr)
        else:
            old.rename(new)
            print(f"  [OK   ] {rubric}/{kind}/{old.name} -> {new.name}", file=sys.stderr)
        success += 1

    print(f"\nApply summary: {success} OK / {failed} skipped", file=sys.stderr)
    return 0 if failed == 0 else 2


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="re_anchor.py",
        description="Re-anchor calibration sample filenames to current Haiku judge scores",
    )
    g = parser.add_mutually_exclusive_group(required=True)
    g.add_argument("--plan-out", help="generate rename plan, write JSON to FILE")
    g.add_argument("--apply", help="apply rename plan from FILE")
    parser.add_argument("--dry-run", action="store_true", help="(--apply) preview without renaming")
    parser.add_argument("--safe-only", action="store_true", help="(--apply) skip direction-flips (samples that crossed into wrong band)")
    parser.add_argument("--throttle-sec", type=float, default=0.5, help="sleep between API calls")
    args = parser.parse_args()

    if args.plan_out:
        plan = run_plan(throttle_sec=args.throttle_sec)
        if plan is None:
            return 1
        out = pathlib.Path(args.plan_out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(plan, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"\nPlan written to {out}", file=sys.stderr)
        print(f"  Samples scored: {plan['samples_total']}", file=sys.stderr)
        print(f"  Renames: {len(plan['renames'])}", file=sys.stderr)
        print(f"  No-ops: {len(plan['noops'])}", file=sys.stderr)
        print(f"  Skipped: {len(plan['skipped'])}", file=sys.stderr)
        print(f"  Tokens: {plan['tokens_used_total']}", file=sys.stderr)
        return 0

    if args.apply:
        return apply_plan(pathlib.Path(args.apply), dry_run=args.dry_run, safe_only=args.safe_only)
    return 0


if __name__ == "__main__":
    sys.exit(main())
