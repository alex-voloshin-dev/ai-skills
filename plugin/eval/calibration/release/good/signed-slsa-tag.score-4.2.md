# Release v2.4.0 — signed tag + SLSA L2 attestation

Single-package Go project. No release-please / GoReleaser config detected → followed inline Step 0b–8 with supply-chain hardening.

## Steps

```bash
$ git describe --tags --abbrev=0
v2.3.5

$ git log v2.3.5..HEAD --oneline | wc -l
24

# Classification: 18 fix, 5 feat, 1 BREAKING CHANGE → minor bump (with breaking-change note)
```

Updated `internal/version/version.go` to `2.4.0`. Generated `CHANGELOG.md` entry.

```bash
$ git tag -s v2.4.0 -m "Release v2.4.0"
$ git push origin v2.4.0
```

CI (GitHub Actions + slsa-framework/slsa-github-generator) emitted the SLSA L2 provenance:

```bash
$ gh attestation verify --owner acme acme-cli-v2.4.0-linux-amd64.tar.gz
✓ Verification succeeded! 1 attestation(s) verified
  - SLSA L2 provenance from acme/acme-cli @ refs/tags/v2.4.0

$ cosign verify-blob \
    --certificate acme-cli-v2.4.0.cert \
    --signature acme-cli-v2.4.0.sig \
    --certificate-identity-regexp '^https://github.com/acme/acme-cli' \
    --certificate-oidc-issuer https://token.actions.githubusercontent.com \
    acme-cli-v2.4.0-linux-amd64.tar.gz
Verified OK
```

## Public-facing release notes

Drafted with `gh release create --generate-notes` then humanized — short hook, two specific behaviour changes, one breaking change called out with migration path. Em-dashes constrained to 2 per paragraph.

## Score rationale

Signed tag (5), SLSA + cosign attestations (5), SemVer correct (4), classification accurate (4), humanized notes (4), changelog complete (4). Avg 4.2.
