#!/usr/bin/env python3
"""
ai-skills plugin eval — Tier 2 smoke runner.

Per 02-EVAL-FRAMEWORK.md §11 + Phase 4 #1 (post-v0.1.2).

## What this checks

Tier 2 is the **judge-calibration drift smoke**. For each sampled rubric, it
asks the Haiku judge to score known good + known bad calibration samples,
then verifies the judge's score is within ±0.5 of the expected score
(encoded in the filename: `<scenario>.score-X.X.md`).

This catches three classes of regression:
1. **Rubric drift** — someone edits the rubric in a way that breaks scoring
2. **Judge model drift** — Anthropic ships a new Haiku version that scores
   our samples differently
3. **Sample quality drift** — someone edits a calibration sample so it no
   longer hits its band

## What it does NOT check

- Skill activation precision (which skill triggers on a prompt) — that's a
  separate Tier 2 facet, deferred to a follow-up
- Skill output quality (executor + judge round-trip) — that's Tier 3
- Tool wiring, hook execution, RALF loops — those are Tier 1 lints + live tests

## Token budget (from eval/config.json)

- Soft 50K, hard 150K
- Default sample: 10 rubrics × 2 calibration samples × ~3K tokens = ~60K
- Configurable via --sample-rubrics N and --samples-per-rubric M

## Dependencies

Requires the `anthropic` Python SDK (`pip install anthropic`) and
`ANTHROPIC_API_KEY` env var. Without these, runs in **dry-run mode**:
prints what would be tested but skips actual API calls.

## Usage (via runner.py)

    python3 plugin/eval/runner.py --tier 2
    python3 plugin/eval/runner.py --tier 2 --seed 42 --sample-rubrics 10
    python3 plugin/eval/runner.py --tier 2 --dry-run
"""

from __future__ import annotations

import json
import os
import pathlib
import random
import re
import sys
from dataclasses import dataclass, field
from typing import Optional


# Token budget per eval/config.json (tier_2_smoke)
TIER_2_TOKEN_SOFT_CAP = 50_000
TIER_2_TOKEN_HARD_CAP = 150_000

# Score-band tolerance — judge can be off by this much before we flag drift
SCORE_TOLERANCE = 0.5

# Default Haiku model (per eval/config.json judge_models.default)
DEFAULT_JUDGE_MODEL = "claude-haiku-4-5"

# Filename score regex: matches `.score-4.6.md` or `.score-1.4.md`
SCORE_RE = re.compile(r"\.score-(\d+\.\d+)\.md$")


@dataclass
class Tier2Result:
    rubric: str
    sample_filename: str
    sample_kind: str                  # "good" or "bad"
    expected_score: float
    actual_score: Optional[float]     # None on judge error
    delta: Optional[float]            # None on judge error
    tokens_used: int
    error: Optional[str] = None       # set when judge fails / API unavailable

    @property
    def passed(self) -> Optional[bool]:
        if self.error is not None:
            return None
        if self.delta is None:
            return None
        return self.delta <= SCORE_TOLERANCE


@dataclass
class Tier2Report:
    results: list[Tier2Result] = field(default_factory=list)
    tokens_used_total: int = 0
    api_available: bool = False
    sample_seed: int = 0
    rubrics_sampled: list[str] = field(default_factory=list)

    def passed_count(self) -> int:
        return sum(1 for r in self.results if r.passed is True)

    def failed_count(self) -> int:
        return sum(1 for r in self.results if r.passed is False)

    def errored_count(self) -> int:
        return sum(1 for r in self.results if r.error is not None)


# ---------- Helpers ----------


def _parse_score(filename: str) -> Optional[float]:
    """Extract expected score from `<name>.score-X.X.md`. Returns None on parse fail."""
    m = SCORE_RE.search(filename)
    if not m:
        return None
    try:
        return float(m.group(1))
    except (ValueError, TypeError):
        return None


def _list_rubrics(plugin_root: pathlib.Path) -> list[str]:
    rubrics_dir = plugin_root / "eval" / "judge-rubrics"
    return sorted(p.stem for p in rubrics_dir.glob("*.md"))


def _list_calibration(
    plugin_root: pathlib.Path, rubric: str, kind: str
) -> list[pathlib.Path]:
    d = plugin_root / "eval" / "calibration" / rubric / kind
    if not d.exists():
        return []
    return sorted(d.glob("*.md"))


