# Architecture Decision: Use Kafka for Event Streaming

## Status
Accepted

## Context
We need a way to handle event streaming between our services. Currently we use direct HTTP calls which creates tight coupling. We want to decouple services so they can evolve independently and scale separately.

## Decision
Use Apache Kafka as our event streaming platform. Kafka is the industry standard for event streaming and is used at scale by LinkedIn, Netflix, Uber, and many others. It supports high throughput, durability, exactly-once semantics, and a rich ecosystem of connectors.

## Consequences
- We can decouple our services
- Events can be replayed for debugging
- We can support new use cases like analytics and ML pipelines
- Kafka has great tooling and a strong community

## Alternatives Considered

We did not seriously consider alternatives because Kafka is clearly the right choice for this scale.

---

**What's wrong with this output**: Advocacy framing — the decision is presented as obviously correct without comparison. "Alternatives Considered" section is the most important part of an ADR (per Nygard) and here it's a single dismissive sentence. Real alternatives at this scale: NATS JetStream (lower operational footprint, native exactly-once), Apache Pulsar (multi-tenancy, geo-replication built in), AWS Kinesis or Google Pub/Sub (managed, less ops), Redpanda (Kafka-API compatible, no JVM/Zookeeper). Each has tradeoffs vs Kafka — operational complexity, latency tail, multi-region support, vendor lock-in. The ADR should compare on 4-6 dimensions and explain why Kafka wins on the dimensions THIS team values. "Industry standard" alone is not a decision rationale; it's bandwagon argument.
