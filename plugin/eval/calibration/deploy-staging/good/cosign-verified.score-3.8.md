# Staging deploy: orders-api v2.6.0 — supply-chain validation gate

Project's CI ships images signed via Sigstore Cosign + SLSA L2 attestation. Staging is the natural validation gate (per Step 0).

## Verify signature before deploy

```bash
$ cosign verify \
    --certificate-identity-regexp '^https://github.com/acme/orders-api' \
    --certificate-oidc-issuer https://token.actions.githubusercontent.com \
    ghcr.io/acme/orders-api:v2.6.0
Verification for ghcr.io/acme/orders-api:v2.6.0 --
The following checks were performed:
  - The cosign claims were validated
  - Existence of the claims in the transparency log was verified offline
  - The certificate was verified against the OIDC issuer
✓ verified
```

## Verify SLSA L2 attestation

```bash
$ gh attestation verify --owner acme \
    oci://ghcr.io/acme/orders-api:v2.6.0
✓ Verification succeeded! 1 attestation(s) verified
  - SLSA L2 provenance from acme/orders-api @ refs/tags/v2.6.0
```

Build provenance confirms image came from the expected source repo + tag.

## Deploy

```bash
$ helm upgrade orders-api ./charts/orders-api -n staging \
    --set image.tag=v2.6.0 --atomic --timeout 5m --wait
deployed
```

Smoke (Playwright @smoke): 18 passed.

## Score rationale

Cosign verify before deploy (4), SLSA attestation verified (4), helm `--atomic` (4), discoverable smoke (3.5). Avg 3.8.
