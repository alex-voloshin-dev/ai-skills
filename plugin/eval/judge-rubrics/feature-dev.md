# Feature Dev Rubric

## Overview

Evaluates `/feature-dev` output — the **single-agent inline fallback** for feature implementation. The default for feature work is `/develop` (multi-agent). `/feature-dev` is reserved for situations where multi-agent spawning is impractical or explicitly opted out. Six dimensions × five levels.

## Dimensions

### Dimension 1: Plan-First Discipline
A plan was presented and the user gave explicit approval before any production code was edited.

- **Level 1:** No plan; jumped straight into edits
- **Level 2:** Brief outline written, but edits started before user response
- **Level 3:** Plan presented; implementation began on implicit assent
- **Level 4:** Plan presented + explicit user approval recorded before edits
- **Level 5:** Plan + approval + checkpoint after each major step (re-confirm if scope shifted)

### Dimension 2: Stack Detection
Read `CLAUDE.md`, `package.json`, `pom.xml`, `pyproject.toml`, or equivalent and selected the correct engineering role (python-engineer, ts-engineer, java-engineer, etc.).

- **Level 1:** No stack detection; generic code emitted
- **Level 2:** Stack guessed from file extensions only
- **Level 3:** Read manifest file; role choice partially correct
- **Level 4:** Read CLAUDE.md + manifest; correct role applied; conventions observed
- **Level 5:** All of L4 + cross-checked against project lint config / framework version

### Dimension 3: Single-Agent Inline Correctness
Implemented inline. No `Agent(...)` calls. Respects the `context: fork` constraint that subagent fan-out is forbidden inside this skill.

- **Level 1:** Spawned subagents via `Agent(...)` (violates fork-context rule)
- **Level 2:** Hinted at delegation ("a developer agent could…") without spawning
- **Level 3:** Inline implementation; some role bleed (mixing reviewer chatter)
- **Level 4:** Strict single-agent inline; one role applied throughout
- **Level 5:** All of L4 + role transition documented if multiple roles needed sequentially

### Dimension 4: Verification Complete
Tests + lint + type-check + build (where applicable) ran clean before declaring done.

- **Level 1:** No verification at all
- **Level 2:** One gate run (e.g., tests only); others skipped silently
- **Level 3:** Most gates run; one failure ignored or hand-waved
- **Level 4:** All applicable gates green; output captured
- **Level 5:** All of L4 + new tests added for the feature; coverage delta reported

### Dimension 5: Acceptance-Criteria Gate
Every acceptance criterion from the request was verified explicitly with a test, command, or evidence trail.

- **Level 1:** ACs ignored or restated without verification
- **Level 2:** Some ACs verified; others marked "should work"
- **Level 3:** All ACs verified; evidence is informal
- **Level 4:** Every AC mapped to a concrete check (test name / curl / screenshot)
- **Level 5:** All of L4 + traceability table (AC → check → result)

### Dimension 6: Boundary Discipline
Refused or escalated when `/develop` is the appropriate path. The skill description states `/develop` is the default; `/feature-dev` runs only when multi-agent is impractical or explicitly requested.

- **Level 1:** Used `/feature-dev` for a clearly multi-agent-suitable task without comment
- **Level 2:** Noted `/develop` exists but proceeded without justification
- **Level 3:** Justified single-agent choice on weak grounds
- **Level 4:** Justified the inline path with concrete reasons (env constraint, single-file change, explicit user request)
- **Level 5:** All of L4 + offered to switch to `/develop` if conditions changed mid-task

## Scoring Logic

- **Aggregate:** average of D1–D6
- **Pass threshold:** 4.0
- **Judge model:** Sonnet (verification + boundary judgment)

## Anti-Patterns (Auto-Fail)

- Wrote code before producing or getting approval on a plan
- Called `Agent(...)` inside the skill body (violates `context: fork`)
- Declared work done without running tests
- Ignored explicit acceptance criteria from the request
- Used `/feature-dev` despite user asking for the multi-agent flow

## Calibration Reference

- **Known-good:** `plugin/eval/calibration/feature-dev/good/*`
- **Known-bad:** `plugin/eval/calibration/feature-dev/bad/*`