def _try_anthropic_client():
    """Lazy import. Returns (client, model) or (None, reason)."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None, "ANTHROPIC_API_KEY not set"
    try:
        import anthropic  # type: ignore
    except ImportError:
        return None, "anthropic SDK not installed (run: pip install anthropic)"
    try:
        client = anthropic.Anthropic(api_key=api_key)
    except Exception as e:  # noqa: BLE001
        return None, f"anthropic client init failed: {e!r}"
    return client, DEFAULT_JUDGE_MODEL


def _build_judge_prompt(rubric_text: str, sample_text: str) -> str:
    """Assemble the judge prompt asking for structured score output."""
    return f"""You are an evaluation judge. Score the artifact below against the rubric.

## Rubric

{rubric_text}

## Artifact under evaluation

{sample_text}

## Required output

Return ONLY a JSON object with this exact shape (no markdown, no prose, no commentary):

{{
  "scores": {{
    "dimension_1": <float 1.0-5.0>,
    "dimension_2": <float 1.0-5.0>,
    "dimension_3": <float 1.0-5.0>,
    "dimension_4": <float 1.0-5.0>,
    "dimension_5": <float 1.0-5.0>,
    "dimension_6": <float 1.0-5.0>
  }},
  "overall": <float — average of the 6 dimensions, rounded to 1 decimal>
}}

