# Faithfulness Rubric (G5)

## Overview

Evaluates whether output claims are SUPPORTED by retrieved/provided context (not invented). Faithfulness is distinct from quality and from citation correctness — a workflow can produce well-cited output that includes invented details NOT present in the cited source.

Applied to every workflow that reads project files, tool outputs, or operates on RALF iterations (improvements must be grounded in last-iteration error, not invented).

## Dimensions

### Dimension 1: Claim Grounding
Every non-trivial claim traces to a specific source (file path + line, tool call_id + excerpt, or prior iteration diff).

- **Level 1:** Most claims have no source; output is largely free-floating
- **Level 2:** Some claims sourced, many unsupported
- **Level 3:** Most claims sourced; a handful unsupported
- **Level 4:** All non-trivial claims sourced with file:line or tool call_id references
- **Level 5:** All claims sourced AND each source quote is reproduced verbatim with span identifier (line range)

### Dimension 2: No Invention
Output does NOT introduce facts, values, or code not present in any input.

- **Level 1:** Output invents core facts (function names, API surfaces, values that don't exist)
- **Level 2:** Output invents minor details (one or two fabricated values, function signatures)
- **Level 3:** Output stays grounded but extrapolates beyond inputs without flagging
- **Level 4:** Output stays strictly grounded; extrapolations explicitly flagged
- **Level 5:** Strict grounding; extrapolations flagged AND uncertainty quantified

### Dimension 3: Quote Fidelity
When output paraphrases or quotes input, it matches the source.

- **Level 1:** Misquotes or distorts source meaning
- **Level 2:** Paraphrases drift from source intent
- **Level 3:** Paraphrases preserve intent; minor word substitutions
- **Level 4:** Paraphrases faithful; direct quotes verbatim
- **Level 5:** Direct quotes verbatim with span identifier; paraphrases marked as such

### Dimension 4: Inference Labelling
When output goes BEYOND inputs (synthesis, extrapolation), the inference is explicitly labelled.

- **Level 1:** Inferences presented as facts without labelling
- **Level 2:** Some inferences labelled; many presented as facts
- **Level 3:** Most inferences labelled; a few not
- **Level 4:** All inferences labelled (e.g., "inferred from the test pattern", "extrapolated from prior runs")
- **Level 5:** Inferences labelled AND confidence level stated

### Dimension 5: Hallucinated Tool Args Absence
For code that invokes tools, args are grounded in observed schema, not invented.

- **Level 1:** Tool calls invent arg names, types, or values not in schema
- **Level 2:** Tool calls use mostly observed args, one or two invented
- **Level 3:** Tool calls grounded; minor speculation on optional args
- **Level 4:** Tool calls strictly grounded in observed schema
- **Level 5:** Tool calls strictly grounded AND output validates against schema before invocation

## Scoring Logic

- **Aggregate:** average of D1–D5
- **Pass threshold:** 4.0
- **CRITICAL: claim-grounding (D1) < 3 = AUTO-FAIL** regardless of other dimensions (treated as factual hallucination, severe)
- **Judge model:** Sonnet by default (subjective faithfulness checks weak on Haiku in calibration assumption); Haiku only after per-rubric calibration verifies Spearman ≥ 0.8

## Anti-Patterns (Auto-Fail)

- Code references function/class names that don't exist in inputs
- Output cites a file:line that doesn't exist
- Tool call uses arguments not in the tool's schema
- Output asserts data values not present in any provided context
- Output reproduces a "quote" that doesn't match any source

## Calibration Reference

- **Known-good:** `plugin/eval/calibration/faithfulness/good/*` (B10a)
- **Known-bad:** `plugin/eval/calibration/faithfulness/bad/*` (B10a)
