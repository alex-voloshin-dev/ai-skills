# Risk-Based QA Plan — `/payments` Service Pre-Release Verification

## Mode: verification (risk-based)

## Scope
Verify the `/payments` service before the v4.3 release. The service handles card-present checkout, refunds, and 3DS challenge flow. Money-handling — high stakes.

## Heuristics Applied
- **CIDTESTD** for product elements (Customers, Information, Dependencies, Tests, Equipment, Schedule, Deliverables) — applied to scope sizing
- **P × I matrix** (Probability × Impact) for risk-driven sequencing
- **SFDPOT** for coverage axes inside each risk band

## Risk Matrix (P × I)

| Area | Probability of regression | Impact if regressed | P × I | Risk band |
|---|---|---|---|---|
| 3DS challenge flow | M | H (lost auth → lost sales) | M-H | **HIGH** |
| Refund processing | L | H (double refund / no refund) | L-H | **HIGH** |
| Idempotency on retry | M | H (double charge) | M-H | **HIGH** |
| Currency conversion | L | H (wrong amount) | L-H | **HIGH** |
| Webhook receiver | M | M (delayed state) | M-M | **MEDIUM** |
| Card-form UI | L | M | L-M | **LOW** |
| Receipt email template | L | L | L-L | **LOW** |

> Probability based on diff scope: 3DS, idempotency, and webhook handlers all received changes; refund + currency unchanged but interact with changed code, hence still HIGH on impact.

## Test Sequencing (HIGH → MEDIUM → LOW)

### HIGH band (Day 1 — must-pass before release)
1. **3DS challenge** — happy path + 3 failure modes (timeout, declined, retried). SFDPOT axes: Function + Time + Platform (test on Chrome, Safari, iOS Safari).
2. **Refund** — full refund, partial refund, refund of refund (must reject), refund after settlement. Verify ledger entries match.
3. **Idempotency** — replay same `Idempotency-Key` 5× — must yield single charge. Verify under simulated retry storm (10 concurrent).
4. **Currency** — boundary amounts in JPY (no decimal), USD (2 decimals), KWD (3 decimals). Watch for rounding bugs.

### MEDIUM band (Day 2)
5. **Webhook receiver** — out-of-order delivery, duplicate delivery, signature-validation failure.

### LOW band (Day 3 — post-release smoke)
6. **Card-form UI** + **Receipt email template** — visual smoke + a11y baseline.

## Living Risk Model
After each band, re-evaluate. If HIGH band surfaces a real bug, MEDIUM/LOW bands may be paused while the fix lands and we re-baseline.

## Exit Criteria
- All HIGH-band tests pass with evidence captured
- No P0/P1 open
- Sign-off from QA + release manager

## Handoff
- Test execution → `/run-tests` and `/test-local` for the integration tier
- Threshold setting / pyramid review → already done in `/test-strategy v4.2` (no re-derivation here)
- Any bug → individual `/qa --mode bug-report` then `/bugfix`
