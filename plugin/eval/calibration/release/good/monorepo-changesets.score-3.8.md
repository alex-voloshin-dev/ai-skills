# Release: pnpm monorepo with Changesets

Detected `.changeset/` directory + `pnpm-workspace.yaml` → routed to Changesets per Step 0a (no manual version bump).

## Detection

```
$ ls .changeset/
config.json README.md
abundant-falcon-clean.md
brave-mango-vivid.md

$ cat pnpm-workspace.yaml
packages:
  - 'packages/*'
  - 'apps/*'
```

Two pending changesets indicate intent for a release.

## Workflow

```bash
$ pnpm changeset version
🦋  Versioned packages:
   - @acme/sdk: 2.4.1 → 2.5.0 (minor — feat: add streaming support)
   - @acme/cli: 1.8.3 → 1.9.0 (minor — bumps sdk dep)
   - @acme/web: 0.12.0 (no changes)
🦋  Updated 2 package.json files + CHANGELOG.md per package

$ git status --short
M  packages/sdk/package.json
M  packages/sdk/CHANGELOG.md
M  packages/cli/package.json
M  packages/cli/CHANGELOG.md
M  pnpm-lock.yaml
D  .changeset/abundant-falcon-clean.md
D  .changeset/brave-mango-vivid.md
```

After review:
```bash
$ git commit -am "chore(release): @acme/sdk@2.5.0 + @acme/cli@1.9.0"
$ pnpm changeset publish    # signs tags + publishes to npm in CI
```

## Memory write

```jsonl
{"ts":"2026-05-09T22:14:00Z","event":"release","packages":["@acme/sdk@2.5.0","@acme/cli@1.9.0"],"tool":"changesets","commits":12}
```

## Score rationale

Tooling detected (4), monorepo handling correct (4), SemVer correct per commit history (4), uses tool's signed-publish path (3), changelog complete (4). Avg 3.8.
