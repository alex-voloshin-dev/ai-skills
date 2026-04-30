# Codebase Summary — `OrderService`

## Overview

`OrderService` (`src/orders/service.py:14-218`) handles three operations: order creation (`createOrder`, lines 35-78), status updates (`updateStatus`, lines 80-120), and cancellation (`cancelOrder`, lines 122-160). It depends on `OrderRepository` (constructor injected, line 22) and emits domain events via `EventBus` (constructor injected, line 23).

## Order Lifecycle

Per the inline state machine (`src/orders/state.py:8-42`), order status transitions follow:

```
created → confirmed → shipped → delivered
        ↘ cancelled
```

Direct quote from `state.py:14`:
> "Cancellation is permitted only from `created` or `confirmed` states; `shipped` and `delivered` orders use the returns flow (not in this service)."

## Concurrency

The service uses optimistic locking via the `version` column on the orders table (verified in `migrations/004_add_version.sql:3-5`). On version mismatch, `updateStatus` raises `ConcurrentModificationError` (`service.py:108`) which the caller is expected to retry.

## Side Effects

`createOrder` emits `OrderCreated` event (`service.py:71`); `updateStatus` emits `OrderStatusChanged` (`service.py:115`); `cancelOrder` emits `OrderCancelled` (`service.py:155`). All events are JSON-serializable per `EventBus.publish` signature (`event_bus.py:18`).

## Inferred (not directly stated in source)

- The retry policy on `ConcurrentModificationError` is the caller's responsibility — INFERRED from absence of retry logic in `service.py`; the service raises and lets the caller decide.
- Event ordering is best-effort — INFERRED from `EventBus.publish` being non-blocking (`event_bus.py:21`); no explicit ordering guarantee in the code.

## Sources

- `src/orders/service.py` — lines 14-218 (read full file)
- `src/orders/state.py` — lines 8-42 (read state machine block)
- `migrations/004_add_version.sql` — lines 1-12 (read full migration)
- `src/events/event_bus.py` — lines 14-30 (read publish method)
