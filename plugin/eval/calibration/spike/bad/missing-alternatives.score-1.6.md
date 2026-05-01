# Spike — Search solution investigation

## Question
What search technology should we use?

## Finding

We should build our own search service. We can index all documents in a custom database and query it with full-text search.

Building custom is the best option. It gives us full control and no vendor lock-in.

## Effort
Maybe 10 weeks to build a production-grade search service. Could be more.

## Trade-offs
None considered. Building custom is the obvious choice.

## Implementation
Start building the search service immediately. Hire a specialist if needed.

## Issues
- Did not evaluate Elasticsearch, Meilisearch, Algolia, or other existing options
- Did not benchmark custom solution vs products
- Did not consider ongoing maintenance cost of custom solution
- Effort estimate is vague and likely underestimated
- No risk assessment for building custom vs using proven product
- No consideration of what "production-grade" entails (failover, backups, monitoring, security)
