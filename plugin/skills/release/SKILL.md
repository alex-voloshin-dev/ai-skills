---
name: release
description: Release workflow — version bump, changelog generation, signed git tag, release notes. Detects existing release tooling (release-please, semantic-release, Changesets, GoReleaser, cargo-release, JReleaser) and routes to it; otherwise runs an inline stack-detected release. Use when cutting a release, tagging a version, preparing a changelog, or publishing release notes.
disable-model-invocation: true
argument-hint: "[version-number] [--prerelease alpha|beta|rc]"
---

# Release

Structured workflow for preparing a release. Bumps version, generates changelog, creates a signed git tag, and produces release notes.

## 0. Gather Context

### 0a. Detect existing release tooling — route first, build inline second

Before running the inline release flow, check whether the repo already has release tooling configured. If so, route to it; the team's choice supersedes anything inline below.

| Marker file present | Tool | Run command / path |
|---|---|---|
| `release-please-config.json` or `.release-please-manifest.json` | [release-please](https://github.com/googleapis/release-please) (Google) | Releases happen via the GitHub Action on PR merge. Check for an open release-please PR; review and merge it instead of cutting manually. |
| `.releaserc*` (`.json`/`.yml`/`.js`) or `release.config.js` | [semantic-release](https://semantic-release.gitbook.io) | Releases happen in CI on push to release branch. Verify the next release will fire; do not bump manually. |
| `.changeset/` directory + `.changeset/config.json` | [Changesets](https://github.com/changesets/changesets) (monorepo Node) | `npx changeset version` to bump per-package; `npx changeset publish` to release. |
| `.goreleaser.yaml` / `.goreleaser.yml` | [GoReleaser](https://goreleaser.com) | `goreleaser release --clean` (CI usually drives it on tag push). |
| `Cargo.toml` with `[workspace.metadata.release]` or local `release.toml` | [cargo-release](https://github.com/crate-ci/cargo-release) | `cargo release <level>` (e.g., `cargo release minor`). |
| `jreleaser.yml` | [JReleaser](https://jreleaser.org) (JVM polyglot) | `jreleaser release` (Maven/Gradle plugins also available). |

If a tool is detected:
1. Inspect its config for current state (next version, release branch, prerelease suffixes).
2. Run its release command (or open a PR / merge a release-please PR depending on tool).
3. Skip Steps 1–6 below; the tool handles version bump + changelog + tag.
4. Continue at Step 7 (Memory Write) so the release is recorded in `runs.jsonl`.

If no tool is detected, continue to Step 0b.

### 0b. Read project context

Read `CLAUDE.md` (or `AGENTS.md`) at the project root to identify:
- Tech stack (determines where version files live: package.json, pom.xml, pyproject.toml, build.gradle)
- Release conventions (semantic versioning, calver, custom)
- CI/CD pipeline (what triggers on tag push)
- Changelog format (CHANGELOG.md, GitHub Releases, both)

## 1. Determine Release Type

Ask the user (or infer from commits since last release):

- **Major** (X.0.0): Breaking changes, removed APIs, major architecture shifts
- **Minor** (x.Y.0): New features, non-breaking API additions
- **Patch** (x.y.Z): Bug fixes, security patches, dependency updates

```
// turbo
git describe --tags --abbrev=0 2>/dev/null || echo "No tags found"
```

```
// turbo
git log $(git describe --tags --abbrev=0 2>/dev/null || echo "HEAD~20")..HEAD --oneline
```

## 2. Analyze Changes

Classify commits since last release:

| Type | Changelog Section |
|---|---|
| `feat` | Features |
| `fix` | Bug Fixes |
| `perf` | Performance |
| `refactor` | Refactoring |
| `docs` | Documentation |
| `chore`/`ci` | Maintenance |
| `BREAKING CHANGE` | Breaking Changes |

## 3. Bump Version

Update version in project files:

| Stack | Files to Update |
|---|---|
| Node.js | `package.json` (`version` field) |
| Java/Maven | `pom.xml` (`<version>`) |
| Java/Gradle | `build.gradle` (`version`) |
| Python | `pyproject.toml` (`version`) |
| .NET | `*.csproj` (`<Version>`) |
| Go | Git tag only (no version file) |

## 4. Generate Changelog

Add entry to `CHANGELOG.md` (create if not exists):

```markdown
## [X.Y.Z] - YYYY-MM-DD

### Breaking Changes
- Description (commit ref)

### ✨ Features
- Description (commit ref)

### 🐛 Bug Fixes
- Description (commit ref)

### ⚡ Performance
- Description (commit ref)

### 🔧 Maintenance
- Description (commit ref)
```

## 5. Create Release Commit

Present the changes for user review.

After approval, suggest:

```
git add -A
git commit -m "chore(release): vX.Y.Z"
git tag -s vX.Y.Z -m "Release vX.Y.Z"   # -s for GPG-signed tag (recommended)
```

If the project ships signed artefacts (supply-chain integrity), also generate a [SLSA provenance](https://slsa.dev) attestation and / or a [cosign sign-blob](https://docs.sigstore.dev/cosign/) signature for the release artefact in CI.

**⚠️ Do NOT run git commands without user confirmation.** This workflow explicitly overrides the "no git write ops" Hard Rule — git ops are permitted here only after user APPROVE.

## 6. Release Notes

Generate release notes for GitHub/GitLab:

```markdown
# Release vX.Y.Z

## Highlights
[1-3 sentence summary of the most important changes]

## What's Changed
[Changelog content from Step 4]

## Upgrade Guide
[If breaking changes — step-by-step migration instructions]

## Contributors
[List contributors from git log]
```

## 7. Memory Write (L4)

Append a release event to `.ai-assets-memory/runs.jsonl` for cross-session aggregation per `memory-discipline.md`:

```json
{"ts": "<ISO8601>", "event": "release", "version": "vX.Y.Z", "type": "major|minor|patch", "commit_count": N, "breaking_changes": <bool>}
```

This enables the memory-curator to surface release cadence patterns and the eval framework to gate behavioral suites against release tags.

## 8. Next Steps

Suggest post-release actions:
- Push tag: `git push origin vX.Y.Z`
- Push branch: `git push`
- Create GitHub Release with release notes
- Deploy to staging: `/deploy-staging`
- Deploy to production: `/deploy-production`
- Announce release to team

## Integration

- **Preceded by**: `/code-review` (all PRs merged)
- **Followed by**: `/deploy-staging`, `/deploy-production`
- **Skills**: `@humanizer` MUST be applied to public-facing release notes per CLAUDE.md humanizer rule
- **Rules**: `git-conventions` (Conventional Commits required for changelog classification)
- **Memory writes**: L4 `runs.jsonl` (release event per Step 7)
