# Spike Rubric

## Overview

Evaluates `/spike` output — time-boxed exploration producing a SPIKE-REPORT with go/no-go/needs-more-info recommendation. Five dimensions × five levels.

## Dimensions

### Dimension 1: Question Clarity
Spike clearly answers the stated question (or explicitly explains why it cannot).

- **Level 1:** Answer absent or unclear
- **Level 2:** Answer addresses an adjacent question
- **Level 3:** Answer addresses the question directly
- **Level 4:** Answer is direct + caveats stated
- **Level 5:** Answer is direct + caveats stated + scope what remains for follow-up

### Dimension 2: Evidence Quality
Findings backed by data (benchmarks, references, working examples), not opinion.

- **Level 1:** Pure opinion; no data
- **Level 2:** One data point; rest opinion
- **Level 3:** Multiple data points but unsourced
- **Level 4:** Multiple data points sourced; benchmarks reproducible
- **Level 5:** All of L4 + counter-evidence considered + assumptions explicit

### Dimension 3: Completeness
Considered trade-offs and at least one alternative; not just one option presented.

- **Level 1:** Only one option presented; no trade-offs
- **Level 2:** Two options; trade-offs hand-waved
- **Level 3:** Two options; trade-offs explicit
- **Level 4:** Three+ options; trade-offs ranked
- **Level 5:** Three+ options; trade-offs ranked with quantified cost/benefit

### Dimension 4: Feasibility Assessment
If go/no-go, effort estimate is realistic and justified.

- **Level 1:** No effort signal; go/no-go arbitrary
- **Level 2:** Vague effort ("a few weeks")
- **Level 3:** Effort range with low confidence
- **Level 4:** Effort estimate with assumptions stated
- **Level 5:** Effort estimate with assumptions + risks that would change estimate + best/likely/worst scenarios

### Dimension 5: Actionability
Next steps clear (prototype? deep dive? abandon?).

- **Level 1:** No next steps
- **Level 2:** Vague "let's discuss"
- **Level 3:** Named next step
- **Level 4:** Named next step + owner + timeline
- **Level 5:** All of L4 + decision deadline + criteria for revisiting

## Scoring Logic

- **Aggregate:** average of D1–D5
- **Pass threshold:** 4.0
- **Judge model:** Haiku default; Sonnet for spikes touching architecture or security questions

## Anti-Patterns (Auto-Fail)

- Recommends "build it" without considering "buy" or "do nothing"
- Effort estimate is a single point with no uncertainty bound
- Findings rest on the spike author's opinion without external evidence
- No artefact produced (POC missing despite `--poc` flag)
- Time cap exceeded without producing the partial-report fallback

## Calibration Reference

- **Known-good:** `plugin/eval/calibration/spike/good/*`
- **Known-bad:** `plugin/eval/calibration/spike/bad/*`
