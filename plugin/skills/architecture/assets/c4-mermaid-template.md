# C4 Diagrams — Mermaid Template

The C4 model (https://c4model.com) describes software architecture at four zoom levels: **Context** (system in its environment with users and external systems), **Container** (high-level deployable units — apps, services, databases), **Component** (modules inside a container), and **Code** (classes, functions). For most architecture documentation the Context and Container levels are sufficient — Component and Code views are produced on demand for areas under active redesign.

The blocks below use Mermaid's native `C4Context` and `C4Container` syntax (Mermaid 8.13+). Render them in any Markdown viewer that ships Mermaid (GitHub, GitLab, Obsidian, Mermaid Live).

## Level 1 — System Context

Shows the system as a single box, surrounded by users and external systems it interacts with. No internal detail.

```mermaid
C4Context
    title System Context — Acme Order Platform

    Person(customer, "Customer", "Places and tracks orders via web or mobile")
    Person(opsAgent, "Ops Agent", "Resolves order issues, processes refunds")

    System(orderPlatform, "Order Platform", "Accepts orders, tracks fulfillment, handles payments and notifications")

    System_Ext(stripe, "Stripe", "Payment processing")
    System_Ext(sendgrid, "SendGrid", "Transactional email")
    System_Ext(warehouse, "Warehouse WMS", "Pick/pack/ship — third-party logistics")

    Rel(customer, orderPlatform, "Places orders, checks status", "HTTPS")
    Rel(opsAgent, orderPlatform, "Manages orders", "HTTPS")
    Rel(orderPlatform, stripe, "Charges cards", "REST/HTTPS")
    Rel(orderPlatform, sendgrid, "Sends confirmations", "REST/HTTPS")
    Rel(orderPlatform, warehouse, "Submits fulfillment requests", "EDI/SFTP")

    UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="1")
```

## Level 2 — Container

Zooms into the system. Each container is something that runs as a separately deployable unit (web app, API, worker, database, cache, queue). Show the major data flows and the protocols.

```mermaid
C4Container
    title Container Diagram — Acme Order Platform

    Person(customer, "Customer", "Places and tracks orders")

    System_Boundary(orderPlatform, "Order Platform") {
        Container(webApp, "Web App", "Next.js, TypeScript", "Server-rendered storefront and account pages")
        Container(apiService, "Order API", "Go, Gin", "Order, payment, and fulfillment endpoints")
        Container(worker, "Order Worker", "Go", "Async outbox dispatch, retry, refunds")
        ContainerDb(postgres, "Order DB", "PostgreSQL 16", "Orders, customers, outbox table")
        ContainerDb(redis, "Cache", "Redis 7", "Session, rate limit, hot product cache")
        ContainerQueue(kafka, "Event Bus", "Kafka", "order.created, order.fulfilled, payment.captured")
    }

    System_Ext(stripe, "Stripe", "Payment processing")
    System_Ext(warehouse, "Warehouse WMS", "Fulfillment")

    Rel(customer, webApp, "Browses, checks out", "HTTPS")
    Rel(webApp, apiService, "Calls", "JSON/HTTPS")
    Rel(apiService, postgres, "Reads, writes orders + outbox", "TCP/SQL")
    Rel(apiService, redis, "Sessions, rate limits", "TCP/RESP")
    Rel(worker, postgres, "Tails outbox via LISTEN/NOTIFY", "TCP/SQL")
    Rel(worker, kafka, "Publishes domain events", "TCP")
    Rel(worker, stripe, "Captures and refunds", "REST/HTTPS")
    Rel(kafka, warehouse, "Fulfillment events (Connector)", "EDI/SFTP")

    UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="1")
```

## Conventions

- One Mermaid block per level — keep them in the same Markdown file under `## Level 1 — System Context`, `## Level 2 — Container`, etc.
- Use `Person`, `System`, `System_Ext`, `Container`, `ContainerDb`, `ContainerQueue` element types — do not invent new shapes.
- Label every `Rel(...)` with a verb + protocol (e.g., `"Reads orders", "JSON/HTTPS"`).
- Keep external systems on the diagram boundary; do not bury them inside the system box.
- For Level 3 (Component) and Level 4 (Code), create separate files named `c4-component-<container>.md` and `c4-code-<component>.md` rather than stacking all four levels in one document.
