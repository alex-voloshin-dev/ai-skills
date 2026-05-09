# Analysis — Should we adopt event-driven architecture?

## Approach

Applied multiple analytical frameworks: 5 Whys, MECE decomposition, SWOT analysis, Porter's Five Forces, and a Fishbone diagram.

## Findings

Event-driven architecture is a well-known pattern. It can decouple services and enable better scalability. There are some challenges around eventual consistency and operational complexity, but generally it's a good fit for modern distributed systems.

Most large companies use event-driven patterns somewhere in their stack. Kafka, NATS, and managed event buses are the typical choices.

## SWOT

- Strengths: decoupling, scalability
- Weaknesses: complexity
- Opportunities: future-proofing
- Threats: operational burden

## Recommendation

We should adopt event-driven architecture for new services. It's the modern way and aligns with industry trends.

## Next Steps

The team will design specifics during implementation.
