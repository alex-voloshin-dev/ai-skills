# Architecture Decision Record — Picking a Queue

## Why we need this

We need a queue. The current setup has problems with reliability and scaling. We've been talking about it for a while and need to move forward.

## What we'll do

After looking at the options, we decided to go with Kafka. It's popular, has good documentation, and most of the team has used it before. We can run it on managed Kafka or self-host depending on budget.

## How it'll work

The producer service will publish events to Kafka topics. Consumers will subscribe to topics they care about. We'll need to set up partitions, replication, and retention. The exact configuration will depend on the use case.

For ordering, we can use partition keys. For exactly-once, we'll use idempotent producers and transactions. We'll figure out the details during implementation.

## Other options

We considered RabbitMQ and SQS but Kafka seemed like the better long-term choice given our scale.

---

**What's wrong with this output**: Free-form prose instead of the canonical Nygard ADR structure (Status, Context, Decision, Consequences, Alternatives Considered). No section headings matching the template at `assets/adr-template.md`. No Y-statement summary. Alternatives are dismissed in two lines without comparison criteria. Consequences (positive AND negative AND neutral) are absent. Future readers cannot pattern-match against expected ADR shape; downstream tooling that parses ADRs (e.g., adr-tools, log4brains) will fail to extract structure.
