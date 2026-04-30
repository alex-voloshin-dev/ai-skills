# API Reference — Orders Service v2

> Audience: developer | Template: api-reference

## Overview

The Orders Service exposes 4 endpoints for managing orders. All endpoints require Bearer token auth (`Authorization: Bearer <jwt>`). Responses are JSON; errors follow [RFC 7807 Problem Details](https://tools.ietf.org/html/rfc7807).

Base URL: `https://api.example.com/orders/v2`

## Quickstart

```bash
# 1. Authenticate
TOKEN=$(curl -X POST https://api.example.com/auth/token \
  -d '{"email":"you@example.com","password":"..."}' | jq -r .access_token)

# 2. List orders
curl https://api.example.com/orders/v2 -H "Authorization: Bearer $TOKEN"
```

Tested 2026-04-19 against staging.

## Endpoints

### `GET /orders` — List orders

| Param | Type | Required | Default | Description |
|---|---|---|---|---|
| `status` | string | no | `all` | `all`, `open`, `shipped`, `cancelled` |
| `since` | ISO8601 date | no | (none) | Only orders created on/after this date |
| `limit` | int | no | 50 | Max 200 |

**Response 200:**
```json
{
  "orders": [
    {"id": "ord_abc", "status": "shipped", "total_cents": 4250, "created_at": "2026-04-15T12:34:56Z"}
  ],
  "next_cursor": "cur_xyz"
}
```

**Errors:** 400 (bad params), 401 (no token), 403 (token lacks scope `orders:read`).

### `POST /orders` — Create order

**Body:**
```json
{
  "items": [{"sku": "WIDGET-1", "qty": 2}],
  "shipping_address": {"line1": "...", "postal_code": "..."}
}
```

**Response 201:** Created order body (same shape as GET item).
**Errors:** 400 (validation), 401, 403, 409 (inventory shortfall — body has `available_qty`).

### `GET /orders/{id}` — Get one order

Returns single order. **Errors:** 404 (not found / not your order — same status to avoid info leak).

### `POST /orders/{id}/cancel` — Cancel order

**Body:** none. **Response 200:** Updated order with `status: cancelled`.
**Errors:** 409 (already shipped — cancellable only in `open` status).

## Authentication & Scopes

All endpoints check the JWT `scope` claim:
- `orders:read` — `GET /orders`, `GET /orders/{id}`
- `orders:write` — `POST /orders`, `POST /orders/{id}/cancel`

Token expires after 8h; refresh via `/auth/refresh`.

## Rate Limits

- 100 req/min per token
- 429 with `Retry-After` header when exceeded

## Pagination

`next_cursor` is opaque; pass back as `?cursor=<value>`. Cursor expires after 1h.

## Error Format (RFC 7807)

```json
{
  "type": "https://api.example.com/problems/inventory-shortfall",
  "title": "Inventory shortfall",
  "status": 409,
  "detail": "SKU WIDGET-1: requested 2, available 1",
  "instance": "/orders",
  "available_qty": 1
}
```

## Versioning

v2 is the current API. v1 sunsets 2026-12-31. See [Migration Guide](./MIGRATION-V1-V2.md).

## Related

- [Authentication](../auth/README.md)
- [Webhooks](./WEBHOOKS.md) — order events delivered to your endpoint
