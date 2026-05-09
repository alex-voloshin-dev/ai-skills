# Ralph Rubric

## Overview

Evaluates `/ralph` — standalone RALF (Read-Act-Learn-Feedback) iteration loop. Wraps a task in a feedback loop with a mechanically-verifiable oracle and runaway-detection kill rules. Six dimensions × five levels.

## Dimensions

### Dimension 1: Oracle Correctness
`--oracle` is mechanically verifiable: a test command, schema validation, regex match, or equivalent binary check. Subjective phrasing ("looks good", "seems right") is disallowed.

- **Level 1:** Oracle is subjective ("code looks good", "user likes it")
- **Level 2:** Oracle references a check but is paraphrased ("tests pass" with no command)
- **Level 3:** Oracle is a command but ambiguous (`pytest` without scope filter)
- **Level 4:** Oracle is a precise mechanical check (`cargo test --quiet -- contract::`) with binary exit
- **Level 5:** All of L4 + oracle includes negative-case guard (also fails when expected)

### Dimension 2: Kill-On Rules
`--kill-on` covers runaway detection. At minimum: no-progress, token-spike, repeat-error.

- **Level 1:** No kill-on rules
- **Level 2:** One rule (e.g., max-iter only)
- **Level 3:** Two rules; gaps remain (no token-spike guard)
- **Level 4:** All three rules wired with thresholds (no-progress=2, token-spike=2x, repeat-error=3)
- **Level 5:** All of L4 + thresholds justified against task class (refactor vs greenfield)

### Dimension 3: Cap Discipline
Respects `userConfig.ralph_session_*` token + iteration caps. Pauses for explicit user approval before exceeding.

- **Level 1:** Caps ignored or unknown
- **Level 2:** Cap referenced; exceeded silently
- **Level 3:** Cap respected; no pause point declared mid-run
- **Level 4:** Cap respected; pause-for-approval handshake when 80% consumed
- **Level 5:** All of L4 + per-iter cost projection shown so user can decide before commit

### Dimension 4: Init vs Continuation Prompts
First iteration uses init prompt; iter ≥ 2 uses the G10 continuation-prompt template (token savings; no full-context replay).

- **Level 1:** Same full prompt re-sent every iteration
- **Level 2:** Continuation hint added but full context still replayed
- **Level 3:** Continuation prompt used inconsistently
- **Level 4:** G10 continuation-prompt template used from iter 2 onward; >50% token saving demonstrated
- **Level 5:** All of L4 + delta-only context (failed assertion + last patch + oracle output) per iter

### Dimension 5: Per-Iteration Telemetry
`tokens.json` written per iteration to `.ai-assets-memory/ralph/<run-id>/iter-NNN/`. Captures input/output/cache tokens + duration + oracle exit code.

- **Level 1:** No telemetry written
- **Level 2:** Aggregate totals only at end of run
- **Level 3:** Per-iter telemetry written but missing fields (no oracle exit)
- **Level 4:** Per-iter `tokens.json` complete (input/output/cache/duration/oracle exit)
- **Level 5:** All of L4 + machine-parseable schema versioned + cross-run aggregator note

### Dimension 6: Convergence Transparency
Final report shows oracle status + iteration count + token totals + termination reason (converged / killed / cap hit).

- **Level 1:** Final report missing or "done"
- **Level 2:** Status only; no iter count or tokens
- **Level 3:** Status + iter count; tokens missing
- **Level 4:** Oracle status + iter count + token totals + termination reason
- **Level 5:** All of L4 + per-iter trend (oracle proximity, error decreasing) summarized

## Scoring Logic

- **Aggregate:** average of D1–D6
- **Pass threshold:** 4.0
- **Judge model:** Haiku for routine loops; Sonnet for novel oracles or runaway-suspect runs

## Anti-Patterns (Auto-Fail)

- Subjective oracle ("looks good", "seems right")
- Loop ran past `userConfig.ralph_session_*` caps without user approval
- No kill-on rules at all
- Telemetry not written per iteration
- Final report omits termination reason

## Calibration Reference

- **Known-good:** `plugin/eval/calibration/ralph/good/*`
- **Known-bad:** `plugin/eval/calibration/ralph/bad/*`
