# Architecture — `<system-name>`

> Aligned with the **C4 model** (https://c4model.com). This document
> covers Level 1 (Context), Level 2 (Container), and key dynamic
> flows. Component-level (L3) and code-level (L4) views live next to
> the relevant module READMEs.

## System context (C4 — Level 1)

```mermaid
C4Context
    title System Context — Acme Orders Platform
    Person(customer, "Customer", "Buys products via web or mobile")
    Person(opsAgent, "Ops agent", "Resolves order issues")
    System(orders, "Orders Platform", "Lets customers place, pay, and track orders")
    System_Ext(stripe, "Stripe", "Card processing")
    System_Ext(sendgrid, "SendGrid", "Transactional email")
    System_Ext(warehouse, "Warehouse WMS", "Fulfillment partner")
    Rel(customer, orders, "Places orders", "HTTPS")
    Rel(opsAgent, orders, "Manages orders", "HTTPS")
    Rel(orders, stripe, "Charges cards", "HTTPS / webhook")
    Rel(orders, sendgrid, "Sends receipts", "HTTPS")
    Rel(orders, warehouse, "Submits shipments", "HTTPS / SFTP")
    UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="1")
```

## Containers (C4 — Level 2)

```mermaid
C4Container
    title Containers — Acme Orders Platform
    Person(customer, "Customer")
    System_Boundary(orders, "Orders Platform") {
        Container(web, "Web app", "Next.js 14", "Customer UI")
        Container(api, "Orders API", "Node.js / Fastify", "REST API for orders")
        Container(worker, "Billing worker", "Node.js", "Charges Stripe; consumes Kafka")
        ContainerDb(pg, "Postgres", "Postgres 16", "Orders, customers, payments")
        ContainerDb(redis, "Redis", "Redis 7", "Cache + idempotency keys")
        ContainerQueue(kafka, "Kafka", "Kafka 3.6", "Domain events")
    }
    System_Ext(stripe, "Stripe")
    Rel(customer, web, "Uses", "HTTPS")
    Rel(web, api, "Calls", "HTTPS / JSON")
    Rel(api, pg, "Reads/writes", "TCP / SQL")
    Rel(api, redis, "Caches + idempotency", "TCP")
    Rel(api, kafka, "Publishes events", "TCP")
    Rel(worker, kafka, "Consumes events", "TCP")
    Rel(worker, stripe, "Charges card", "HTTPS")
    Rel(worker, pg, "Updates payment status", "TCP / SQL")
```

## Key flows

### Flow 1 — Place an order (happy path)

```mermaid
sequenceDiagram
    participant C as Customer
    participant W as Web app
    participant A as Orders API
    participant DB as Postgres
    participant K as Kafka
    participant BW as Billing worker
    participant S as Stripe

    C->>W: Submit checkout
    W->>A: POST /v1/orders
    A->>DB: INSERT order (status=pending)
    A->>K: emit order.created
    A-->>W: 201 Created (order_id)
    W-->>C: Show "processing"
    BW->>K: consume order.created
    BW->>S: charge card
    S-->>BW: payment_intent.succeeded
    BW->>DB: UPDATE order set status=paid
    BW->>K: emit order.paid
```

### Flow 2 — Idempotent retry

```mermaid
sequenceDiagram
    participant C as Client
    participant A as Orders API
    participant R as Redis
    participant DB as Postgres

    C->>A: POST /v1/orders (Idempotency-Key=K)
    A->>R: GET idem:K
    alt cache miss
        A->>DB: INSERT order
        A->>R: SET idem:K = order_id (TTL 24h)
        A-->>C: 201 Created
    else cache hit
        A->>DB: SELECT order by id
        A-->>C: 201 Created (same body)
    end
```

### Flow 3 — Stripe webhook (async settlement)

```mermaid
sequenceDiagram
    participant S as Stripe
    participant A as Orders API
    participant K as Kafka
    participant BW as Billing worker

    S->>A: POST /webhooks/stripe (signed)
    A->>A: verify signature
    A->>K: emit stripe.event.received
    A-->>S: 200 OK
    BW->>K: consume stripe.event.received
    BW->>BW: reconcile order state
```

### Flow 4 — Read-heavy product page

```mermaid
sequenceDiagram
    participant C as Customer
    participant CDN as CDN
    participant W as Web app
    participant A as Orders API
    CDN->>C: serve static assets (cached)
    C->>W: page load
    W->>A: GET /v1/products/:sku
    A->>A: Redis cache lookup
    A-->>W: product JSON
    W-->>C: rendered page
```

### Flow 5 — Refund

```mermaid
sequenceDiagram
    participant Op as Ops agent
    participant A as Orders API
    participant S as Stripe
    participant DB as Postgres
    Op->>A: POST /v1/orders/:id/refund
    A->>S: refund payment_intent
    S-->>A: refund.succeeded
    A->>DB: UPDATE order set status=refunded
    A-->>Op: 200 OK
```

## Tech stack

| Layer | Choice | Version | Why |
|---|---|---|---|
| Web app | Next.js | 14 | SSR + edge rendering |
| API | Node.js + Fastify | 20 LTS / 4.x | Low-overhead JSON API |
| Worker | Node.js | 20 LTS | Code-share with API |
| DB | Postgres | 16 | OLTP + JSONB events |
| Cache | Redis | 7 | Idempotency + hot reads |
| Queue | Kafka | 3.6 | Durable event log |
| Container | Kubernetes (EKS) | 1.29 | Standard cloud target |
| Observability | Prometheus + Loki + Tempo | latest | OSS, OTel-native |

## Quality attributes (non-functional requirements)

See [`NFR.md`](./NFR.md). Headlines:

- **Availability:** 99.95% rolling-30d (Tier 1).
- **p99 latency:** 400 ms on `POST /v1/orders`.
- **Durability:** RPO 5 min, RTO 30 min (Postgres PITR + WAL replication).
- **Security:** SOC 2 Type II; OWASP ASVS L2.
- **Privacy:** GDPR/CCPA — PII in Postgres `pii.*` schema, encrypted at rest with KMS.

## Decisions ledger

Architecture Decision Records live under [`adr/`](./adr/). Notable
recent ones:

- [ADR-0007 — Choose Kafka over RabbitMQ](./adr/0007-kafka-over-rabbitmq.md)
- [ADR-0011 — Postgres JSONB for event payloads](./adr/0011-postgres-jsonb.md)
- [ADR-0014 — Idempotency-Key TTL = 24h](./adr/0014-idempotency-ttl.md)

## Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Stripe outage blocks payments | Low | High | Queue intent; retry with backoff; ops dashboard |
| Postgres single-AZ failure | Low | High | Multi-AZ replica + automated failover |
| Kafka consumer lag during traffic spike | Medium | Medium | Auto-scale workers on lag metric |
| PII leak via logs | Low | High | Log scrubber; SOC 2 audit + DLP scans |
| Vendor lock-in (EKS-specific features) | Medium | Low | Kept to vanilla K8s primitives where possible |
