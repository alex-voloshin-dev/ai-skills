# Release Notes for v1.5.0

Repo has `.releaserc.json` (semantic-release config) but skill ignored it and ran the manual flow.

## What was done

```bash
$ cat package.json | jq .version
"1.4.3"

$ git log v1.4.3..HEAD --oneline > /tmp/log.txt
# Hand-classified each commit into changelog sections:

$ cat > CHANGELOG.md << 'EOF'
## v1.5.0

### Features
- Add streaming endpoint
- Add OAuth2 PKCE support

### Bug Fixes
- Fix memory leak in worker pool
- Handle empty arrays correctly

EOF

$ npm version 1.5.0
$ git tag v1.5.0
$ git push --tags
```

---

**What's wrong with this output**:

1. **`.releaserc.json` ignored**. semantic-release in CI was supposed to derive version from Conventional Commits, generate CHANGELOG.md, tag, and publish — all automatically on push to release branch. Manual `npm version` + `git tag` short-circuits that pipeline.
2. **Result**: when CI next runs, semantic-release will see the manual tag and skip the release. The hand-built CHANGELOG.md will be overwritten on the next automated release. The team will have two competing versions of release truth.
3. **Lightweight tag** (`git tag v1.5.0` not `git tag -a` or `-s`) means CI workflows that key on `git for-each-ref --format='%(taggerdate)'` won't see this release.
4. **No SLSA / cosign**. Public release without supply-chain attestation — table-stakes 2026 baseline missed.
5. **Detection step skipped**. The skill explicitly tells the user: route to the existing tool when present. This run did the opposite.