Use the dimension names from the rubric. Be strict and consistent — score against the level descriptions verbatim, do not be charitable.
"""


def _call_judge(
    client,
    model: str,
    rubric_text: str,
    sample_text: str,
    max_tokens: int = 1500,
    temperature: float = 0.0,
) -> tuple[Optional[float], int, Optional[str]]:
    """Call Haiku judge. Returns (overall_score, tokens_used, error).

    Uses `temperature=0` by default for deterministic scoring — same input
    yields the same score on re-runs (modulo Anthropic-side sampling
    floor). Critical for re-anchor and CI smoke reliability.
    """
    try:
        prompt = _build_judge_prompt(rubric_text, sample_text)
        msg = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}],
        )
        text = "".join(
            block.text for block in msg.content if hasattr(block, "text")
        )
        tokens = (msg.usage.input_tokens or 0) + (msg.usage.output_tokens or 0)
        # Extract JSON — robust against (a) judge wrapping in markdown,
        # (b) judge generating multiple JSON objects (use first), (c) trailing
        # commentary after the JSON block.
        data = None
        # Strategy 1: parse whole text directly
        try:
            data = json.loads(text.strip())
        except json.JSONDecodeError:
            pass
        # Strategy 2: use raw_decode to grab the FIRST valid JSON object,
        # ignoring anything after it. Handles "Extra data" errors where
        # judge generates multiple JSONs.
        if data is None:
            stripped = text.strip()
            decoder = json.JSONDecoder()
            for offset in range(len(stripped)):
                if stripped[offset] != "{":
                    continue
                try:
                    candidate, _end = decoder.raw_decode(stripped[offset:])
                    if isinstance(candidate, dict):
                        data = candidate
                        break
                except json.JSONDecodeError:
                    continue
        if data is None:
            return None, tokens, f"judge returned non-JSON: {text[:200]!r}"
        # Strategy 3: find `overall` at top-level OR nested under `scores`
        # (Haiku sometimes nests it instead of putting at root).
        overall = data.get("overall")
        if not isinstance(overall, (int, float)):
            scores = data.get("scores")
            if isinstance(scores, dict) and isinstance(scores.get("overall"), (int, float)):
                overall = scores["overall"]
        # Strategy 4: if still no overall, compute from per-dimension scores
        if not isinstance(overall, (int, float)):
            scores = data.get("scores", {})
            dim_values = [v for k, v in scores.items() if k != "overall" and isinstance(v, (int, float))]
            if dim_values:
                overall = round(sum(dim_values) / len(dim_values), 1)
        if not isinstance(overall, (int, float)):
            return None, tokens, f"judge returned no 'overall' (or computable from dims): {data}"
        return float(overall), tokens, None
    except Exception as e:  # noqa: BLE001
        return None, 0, f"judge call raised: {e!r}"


# ---------- Main entrypoint ----------


def run(
    plugin_root: pathlib.Path,
    seed: int = 42,
    sample_rubrics: int = 10,
    samples_per_rubric: int = 2,
    dry_run: bool = False,
    only_rubric: Optional[str] = None,
) -> Tier2Report:
    """Run Tier 2 smoke."""
    rng = random.Random(seed)
    report = Tier2Report(sample_seed=seed)

    all_rubrics = _list_rubrics(plugin_root)
    if only_rubric:
        if only_rubric not in all_rubrics:
            print(f"ERROR: rubric {only_rubric!r} not found", file=sys.stderr)
            return report
        sampled = [only_rubric]
    else:
        sampled = rng.sample(all_rubrics, min(sample_rubrics, len(all_rubrics)))
    sampled.sort()
    report.rubrics_sampled = sampled

    if dry_run:
        report.api_available = False
    else:
        client, model_or_reason = _try_anthropic_client()
        if client is None:
            print(
                f"WARN: API unavailable ({model_or_reason}); switching to dry-run mode",
                file=sys.stderr,
            )
            dry_run = True
            report.api_available = False
        else:
            report.api_available = True
            model = model_or_reason

    for rubric in sampled:
        if report.tokens_used_total > TIER_2_TOKEN_HARD_CAP:
            print(
                f"WARN: hard cap {TIER_2_TOKEN_HARD_CAP} tokens reached; stopping",
                file=sys.stderr,
            )
            break

        rubric_path = plugin_root / "eval" / "judge-rubrics" / f"{rubric}.md"
        if not rubric_path.exists():
            continue
        rubric_text = rubric_path.read_text(encoding="utf-8")

        # Sample 1 good + 1 bad (or N each per samples_per_rubric/2)
        n_each = max(1, samples_per_rubric // 2)
        chosen: list[tuple[pathlib.Path, str]] = []
        for kind in ("good", "bad"):
            candidates = _list_calibration(plugin_root, rubric, kind)
            if not candidates:
                continue
            picks = rng.sample(candidates, min(n_each, len(candidates)))
            chosen.extend((p, kind) for p in picks)

        for sample_path, kind in chosen:
            expected = _parse_score(sample_path.name)
            if expected is None:
                report.results.append(
                    Tier2Result(
                        rubric=rubric,
                        sample_filename=sample_path.name,
                        sample_kind=kind,
                        expected_score=0.0,
                        actual_score=None,
                        delta=None,
                        tokens_used=0,
                        error="filename score not parseable",
                    )
                )
                continue

            if dry_run:
                report.results.append(
                    Tier2Result(
                        rubric=rubric,
                        sample_filename=sample_path.name,
                        sample_kind=kind,
                        expected_score=expected,
                        actual_score=None,
                        delta=None,
                        tokens_used=0,
                        error="dry-run (skipped API)",
                    )
                )
                continue

            sample_text = sample_path.read_text(encoding="utf-8")
            actual, tokens, error = _call_judge(client, model, rubric_text, sample_text)
            report.tokens_used_total += tokens

            if error is not None:
                report.results.append(
                    Tier2Result(
                        rubric=rubric,
                        sample_filename=sample_path.name,
                        sample_kind=kind,
                        expected_score=expected,
                        actual_score=None,
                        delta=None,
                        tokens_used=tokens,
                        error=error,
                    )
                )
                continue

            delta = abs(actual - expected) if actual is not None else None
            report.results.append(
                Tier2Result(
                    rubric=rubric,
                    sample_filename=sample_path.name,
                    sample_kind=kind,
                    expected_score=expected,
                    actual_score=actual,
                    delta=delta,
                    tokens_used=tokens,
                    error=None,
                )
            )

    return report


def format_report(report: Tier2Report) -> str:
    """Human-readable report."""
    lines = []
    lines.append(f"=== Tier 2 — Judge-Calibration Drift Smoke ===")
    lines.append(f"Sample seed: {report.sample_seed}")
    lines.append(f"Rubrics sampled: {len(report.rubrics_sampled)} ({', '.join(report.rubrics_sampled)})")
    lines.append(f"API available: {report.api_available}")
    lines.append(f"Tokens used: {report.tokens_used_total} (soft {TIER_2_TOKEN_SOFT_CAP}, hard {TIER_2_TOKEN_HARD_CAP})")
    lines.append("")
    for r in report.results:
        if r.error:
            badge = "ERR "
            detail = f"{r.error}"
        elif r.passed:
            badge = "OK  "
            detail = f"expected {r.expected_score:.1f}, got {r.actual_score:.1f} (Δ {r.delta:.2f})"
        else:
            badge = "FAIL"
            detail = f"expected {r.expected_score:.1f}, got {r.actual_score:.1f} (Δ {r.delta:.2f}, tolerance ±{SCORE_TOLERANCE})"
        lines.append(f"  [{badge}] {r.rubric:30s} {r.sample_kind:5s} {r.sample_filename:50s} -- {detail}")
    lines.append("")
    lines.append(
        f"Summary: {report.passed_count()} pass, {report.failed_count()} fail, "
        f"{report.errored_count()} err"
    )
    return "\n".join(lines)
