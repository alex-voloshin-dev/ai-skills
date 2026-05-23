# Calibration (bad) — over-cap, no front-matter, mixed topics · score 1.8

## Run output

```
/knowledge-sync
Config baseline m1n2o3p.
Git delta: src/** (large refactor, 38 files).
Area map: tech-docs ← src/** → AFFECTED.
Fan-out: content-writer ×1 [tech-docs].
  return: ok — knowledge/tech-docs/Everything.md written:
    - 4280 words (over the 3000 hard cap; NOT split)
    - no YAML front-matter block at all (no title/area/last_reviewed/source_refs)
    - filename "Everything.md" (not kebab-case)
    - mixes three topics in one file: auth, billing, and the deploy runbook
Pre-write gates: (no KB-hygiene conformance check ran)
Update policy: propose → PR #240 (draft).
Baseline advanced.
Done.
```

## Why 1.8
- D7 Conventions **1** (release blocker) — every conventions rule violated: over the 3000-word hard cap with NO split, missing the entire front-matter floor, non-kebab filename, three topics in one doc. The strict KB-hygiene gate should have blocked or split this; it did not run.
- D3 Doc quality **2** — a single sprawling multi-topic dump harms indexability/accessibility (the whole point of the internal KB).
- D4 Safety **3** — draft PR used (no main commit), so not a safety blocker; but the doc still should not have been written under strict enforcement.
- D5 Wrapping **3** — assume diff wrapped (not the failure here).
- D1 **3**, D2 **4**, D6 **3**.
Fails D7 (=1 < 4) — blocker. Score 1.8.
