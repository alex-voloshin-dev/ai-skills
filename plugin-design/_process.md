# Authoring & Review Process — Plugin Design Maintenance

> **Purpose:** captures process improvements T3, T5, T8 from Round 5. These are NOT design content — they are the methodology for keeping the design correct over time.
>
> **Companion to:** `_glossary.md` (T1, source of truth), `plugin-design-doctor.py` (T6, programmatic checks), `_phase-gate-criteria.md` (T7, explicit gates), `feedback_design_doc_quality.md` (in memory, recurring error patterns).

---

## T3 — Pre-flight checklist BEFORE user review

**Rule:** apply the 10-item checklist from `feedback_design_doc_quality.md` (in memory) BEFORE asking the user for review. Do not ship docs with known-fixable issues for the user to find.

**Practical workflow:**
1. Author edit (one or more)
2. Run `python3 plugin-design-doctor.py` — review output
3. Apply 10-item checklist mentally:
   - Counts match across docs?
   - Glossary entries spelled identically?
   - Cross-doc references resolve?
   - Every requirement / decision addressed?
   - Every "what" has a "how"?
   - Best practices fresh?
   - Capability assumptions verified?
   - Issue ID prefixes don't collide?
   - Atomic items (one deliverable per checklist item)?
   - Math sweeps (totals add up)?
4. Fix anything that fails
5. THEN ship to user for review

**Anti-pattern (we did this 5 rounds in a row):** ship docs to user → user reviews → user finds 12-25 issues → re-ship. Cost: many user-side rounds. Pre-flight catches most issues author-side.

**Expected effect:** future rounds should find ≤5 issues (down from 12-25), and most should be subjective/strategic rather than mechanical.

---

## T5 — Smaller atomic edits with verification gates

**Rule:** edit in batches of ≤5 patches, then verify, then continue. Don't apply 25 patches in one batch (Round 1 anti-pattern).

**Practical workflow:**
1. Identify a coherent batch of 3-5 related patches
2. Apply via Edit tool, one at a time
3. After batch:
   - `grep` to verify the targets actually changed
   - Read the affected sections to verify they make sense in context
   - Run `plugin-design-doctor.py` for changed file area
4. If anything unexpected: STOP, diagnose, fix
5. Then move to next batch

**Why:** large batches accumulate compounding errors. A small mistake in patch 3 of 25 propagates through patches 4-25 and gets attributed wrong in critique. Small batches isolate causes.

**Anti-pattern caught:** Round 5 found `eval/config.json` listed in both B1.7 and B10.4 of migration checklist. Both edits were applied as part of large batches without re-reading the surrounding context.

---

## T8 — Iterative authoring with feedback loop

**Rule:** for new docs, author ONE doc → pre-flight → next doc. Don't author all 7 docs and review at the end.

**Practical workflow:**
1. Author doc 1 (e.g., `01-WORKFLOW-SPECS.md`)
2. Run `plugin-design-doctor.py` against the partial set (just `00`, `00a`, `01`)
3. Apply 10-item checklist
4. Fix anything found
5. THEN start doc 2

**Why:** errors in doc 1 propagate into doc 2, doc 3 if not caught early. By Round 3 the docs were authored simultaneously by 3 parallel agents, then reviewed together. Errors compounded.

**Trade-off:** iterative is slower in raw author-time but catches errors when they're cheap. Total time including review rounds is shorter.

---

## How these complement each other

| Improvement | Catches what kind of error |
|---|---|
| T1 glossary | terminology drift, count drift, naming collisions |
| T3 pre-flight | mechanical errors, math, refs, completeness |
| T5 small batches | cascade failures, mis-attributed bugs |
| T6 doctor script | leaks, forbidden fields, namespace, programmatic checks |
| T7 phase gates | "complete" without explicit criteria, premature shipping |
| T8 iterative | errors in early docs propagating to later |

T2 (critic subagent) and T4 (re-fetch upstream) are EVENT-driven (run at phase boundaries), not continuous.

---

## When to skip parts of this process

This process is calibrated for HIGH-stakes docs (Phase 1 design has 5571 lines, will guide months of implementation). For low-stakes work:

- Ad-hoc small edits: T3 + T5 only
- Quick research note: T3 only
- Refactor of one section: T1 update + T3 + T6
- New phase: ALL of T1-T8

For Phase 2 implementation (writing plugin code), additional process applies:
- Test-driven where possible (write eval case, then implement skill)
- Branch per batch from `04-MIGRATION-CHECKLIST.md`
- Per-batch validation per the checklist
- T6 doctor runs in CI on every PR

---

## Calibrating to "good enough"

Diminishing returns are real. After 5 rounds of self-review:
- Round 1: 25 patches (P1-P25)
- Round 2: ~22 issues across F/H/M sections
- Round 3: 14 issues (Q1-Q4 + G1-G10)
- Round 4: 12 issues (N1-N6 + O1-O4 + P1-P2)
- Round 5: 11 issues (S1-S11) but ~70% mechanical, increasingly subjective

If a round finds <5 issues AND none are HIGH severity AND `plugin-design-doctor.py --strict` exits 0, declare the docs "good enough" for the current phase. Continue improving in subsequent phases when the docs naturally evolve.

Don't chase asymptote of zero issues — the docs have to ship.
