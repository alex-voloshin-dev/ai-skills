# Release Rubric

## Overview

Evaluates `/release` output — version bump, changelog, tag, and (where applicable) artefact publish. Six dimensions × five levels. Frame: route to existing release tooling first; SemVer correctness; signed and attested artefacts for public releases.

## Dimensions

### Dimension 1: Tooling Routing (Step 0a)
Detects existing release automation and uses it.

- **Level 1:** Hand-bumps version, hand-writes changelog, hand-tags despite `release-please-config.json` / `.releaserc` / `.changeset/` / `.goreleaser.yaml` / `release.toml` / `jreleaser.yml` present
- **Level 2:** Notices tooling but bypasses it ("just this once")
- **Level 3:** Detects and runs the right tool (release-please / semantic-release / Changesets / GoReleaser / cargo-release / JReleaser)
- **Level 4:** Tool routed + dry-run shown + user APPROVE before publish
- **Level 5:** All of L4 + verifies tool version against the lockfile / pinned manifest

### Dimension 2: Monorepo Handling
For monorepos, uses per-package versioning.

- **Level 1:** Bumps a single root version on a Changesets / Lerna / Nx repo
- **Level 2:** Touches multiple packages but to the same bump (e.g., all `patch`)
- **Level 3:** Per-package bump driven by changeset / nx affected
- **Level 4:** Per-package bump + dependency-graph cascade applied (downstream patches when upstream minor)
- **Level 5:** All of L4 + private packages skipped from publish; release notes per package

### Dimension 3: SemVer Correctness
Major/Minor/Patch decision matches commit history (BREAKING / feat / fix).

- **Level 1:** `patch` chosen for a `BREAKING CHANGE` footer (or vice versa)
- **Level 2:** Bump justified by "no breaking changes" without checking footers
- **Level 3:** Bump matches highest-severity commit in range
- **Level 4:** Bump justified per commit-by-commit scan; pre-release tags handled (rc/beta/alpha)
- **Level 5:** All of L4 + 0.x.y rules respected (breaking → minor pre-1.0)

### Dimension 4: Signed Tag
Public releases use signed annotated tags; provenance attestation when ecosystem supports it.

- **Level 1:** `git tag X` (lightweight) used for public release
- **Level 2:** Annotated `-a` but unsigned
- **Level 3:** `git tag -s -a` (signed annotated)
- **Level 4:** Signed tag + cosign sign-blob on artefacts when shipped
- **Level 5:** All of L4 + SLSA provenance attestation; `cosign verify-attestation` round-tripped

### Dimension 5: Changelog Completeness
Covers features / fixes / perf / breaking; sourced from git log not memory.

- **Level 1:** Single-line "various improvements"
- **Level 2:** Bullets present but cherry-picked from memory; commits missed
- **Level 3:** Generated from `git log <prev>..HEAD` with type buckets
- **Level 4:** Type buckets + commit links + author attribution + breaking-change call-out
- **Level 5:** All of L4 + upgrade notes / migration steps for breaking entries

### Dimension 6: Humanizer Compliance
Public-facing release notes pass humanizer (per CLAUDE.md rule).

- **Level 1:** Heavy AI-tone ("we're thrilled to introduce...", "leveraging cutting-edge")
- **Level 2:** Some inflated language; em-dash overuse; rule-of-three
- **Level 3:** Plain English; minor patterns remain
- **Level 4:** Clean per humanizer skill checks
- **Level 5:** All of L4 + voice matches prior release notes (consistent persona/tone)

## Scoring Logic

- **Aggregate:** average of D1–D6
- **Pass threshold:** 3.5
- **Judge model:** Sonnet

## Anti-Patterns (Auto-Fail)

- Hand-writes changelog when `.releaserc` / Changesets config present
- `patch` bump for a commit with `BREAKING CHANGE:` footer
- Lightweight tag (`git tag X`) used for public release
- Public release notes fail humanizer audit
- Single-package version bump on a Changesets monorepo

## Calibration Reference

- **Known-good:** `plugin/eval/calibration/release/good/*`
- **Known-bad:** `plugin/eval/calibration/release/bad/*`
