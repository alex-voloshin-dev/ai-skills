# Phase-Gate Criteria — Explicit Pass/Fail per Phase

> **Purpose (T7 from Round 5):** make "phase complete" a verifiable claim, not a feeling. After 5 rounds of "Phase 1 design complete" being declared and then re-found incomplete, this doc defines specific criteria each phase MUST pass before moving on.
>
> **Verification:** every criterion is either checked by `plugin-design-doctor.py` (programmatic) or has a manual checkbox a human walks through.

---

## Phase 1 — Design Complete

This is the phase we're currently in. To declare DONE, ALL of the following must pass:

### Programmatic (run `plugin-design-doctor.py --strict`)

- [ ] **C1.** All 7 design docs present (00, 00a, 01, 02, 03, 04, 05) plus `_glossary.md`, `plugin-design-doctor.py`, `_phase-gate-criteria.md`, `_process.md` (this set = 11 files)
- [ ] **C2.** `plugin-design-doctor.py --check leaks --strict` exits 0 (no friendly4ai or personal info leaks)
- [ ] **C3.** `plugin-design-doctor.py --check forbidden --strict` exits 0 (no plugin agent has `permissionMode`/`hooks`/`mcpServers` set in actual frontmatter; before/after examples are exempt)
- [ ] **C4.** `plugin-design-doctor.py --check glossary --strict` exits 0 (glossary present, has correct header)
- [ ] **C5.** `plugin-design-doctor.py --check counts` reports 0 errors (warnings expected for contextual mentions; review each)
- [ ] **C6.** `plugin-design-doctor.py --check refs` exits 0 (every cross-doc reference resolves)
- [ ] **C7.** `plugin-design-doctor.py --check namespace` reports 0 errors (issue ID prefixes match glossary §10 reservations)

### Manual (walk through)

- [ ] **M1.** Glossary §1 counts (skills/agents/rules/hooks/rubrics) match plan §7b counts table
- [ ] **M2.** Glossary §2 skill list (52 entries) matches plan §2.1 disposition (sum of KEEP+REFACTOR+MERGE-output+NEW = 52)
- [ ] **M3.** Glossary §3 agent list (26 entries) matches plan §2.2
- [ ] **M4.** Every workflow in `01-WORKFLOW-SPECS.md` Part A has a corresponding skill in glossary (whether KEEP/REFACTOR/NEW)
- [ ] **M5.** Every issue ID in `00a-CRITIQUE-AND-CORRECTIONS.md` uses a prefix listed in glossary §10
- [ ] **M6.** Every locked decision (D1-D13) in plan §0 still has a `Locked` status (no decision moved to "RESOLVED" or "deferred" without flagging)
- [ ] **M7.** All 13 "patches applied" tables in critique (P, U, etc.) have target-file paths that exist
- [ ] **M8.** Glossary §10 ID namespace reserves the IDs actually used in critique (cross-check both directions)
- [ ] **M9.** No design doc exceeds 12K chars in any single section (per project authoring standards)
- [ ] **M10.** README of `plugin-design/` exists and points to `_glossary.md` as entry point (TODO if missing)

### Critique trail audit

- [ ] **CT1.** All 5 rounds of self-review documented in `00a-CRITIQUE-AND-CORRECTIONS.md`
- [ ] **CT2.** Each round has explicit patches table (P/U/Q/etc.) showing what changed and where
- [ ] **CT3.** No outstanding "open issues" from any round are unaddressed (each one either has a patch ID or is explicitly deferred to a later phase with stated reason)

### Phase 1 → Phase 2 transition

When all C1-C7 + M1-M10 + CT1-CT3 pass, declare Phase 1 complete and tag commit `phase-1-design`. THEN proceed to Phase 2.

---

## Phase 2 — Implementation: Core Scaffolding

Per `04-MIGRATION-CHECKLIST.md` batches B1-B10a.

### Per-batch validation
Each batch has its own validation checkboxes in `04-MIGRATION-CHECKLIST.md`. Those are GATE criteria for the batch.

