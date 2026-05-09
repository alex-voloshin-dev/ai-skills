# Release v3.2.4 (patch bump)

Single-package Python project. Hand-classified commits, then bumped patch.

## Commit history (v3.2.3..HEAD)

```
$ git log v3.2.3..HEAD --oneline
fix: handle 503 from upstream
feat: add /v2/widgets API endpoint with new schema
BREAKING CHANGE: /v1/widgets removes the deprecated `legacy_id` field
fix: race in worker shutdown
chore: bump deps
docs: update README
```

## What was done

```bash
$ sed -i 's/version = "3.2.3"/version = "3.2.4"/' pyproject.toml
$ git tag v3.2.4
```

CHANGELOG.md updated:

```
## v3.2.4
- fix: handle 503 from upstream
- feat: add /v2/widgets endpoint
- fix: race in worker shutdown
- BREAKING CHANGE: legacy_id field removed
```

---

**What's wrong with this output**:

1. **SemVer violation**. The history contains a `BREAKING CHANGE:` footer. SemVer 2.0 requires a MAJOR bump on any breaking change — `3.2.3 → 4.0.0`. The skill bumped patch (`3.2.4`), which silently breaks downstream consumers who pinned `^3.0.0`.
2. **Also a feat:** present, which on its own would have required a MINOR bump (`3.3.0`), even without the breaking change.
3. **Breaking change buried in CHANGELOG**. Should be a top-line `### Breaking Changes` section with migration instructions, not a bullet at the bottom.
4. **No upgrade guide**. The release notes template requires an Upgrade Guide section when breaking changes are present. Missing.

The classification table in the release skill explicitly maps `BREAKING CHANGE` → "Breaking Changes" section + MAJOR bump. Skill ignored both rules.
