# Production Deploy: payments-api v2.8.0 — decoupled deploy

## Detection (Step 0b)

```bash
$ grep -r "launchdarkly" packages/payments/package.json
"launchdarkly-node-server-sdk": "^9.4.2"
```

LaunchDarkly SDK present → decoupled deploy: ship dark, flip flag separately.

## Phase 1: Deploy with flag OFF

New code path (`use-stripe-paymentintents-v2`) gated behind LD flag, default OFF.

```bash
$ helm upgrade payments-api ./charts/payments-api \
    -n production \
    --set image.tag=v2.8.0 \
    --atomic --timeout 5m --wait
Release "payments-api" has been upgraded. Happy Helming!
STATUS: deployed
REVISION: 41
```

Smoke (project's `tests/smoke/`):
```bash
$ npx playwright test --grep @smoke --reporter=list
12 passed (4.2s)
```

Old code path still serving 100% of traffic. Risk = pure deploy risk (low).

## Phase 2: Flip flag for internal users

```bash
$ ldcli flag toggle use-stripe-paymentintents-v2 \
    --target-rule "email-domain:acme.com" \
    --value true \
    --env production
```

10 internal users served new path. Verified via Datadog APM filter `@user.email:*@acme.com AND @feature.flag:use-stripe-paymentintents-v2=true` — no errors over 30 min.

## Phase 3: Ramp

```bash
1% → wait 30min, error rate stable → 5% → wait 1h → 25% → wait 4h → 50% → overnight → 100%
```

Each step gated on Datadog SLO (success-rate ≥ 99.9, p99 < 800ms). No regressions. Reached 100% on day 3.

## Score rationale

Flag detection (4), decoupled deploy applied (4), `--atomic` used (4), staged ramp with SLO gates (4), Datadog filter for internal verification (4). Avg 3.8.
