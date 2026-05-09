# Risk Register — Two-Factor Authentication

> Template owned by `feature-design` skill. Co-producers: `security-engineer` (Wave 2) + `qa-engineer` (Wave 2). Lead consolidates. Replace example rows; keep the heatmap legend.

## Probability × Impact heatmap

A risk's cell is `Probability × Impact`. **Red = act now / block release**, **Amber = mitigate before GA**, **Green = monitor**.

```
                    Impact →
                  Low      Medium   High
Probability ↓   ┌────────┬────────┬────────┐
   High         │  Amber │  Red   │  Red   │
                ├────────┼────────┼────────┤
   Medium       │  Green │  Amber │  Red   │
                ├────────┼────────┼────────┤
   Low          │  Green │  Green │  Amber │
                └────────┴────────┴────────┘
```

Severity ranking for triage order: **Red > Amber > Green**. All Red items must have a named owner and a mitigation landed before the GA gate. Green items go to the backlog with a review-by date.

## Register

| ID | Description | Category | P (L/M/H) | I (L/M/H) | Severity | Mitigation | Owner | Status |
|---|---|---|---|---|---|---|---|---|
| R-1 | TOTP shared-secret leak via misconfigured DB backup | Technical | L | H | Amber | Encrypt secret column with per-tenant KMS key; exclude from logical backups; quarterly key rotation runbook | security-engineer | Mitigation in design |
| R-2 | Clock-skew on user device causes legitimate codes to fail | Technical | M | M | Amber | Accept ±1 step (30s) on TOTP window; surface "wrong code? check phone clock" hint after 2 failures | backend-engineer | Open |
| R-3 | User lockout cascade — both device + recovery codes lost | Operational | M | H | Red | Admin override flow with identity-verification email + 24h cooldown; documented runbook in support wiki | qa-engineer | Open — blocks GA |
| R-4 | Free-tier users complain about forced 2FA changing UX they did not ask for | Product | M | M | Amber | Default OFF for free tier; only Enterprise tenants get the admin enforcement toggle in v1 | product-manager | Resolved by scope decision |
| R-5 | SMS-flood bill spike — abuser triggers repeated SMS challenges | Compliance | M | H | Red | Per-account SMS rate limit (5/hour) + per-tenant daily cap + alert at 80% of cap; SMS opt-in only | security-engineer | Mitigation in design |
| R-6 | Adoption stalls because enrollment UX is too friction-heavy on mobile | Market | M | M | Amber | Usability test with 5 mobile users pre-GA; track time-to-enroll metric, gate GA on p50 < 90s | ui-ux-designer | Open |
| R-7 | Tenants relying on IP allowlist disable it after 2FA ships, weakening posture | Product | L | M | Green | Migration doc + admin-console nudge: "2FA complements, does not replace, IP allowlist" | product-manager | Doc planned |
| R-8 | Auditor rejects implementation because TOTP allows shared secrets across users | Compliance | L | H | Amber | Cryptographic uniqueness check at enrollment; SOC 2 evidence package includes test artefact | security-engineer | Validation pending |

## Mitigation review cadence

- Red: re-checked at every wave-3 review and at each pre-GA gate
- Amber: re-checked at GA gate
- Green: review every quarter or on related incident

## Out-of-scope risks (deferred, recorded for awareness)

- WebAuthn UX inconsistency across browsers — deferred to v2 with WebAuthn rollout
- Recovery-code phishing pattern — monitor, no current mitigation beyond user education
