# Exploratory Session — New Search Filter UI

## Mode: exploratory (SBTM — session-based test management)

## Charter
Explore the new `/search` filter chip UI to discover usability and correctness issues with combined filters (date + category + price + tag). Focus on filter interaction edge cases. Time-box: 90 minutes.

## Session Setup
- **Session start:** 2026-05-09 10:00
- **Tester:** qa
- **Build:** `web@3.22.0-rc.4` (staging)
- **Areas covered:** filter chip add/remove, URL persistence, multi-filter combinations, mobile width, keyboard nav
- **Areas explicitly skipped:** screen-reader (charter scope; will charter a separate a11y session)

## Heuristics Applied
- SFDPOT — covered Function (filter combinations), Data (boundary values: 0, 1, 25, 100 results), Platform (desktop Chrome + iOS Safari mobile), Time (rapid filter toggling)
- Goldilocks (too many / too few / just right filter combinations)

## Session Log

| Time | Activity | Note |
|---|---|---|
| 10:00 | Charter review + setup | OK |
| 10:08 | Add 1 chip at a time, observe URL | URL updates as expected |
| 10:18 | Add 5 chips rapidly | Bug-1 found |
| 10:32 | Remove chip via X click | OK |
| 10:38 | Remove chip via keyboard (Backspace in chip) | Bug-2 found |
| 10:55 | Mobile (responsive 390px) | Bug-3 found |
| 11:10 | URL share/load with 4 chips | OK |
| 11:18 | Empty result state (filter combo with 0 results) | Bug-4 found |
| 11:30 | Debrief | done |

## TBS Time Split
- **Test (T):** 62 min — direct exploration
- **Bug investigation (B):** 18 min — reproducing + capturing the four findings
- **Setup (S):** 10 min — switching builds, viewport tools

## Findings

- **Bug-1 (S3, P2):** Adding 5 filters in <500ms causes the 5th chip to render but not register in the URL state. Race in the debounced URL writer. Repro 4/5.
- **Bug-2 (S2, P2):** Backspace inside a chip removes the chip AND the previous chip (double-remove). Repro 10/10.
- **Bug-3 (S3, P3):** At 390px width, the "Clear all" button overlaps the last chip. Cosmetic.
- **Bug-4 (S2, P2):** Zero-result state shows the loader spinner indefinitely when applied filters return 0. Should show empty state. Repro 10/10.

## Open Questions (chartered for follow-up)
- Charter-2: a11y screen-reader session on the same UI
- Charter-3: filter performance under 50+ chips (does anything break at high cardinality?)

## Handoff
- Each bug → standard `/bugfix` or full report via this skill in bug-report mode (Bug-2 most urgent)
- a11y → new `/qa --mode exploratory --charter a11y-search`
