# Release — release-please flow

## Step 0a: tooling detection

`release-please-config.json` and `.release-please-manifest.json` present in repo root.

```json
{
  "release-type": "node",
  "include-v-in-tag": true,
  "packages": {
    ".": { "package-name": "@acme/web" }
  }
}
```

Routed to release-please. No hand changelog, no hand version bump, no hand tag.

## Dry-run review

```
$ npx release-please release-pr --dry-run \
    --repo-url acme/web --target-branch main
[release-please] Would create release PR:
  title: chore(release): @acme/web 2.4.0
  body:
    ## Features
    - billing: prorate charges on mid-cycle plan upgrade (#4318)
    - search: rank typeahead by recency x match-quality (#4310)
    ## Bug Fixes
    - auth: rotate session on role change (#4322)
    - api: validate cursor format on /v2/orders (#4321)
  bump: minor (2.3.4 -> 2.4.0)  -- driven by feat: commits since v2.3.4
```

Bump is `minor` because the range contains `feat:` commits but no `feat!:` or `BREAKING CHANGE:` footers — verified by scanning `git log v2.3.4..HEAD --grep=BREAKING`.

## User APPROVE

> Review the dry-run output. Proceed with release-please release-pr? **APPROVE / REJECT**

User: APPROVE.

## Apply

```
$ npx release-please release-pr --repo-url acme/web --target-branch main
[release-please] Created PR #4330: chore(release): @acme/web 2.4.0
```

PR #4330 was reviewed and merged. On merge, release-please's GitHub Action ran:

```
[release-please] Tag created: v2.4.0 (annotated, signed via GitHub signing identity)
[release-please] GitHub Release created: https://github.com/acme/web/releases/tag/v2.4.0
[release-please] Manifest updated: .release-please-manifest.json -> "2.4.0"
```

## Verification

```
$ git tag -v v2.4.0
object 4f8a2c1...
type commit
tag v2.4.0
gpg: Good signature from "github-actions[bot]"
```

## Release notes (humanizer-checked)

The body release-please generated was reviewed via the humanizer skill:
- No "thrilled to introduce" / "leveraging" patterns
- No em-dash overuse, no rule-of-three
- Plain bullets sourced directly from PR titles

Public-facing release notes published as written.

## Verdict

Released v2.4.0. Tag signed; changelog generated from commit history; humanizer-clean.
