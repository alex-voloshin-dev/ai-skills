# ADR-NNN: [Short Decision Title]

<!--
  Format: Michael Nygard original (2011) + MADR (https://adr.github.io/madr/).
  Filename convention: ADR-NNN-kebab-case-title.md
  Store under: docs/adr/ or docs/architecture/decisions/
-->

## Y-Statement

> In the context of **[use case / capability]**, facing **[concern / quality attribute / problem]**, we decided for **[option / pattern / technology]** and against **[alternatives]**, to achieve **[desired qualities, e.g., availability, latency, cost]**, accepting **[downside / drawback]**.

<!--
  Concrete example:
  In the context of order-service write throughput at 5k req/s peak,
  facing tail latency spikes under DB contention, we decided for an
  outbox pattern with Postgres LISTEN/NOTIFY and against synchronous
  Kafka publish, to achieve atomic writes and 99th-percentile latency
  under 200ms, accepting a 1–3s end-to-end publish delay.
-->

## Status

`Proposed` | `Accepted` | `Deprecated` | `Superseded by ADR-MMM`

- **Date:** YYYY-MM-DD
- **Decision-makers:** [names / roles]
- **Consulted:** [stakeholders reviewed]
- **Informed:** [downstream teams notified]

## Context

State the problem, the forces in play, and the constraints. Include relevant numbers (load, latency targets, team size, deadline). Avoid jumping to a solution.

<!--
  Example:
  Order-service currently publishes order-events synchronously to Kafka
  inside the same DB transaction. p99 latency spiked from 180ms to
  1100ms during a Kafka broker rolling restart on 2026-04-12. Compliance
  requires 99.9% availability for the checkout flow. Team has 2
  backend engineers and 1 SRE; 6-week deadline before Black Friday.
-->

## Decision

State the chosen option in one sentence, then expand with rationale (1–3 paragraphs). Reference the Y-statement above.

<!--
  Example:
  Adopt the transactional outbox pattern. Order-service writes the
  order row and an outbox row in a single Postgres transaction. A
  separate dispatcher process tails the outbox via LISTEN/NOTIFY and
  publishes to Kafka with at-least-once semantics. Consumers
  deduplicate via order-id idempotency keys.
-->

## Consequences

### Positive

- [Benefit 1: e.g., decouples API latency from Kafka availability]
- [Benefit 2: e.g., atomic write guarantees — no lost events]
- [Benefit 3: e.g., simpler retry semantics in dispatcher]

### Negative

- [Cost 1: e.g., 1–3 second end-to-end publish delay]
- [Cost 2: e.g., new dispatcher service to operate and monitor]
- [Cost 3: e.g., outbox table growth requires retention policy]

### Neutral

- [Trade-off: e.g., consumers must already be idempotent — they were]
- [Operational change: e.g., adds Postgres LISTEN/NOTIFY to runbook]

## Alternatives Considered

### Alternative 1: [Name]

- **Approach:** [1–2 sentences]
- **Why rejected:** [reason]

<!--
  Example:
  Alternative 1: Synchronous Kafka publish with circuit breaker.
  Why rejected: Still couples API latency to Kafka health; circuit
  breaker open state would drop events without persistence.
-->

### Alternative 2: [Name]

- **Approach:** [1–2 sentences]
- **Why rejected:** [reason]

### Alternative 3: [Name]

- **Approach:** [1–2 sentences]
- **Why rejected:** [reason]

## References

- Related ADRs: [ADR-NNN]
- External: [RFC / paper / blog post / spec link]
- Tickets: [JIRA / GitHub issue]
