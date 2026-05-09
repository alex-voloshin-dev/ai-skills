# Evaluation in ai-assets

How the plugin scores workflow outputs and prevents regressions.

> Internal framework lives in `plugin-design/02-EVAL-FRAMEWORK.md`. This doc is the user-facing summary.

## Why eval matters

A workflow that "looked right last time" can silently regress when:
- The underlying model changes (Anthropic ships updates)
- A skill body is edited
- A new agent is added to a multi-agent pipeline
- An upstream dependency (rubric, schema) changes

Eval is the safety net: rubric-scored test cases that surface regressions before they hit users.

## Three tiers

The framework has three tiers, each with its own cost profile:

| Tier | What | LLM calls? | Token budget |
|---|---|---|---|
| **Tier 1 — Linters** | Frontmatter, schema, references, AST, JSON validity | None | 0 |
| **Tier 2 — Smoke** | Sampled skills × sampled prompts; activation precision check | Yes (Haiku) | ~50K soft / 150K hard |
| **Tier 3 — Behavioral** | Full test cases per skill; executor + judge + blind-comparator | Yes (Haiku + Sonnet override) | ~30K soft / 100K hard per skill |

Run them via:

```bash
/eval --tier 1                           # always free; runs on every install
/eval --tier 2                           # daily smoke
/eval --skill feature-design --tier 3    # per-skill behavioral
/eval --all                              # release-gate full suite
/eval --all --resume                     # resume after interruption
```

## How rubrics work

Each rubric (`plugin/eval/judge-rubrics/<name>.md`) defines:
- **Dimensions** (3–6 per rubric) — what to measure
- **Levels** (1–5 per dimension) — descriptors per quality level
- **Pass threshold** — usually average ≥ 4.0
- **Anti-patterns** — auto-fail conditions regardless of dimension scores
- **Judge model** — Haiku for routine, Sonnet for subjective/complex

The plugin ships **45 rubrics** organized as:

### Per-workflow (28)
One rubric per major workflow. The original 10 (`feature-design`, `develop`, `bugfix`, `refactor`, `migrate`, `spike`, `security-audit`, `docs-pack`, `env-analyze`, `ai-assets-init`) plus 4 meta-tools rubrics and the 24-rubric per-skill workflow expansion (audit B coverage push). Live list: `plugin/eval/judge-rubrics/`.

### Per-skill workflow rubrics (additional coverage)
Included in the 28 above — each user-invocable workflow skill has a matched rubric so Tier 2 can score outputs against that skill's contract.

### Cross-cutting (7)
- `humanizer-compliance.md` — text passes the `humanize-content` rule
- `code-quality.md` — code-facing output meets baseline standards
- `security-soundness.md` — no obvious vulnerabilities
- `geo-readiness.md` — public-facing content structured for LLM extraction
- `subagent-handoff-quality.md` — G7 spawn payloads + return contracts followed
- `memory-write-discipline.md` — memory writes follow `memory-discipline.md` rule
- `faithfulness.md` (G5) — output claims grounded in inputs (no hallucination)

## How the judge is calibrated

`/plugin-doctor --calibrate-judge` (opt-in per Round 4 O4) computes Spearman correlation between the judge's scores and known-good/bad reference samples in `plugin/eval/calibration/<rubric>/{good,bad}/`.

If correlation < 0.7, the rubric flips to Sonnet judge until calibration is restored.

Currently ships **270 calibration samples** (3 good + 3 bad per rubric × 45). With this N, calibration is still informational-only; gates use the rubric directly without weighting by Spearman.

## Faithfulness — the special rubric (G5)

The `faithfulness` rubric is special: every workflow that reads project files, tool outputs, or RALF iteration state runs against it. It catches hallucinations that other rubrics miss — well-cited output that includes invented details NOT present in the cited sources.

Auto-fail trigger: `claim-grounding` dimension < 3 = treated as factual hallucination.

## Baselines for regression detection

Capture a baseline at each release tag:

```bash
/eval --baseline v0.1.0
```

Stored at `plugin/eval/baselines/<skill>/v0.1.0.json` (per-skill scorecards). Subsequent runs compare against the baseline; deltas > 0.5 flag as potential regressions.

For project-specific baselines, write to `.ai-assets-memory/.committed/eval-baselines/<release-tag>.json` (allowlist-validated).

## Blind-comparator (Round 3 Q3)

Tier 3 cases that ship a `comparator-prompt` field run a third agent in an isolated subagent context with skills suppressed via instruction. Validates that the executor's output is genuinely better than a vanilla baseline (not just "different").

Suppression compliance probe runs alongside to verify the comparator actually had skills disabled (catches "skills not really suppressed" as a meta-bug).

## When eval blocks vs warns

| Tier | Failure mode | Effect |
|---|---|---|
| Tier 1 | CRITICAL finding | Exit code 1; CI blocks merge |
| Tier 1 | WARNING only | Exit code 2; CI surfaces but doesn't block |
| Tier 2 | Activation drift > threshold | Exit code 1; investigate before release |
| Tier 3 | Rubric score below pass threshold | Exit code 1; release-gate blocks |
| Tier 3 | Anti-pattern matched | Exit code 1 immediately, regardless of score |

## Status (v0.1)

- **Tier 1**: implemented and runnable (`plugin/eval/runner.py`)
- **Tier 2**: spec'd; runner stubbed (returns "not implemented in v0.1")
- **Tier 3**: spec'd; runner stubbed
- **Calibration**: 34 minimal samples shipped; informational-only

Tier 2/3 ship after eval-judge wiring is hardened in Phase 3.

## Related workflows

- [`/eval`](../workflows/feature-design.md) — runs eval tiers
- [`/plugin-doctor`](../workflows/ai-assets-init.md) — calibration mode
- [`/feature-design`](../workflows/feature-design.md) — uses `feature-design.md` rubric internally for RALF gates
- [`/security-audit`](../workflows/security-audit.md) — uses `security-audit.md` rubric