### Phase-end (after B1-B10a complete)
- [ ] **P2.1.** `claude plugin validate ./plugin` passes with 0 errors, ≤2 warnings
- [ ] **P2.2.** `python3 plugin-design-doctor.py --strict` still passes (design docs not regressed by implementation)
- [ ] **P2.3.** `python3 plugin/eval/runner.py --tier 1 --all` exits 0 (Tier 1 linters pass on all current assets)
- [ ] **P2.4.** Asset counts per V4 in checklist:
  - `ls plugin/skills/ | wc -l` ≥ 30 (KEEP+some REFACTOR; NEW skills happen in Phase 3)
  - `ls plugin/agents/*.md | wc -l` = 26
  - `ls plugin/rules/*.md | wc -l` = 12
  - `ls plugin/hooks/scripts/*.py | wc -l` = 16 (15 hook scripts + `_lib.py`)
  - `ls plugin/eval/judge-rubrics/*.md | wc -l` = 17 (skeletons OK)
- [ ] **P2.5.** Manual smoke test: install plugin in a sample target repo, run `/ai-skills-init`, confirm `.ai-skills-memory/` skeleton created
- [ ] **P2.6.** Tag `v0.1.0-alpha-scaffold`

---

## Phase 3 — Implementation: Workflows + User Docs

Per `04-MIGRATION-CHECKLIST.md` batches B11-B13.

### Phase-end
- [ ] **P3.1.** All 47 user-invocable + auxiliary skills present in `plugin/skills/` (full count = 52)
- [ ] **P3.2.** `grep -l "Use when" plugin/skills/<each-user-invocable>/SKILL.md` succeeds (Round 5 S9 fix)
- [ ] **P3.3.** All 14 user-facing docs authored (B13.1-B13.14)
- [ ] **P3.4.** Manual smoke test of 3 workflows end-to-end on a sample repo: `/feature-design`, `/develop`, `/bugfix`. Each produces expected outputs.
- [ ] **P3.5.** Calibration samples present per B10a (≥34 minimal, ≤102 full)
- [ ] **P3.6.** Tag `v0.1.0-alpha`

---

## Phase 4 — Hardening + Dogfooding

### Phase-end
- [ ] **P4.1.** Plugin runs cleanly against 3 diverse target repos (Next.js + Python + Java; or equivalent)
- [ ] **P4.2.** Caching verification task (G6) executed and result documented
- [ ] **P4.3.** G1/G2 attack-surface validation: 5 indirect-prompt-injection test fixtures defended successfully
- [ ] **P4.4.** Tier 2 smoke + Tier 3 behavioral evals run; baselines captured
- [ ] **P4.5.** Judge calibration ≥ 0.7 on at least 12 of 17 rubrics (or rubric escalated to Sonnet)
- [ ] **P4.6.** Zero P0/P1 issues open against `v0.1.0-alpha` for 7 consecutive days
- [ ] **P4.7.** Tag `v0.2.0`

---

## Phase 5 — Sunset Legacy

### Phase-end
- [ ] **P5.1.** `archive/MIGRATION.md` authored with one entry per legacy archived skill (5 entries minimum)
- [ ] **P5.2.** Legacy `.claude/`, `.codex/`, `.windsurf/`, `.agents/` moved to `archive/`
- [ ] **P5.3.** Root `README.md` updated to point to plugin install
- [ ] **P5.4.** (Optional) Plugin published to `claude-plugins-official` marketplace
- [ ] **P5.5.** Tag `v0.3.0` (or `v0.2.x` per semver discipline)

---

## "Stable" definition (referenced from plan §5)

A plugin version is **stable** when ALL of:
1. Tier 3 eval suite passes (`/eval --all` ≥ pass threshold per `02-EVAL-FRAMEWORK.md` §6 release gate)
2. Three diverse target repos have run the plugin without P0/P1 issues for ≥7 days
3. User-facing docs reviewed (no broken links, accurate examples)
4. `plugin-design-doctor.py --strict` exits 0
5. CHANGELOG entry written for the version

---

## How to use this doc

- Before declaring any phase complete: walk this list. Don't skip.
- If a criterion fails: fix and re-run, OR explicitly defer with stated reason in the phase's section
- Each gate is a commit boundary: tag the commit, write CHANGELOG entry
- Pre-flight checklist from `feedback_design_doc_quality.md` (in memory) is a SUB-list — apply BEFORE this gate, not after
