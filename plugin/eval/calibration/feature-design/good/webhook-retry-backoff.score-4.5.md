# Webhook Retry with Exponential Backoff — Feature Design

> Feature: webhook-retry-2026q2
> Date: 2026-04-19
> Author: events-team
> Status: approved

## Goal & Success Metrics

Reduce webhook delivery failures from 15% (current, due to no retry logic) to < 2% by implementing exponential backoff. Target: 99.5% delivery success rate for webhooks within 1 hour of event emission.

## Acceptance Criteria

1. Failed webhooks retried with exponential backoff: 1s, 2s, 4s, 8s, 16s (max 5 attempts)
2. Webhook delivery status queryable via API; customers see delivery attempt count + last error
3. Dead-letter queue captures permanently failed webhooks (after 5 attempts); retention 30d for diagnostics
4. Retry logic does not block event processing (async queue only)

## Architecture

| Component | Responsibility | Owner |
|---|---|---|
| Event emitter | Publishes events to webhook queue | events |
| Retry queue worker | Processes queue; schedules retries on failure | events |
| Status tracker | Stores delivery attempts + last error per webhook | webhooks-db |
| Dead-letter sink | Captures failures after max retries; logs + alerts | observability |

Sequence: event → queue → deliver → timeout/error → backoff schedule → retry or DLQ.

## Trade-offs Considered

- **Exponential vs fixed-interval backoff:** exponential — reduces thundering herd during outages; adds ~5ms scheduling overhead per retry.
- **Max 5 retries vs 10:** 5 retries — 31s total window sufficient for most transient issues; 10 retries extends to 17 minutes (too long).
- **Retry state in-process vs DB:** DB — survives worker restarts; enables customer API query; small overhead acceptable.

## Rollout

1. Wave 1: enable for test webhook only; verify backoff timing 2d
2. Wave 2: enable for customers with < 1000 webhooks/day; monitor error rates 5d
3. Wave 3: full rollout; legacy immediate-fail mode deprecated

Gating: delivery success rate > 98%, DLQ error rate < 0.5%, no blocked event processing.

## Risks

| Risk | P × I | Mitigation | Owner |
|---|---|---|---|
| Retry queue buildup | M × H | Disk quota alerting; auto-scale queue workers | events-sre |
| Customer sees stale status | L × M | Status updated within 10s of each attempt; cache TTL 5s | webhooks-api |
| Webhook processing lag | L × M | Retry queue separate from event queue; independent scaling | events-sre |
| Duplicate delivery on retry | M × M | Idempotency key in webhook payload; customer implements dedup | webhooks-eng |

## Rollback

Disable retry queue; webhooks delivered once, failures recorded in DLQ only. Recovery < 1 min. Tested 2026-04-18 (measured: 45s).

## Open Questions

- Should customers be able to configure max retries per webhook? (assigned: webhooks-pm)
- What error types warrant immediate DLQ (e.g., 401 auth failure) vs retry? (assigned: events-team)

