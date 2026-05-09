# Run Tests — `payments-service` integration suite (run #1882)

## Stack Detection
- Detected: Java 21 / Maven / Failsafe (integration tier)
- `pom.xml` confirms Spring Boot 3.3 + Testcontainers 1.20
- Workspace shape: single module

## Command Used
```
mvn -B verify -Pintegration -DforkCount=1C
```

## Suite Summary

| Tier | Tests | Pass | Fail | Skipped | Duration |
|---|---|---|---|---|---|
| Integration | 142 | 140 | 1 | 1 | 4m 38s |

Coverage gate (read from `jacoco-maven-plugin` config — line ≥ 85%, branch ≥ 80%): **PASS** (line 87.2%, branch 82.4%). Per-package compliance attached.

## Per-Failure Analysis

### `RefundIntegrationTest.refundPropagatesToWebhook` — class: **flaky** (timing)

Evidence:
- Failed at `assertEquals(2, webhookCalls.size())` — got 1 then later got 2 on a retry
- Stack frame points at line 87, an assertion 200ms after the action
- Run history (last 10 builds): pass, fail, pass, pass, fail, pass, pass, pass, fail, pass — 30% flake rate
- The webhook receiver is asynchronous; the test races the dispatch

Class confidence: HIGH — clear race, no behaviour change in this PR's diff.

### Suggested Next Action

Move to `Awaitility` polling (5s timeout, 50ms interval) instead of fixed sleep. Quarantine in the meantime: add `@Tag("flaky")` and exclude from PR runs; surface owner + 14-day fix SLA in the quarantine register.

Did NOT auto-fix because the change is non-trivial (touches assertion semantics) and exceeds the 3-attempt safe-fix bound. Escalating.

## Skipped

`RefundIntegrationTest.partialRefundOnSettledOrder` — `@Disabled("blocked on payments-gateway #2241")`. Carried forward.

## Class-Frequency Summary (this run)

| Class | Count |
|---|---|
| Flaky (timing race) | 1 |
| Code-bug | 0 |
| Test-bug | 0 |
| Contract-drift | 0 |
| Environment | 0 |

## Machine-Readable Tail

```json
{
  "summary": {"tests": 142, "pass": 140, "fail": 1, "skip": 1, "duration_s": 278},
  "coverage": {"line": 87.2, "branch": 82.4, "gate": "PASS"},
  "failures": [
    {
      "id": "RefundIntegrationTest.refundPropagatesToWebhook",
      "class": "flaky",
      "next_action": "quarantine + Awaitility migration",
      "auto_fixed": false
    }
  ]
}
```
