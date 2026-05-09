# Release v0.9.0 — public OSS package

Public-facing release of a Python package (PyPI distribution). Skill ran inline Steps 1–8 but skipped supply-chain hardening.

## What was done

```bash
$ python -m build
$ git tag v0.9.0    # lightweight tag, no -s, no -a
$ git push --tags
$ twine upload dist/*
```

CHANGELOG and release notes prepared (humanized). Notes pushed to GitHub Releases via `gh release create v0.9.0`.

---

**What's wrong with this output**:

1. **Lightweight tag, not signed.** `git tag v0.9.0` creates a lightweight tag — no annotation, no GPG signature. The release skill explicitly says `git tag -s` for signed tags (recommended) and `-a` for annotated. Lightweight tags will silently break CI workflows that filter `git for-each-ref --merged --format='%(taggerdate:iso)'` and produce empty results.
2. **No SLSA provenance**. PyPI publishing without attestations leaves users unable to verify the artefact came from this source. PyPI now supports attestations (PEP 740 + Trusted Publishing); the skill should enable `attestations: true` in the GitHub Action and let the OIDC flow generate signed provenance.
3. **No cosign sign-blob**. Signing the wheel/tarball is the supply-chain table-stakes 2026 baseline. Skill says so explicitly.
4. **`twine upload` with stored API token** (implied by direct upload). Should use Trusted Publishing (OIDC) to eliminate long-lived PyPI tokens.

Result: users cannot detect whether a malicious actor pushed a fake `v0.9.0` to PyPI from a different repo. SLSA L2 + signed tags would prevent that.
