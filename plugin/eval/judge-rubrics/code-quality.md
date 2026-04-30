# Code Quality Rubric

## Overview

Cross-cutting rubric: code-facing output (PRs, scripts, configs) meets baseline quality standards. Applied to develop, bugfix, refactor, migrate.

## Dimensions

### Dimension 1: Naming Convention
Variables, functions, classes use stack-idiomatic names; no abbreviations that obscure meaning.

- **Level 1:** Single-letter vars in non-trivial code; cryptic abbreviations
- **Level 2:** Inconsistent style; some unclear names
- **Level 3:** Adheres to project conventions
- **Level 4:** Idiomatic names; intent visible from signature
- **Level 5:** Names read as documentation; no in-code clarification needed

### Dimension 2: Comment Clarity
Comments explain WHY (not WHAT); docstrings document contracts.

- **Level 1:** Comments restate what the code says; or no comments where needed
- **Level 2:** Mix of helpful and noise comments
- **Level 3:** Comments help; docstrings present for public API
- **Level 4:** Comments explain WHY; docstrings document inputs/outputs/exceptions
- **Level 5:** All of L4 + edge-case comments at non-obvious decisions

### Dimension 3: Testability
Functions are pure or have explicit dependencies; mocks possible without major rewrites.

- **Level 1:** Hidden dependencies; tightly coupled to globals
- **Level 2:** Dependencies implicit; testing requires shimming
- **Level 3:** Dependencies explicit; testable with effort
- **Level 4:** Dependencies injected; pure where possible
- **Level 5:** All of L4 + side effects isolated at the boundary

### Dimension 4: DRY Principle
No duplicated logic without justification.

- **Level 1:** Significant duplication; clear copy-paste
- **Level 2:** Some duplication; rationale missing
- **Level 3:** Minor duplication acknowledged
- **Level 4:** No duplication beyond intentional (like fixture data)
- **Level 5:** All of L4 + extracted helpers are well-named and tested

### Dimension 5: Error Handling
Errors handled at the right level; no silent swallows; exceptions are typed.

- **Level 1:** Bare `except:` or `try { } catch (Exception e) { }`
- **Level 2:** Errors caught but not logged or re-raised
- **Level 3:** Errors logged; types specific
- **Level 4:** Errors typed + logged + handled at the right level
- **Level 5:** All of L4 + recovery strategy documented per error class

## Scoring Logic

- **Aggregate:** average of D1–D5
- **Pass threshold:** 4.0
- **Judge model:** Sonnet (code judgment benefits from richer context understanding)

## Anti-Patterns (Auto-Fail)

- Bare `except:` / catch-all exception handlers
- Hardcoded credentials or secrets in code
- TODO / FIXME / XXX comments left in production code path
- Commented-out code blocks (use git history instead)
- Function > 80 lines without justification

## Calibration Reference

- **Known-good:** `plugin/eval/calibration/code-quality/good/*`
- **Known-bad:** `plugin/eval/calibration/code-quality/bad/*`
