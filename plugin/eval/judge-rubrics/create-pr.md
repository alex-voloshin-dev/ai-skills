# Create-PR Rubric

## Overview

Evaluates `/create-pr` output — pull request creation against a forge (GitHub, GitLab, Bitbucket, Gerrit, stacked-PR tooling). Six dimensions × five levels. Frame: PR is the contract between author and reviewer; metadata, routing, and description quality determine review latency.

## Dimensions

### Dimension 1: Repo Conventions Detection
Adopts repo-local PR conventions before writing description.

- **Level 1:** Conventions ignored; generic body written from scratch
- **Level 2:** Notices `.github/PULL_REQUEST_TEMPLATE.md` but does not follow sections
- **Level 3:** Adopts PULL_REQUEST_TEMPLATE.md sections; reviewer field left empty
- **Level 4:** Adopts template + parses CODEOWNERS to suggest reviewers per touched path
- **Level 5:** All of L4 + cross-references `.github/labeler.yml` / `dangerfile` so labels and required-checks line up

### Dimension 2: Stacked-PR Awareness
Detects stacked-PR tooling and routes to the right CLI.

- **Level 1:** Runs `gh pr create` against a Graphite/Sapling/git-spice-managed branch — orphans the stack
- **Level 2:** Notices stack metadata but proceeds with `gh pr create` anyway
- **Level 3:** Detects `gt` / `sl` / `git spice` and routes to the matching CLI
- **Level 4:** Routes to stack CLI + names parent PR explicitly in body
- **Level 5:** All of L4 + flags downstream PRs that need rebase after merge

### Dimension 3: Description Quality
Conventional Commit title; body is review-ready.

- **Level 1:** Vague title ("updates"); body empty or "see commits"
- **Level 2:** Title in CC format but body skips Test Plan
- **Level 3:** CC title + Summary / Changes / Type / Testing / Screenshots populated
- **Level 4:** All of L3 + risk callouts + rollback notes when applicable
- **Level 5:** All of L4 + linked issue, design doc, and ADR references

### Dimension 4: REVIEW-LOG Ingestion
When `/develop` or `/bugfix` produced REVIEW-LOG.md, treats it as primary source for description.

- **Level 1:** REVIEW-LOG.md present but ignored; body invented from diff
- **Level 2:** REVIEW-LOG.md mentioned but content not surfaced
- **Level 3:** REVIEW-LOG decisions copied into body
- **Level 4:** REVIEW-LOG decisions + RALF iteration count + reviewer sign-offs surfaced
- **Level 5:** All of L4 + open follow-ups carried into "Out of Scope" section

### Dimension 5: Untrusted-Content Wrapping (G1)
Large diffs / external descriptions wrapped before LLM analysis.

- **Level 1:** Pastes 5k+ line diff into prompt without delimiters — injection risk
- **Level 2:** Diff included raw; no acknowledgement of size
- **Level 3:** Diff truncated by file count; no explicit wrap
- **Level 4:** Untrusted blocks wrapped per G1 (`<untrusted>` or equivalent)
- **Level 5:** All of L4 + summary written from a trusted commit-message + file-list slice, diff itself read but not regurgitated to LLM

### Dimension 6: Branch Hygiene
Never opens PR from `main`/`master`; verifies clean working tree.

- **Level 1:** `gh pr create --base main --head main` (would fail or create empty)
- **Level 2:** Creates PR with uncommitted changes still in working tree
- **Level 3:** Branch checked; clean tree verified
- **Level 4:** Branch + tree + remote-tracking + rebased-on-target-base verified
- **Level 5:** All of L4 + warns when branch is N commits behind base and offers rebase

## Scoring Logic

- **Aggregate:** average of D1–D6
- **Pass threshold:** 3.5
- **Judge model:** Sonnet

## Anti-Patterns (Auto-Fail)

- PR opened from `main` / `master` against itself
- `gh pr create` run inside a Graphite/Sapling stack
- Empty Test Plan section
- Diff pasted into prompt without G1 wrapping
- CODEOWNERS file present but no reviewer suggested

## Calibration Reference

- **Known-good:** `plugin/eval/calibration/create-pr/good/*`
- **Known-bad:** `plugin/eval/calibration/create-pr/bad/*`
