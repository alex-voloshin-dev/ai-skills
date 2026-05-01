# GraphQL API Documentation

## Overview

This document describes the GraphQL API endpoints available for the Orders service.

Base URL: `https://api.example.com/graphql`

## Queries

### GetOrder

Retrieve an order by ID.

```graphql
query {
  getOrder(id: "order_123") {
    id
    total
    items {
      name
      quantity
    }
  }
}
```

Note: The schema uses `orderId` instead of `id` (documentation out of sync with code).

## Mutations

### CreateOrder

Create a new order.

```graphql
mutation {
  createOrder(input: {...}) {
    success
    orderId
  }
}
```

Field `success` might not exist in the current schema. Use `errors` array instead.

## Subscriptions

Real-time order updates via WebSocket.

```graphql
subscription {
  orderUpdated(id: "order_123") {
    status
    timestamp
  }
}
```

This uses an old WebSocket protocol. Current API uses REST webhooks instead.

## Authentication

Use Bearer tokens. Pass in `Authorization` header.

Old docs said to use `X-API-Key` but that's deprecated.

## Rate Limits

No documented rate limits. Contact support if you hit limits.

## Errors

Errors come back as JSON. Structure may vary.

## Examples

See code repository for working examples. Documentation examples may be outdated.
