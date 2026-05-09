# API Reference — `<service-name>`

> Template aligned with **OpenAPI 3.1**. For HTTP APIs, the OpenAPI spec
> (`openapi.yaml`) is the preferred co-output of `/docs-pack` —
> this Markdown reference is generated from it (or hand-kept in sync).

## Overview

`<service-name>` exposes a JSON over HTTPS API for `<one-line purpose>`.

- **Base URL:** `https://api.example.com/v1`
- **Protocol:** HTTPS only (TLS 1.2+)
- **Content type:** `application/json; charset=utf-8`
- **OpenAPI spec:** [`./openapi.yaml`](./openapi.yaml)

## Authentication

All endpoints require a bearer token in the `Authorization` header:

```http
Authorization: Bearer <ACCESS_TOKEN>
```

Tokens are issued via `POST /v1/auth/token` (see endpoint below) and
expire after 1 hour. Refresh with `POST /v1/auth/refresh`.

## Versioning

- URL-versioned: `/v1/...`, `/v2/...`
- Breaking changes bump the major version.
- Deprecation: 6-month overlap window; `Deprecation` and `Sunset`
  response headers (RFC 8594) on retired versions.

## Common patterns

| Concern | Convention |
|---|---|
| Pagination | `?cursor=<opaque>&limit=50` (max 100); response contains `next_cursor` |
| Filtering | Query params: `?status=active&created_after=2026-01-01` |
| Idempotency | `Idempotency-Key: <uuid>` header on `POST` (24h dedup window) |
| Errors | RFC 7807 `application/problem+json` |
| Tracing | Echo `X-Request-Id` from request, or generate if absent |

---

## Endpoint: Create order

### Summary

Create a new order for the authenticated customer.

### Authentication

Bearer token; scope `orders:write`.

### Request

```http
POST /v1/orders HTTP/1.1
Host: api.example.com
Authorization: Bearer <ACCESS_TOKEN>
Content-Type: application/json
Idempotency-Key: 8e3f7c12-9b4a-4f2c-9d1e-2c5e8f4a6d11

{
  "customer_id": "cus_01H8X9...",
  "items": [
    { "sku": "SKU-1234", "quantity": 2 }
  ],
  "currency": "USD"
}
```

**Body schema (request):**

| Field | Type | Required | Notes |
|---|---|---|---|
| `customer_id` | string | yes | ULID prefixed `cus_` |
| `items` | array<Item> | yes | 1–100 items |
| `items[].sku` | string | yes | Product SKU |
| `items[].quantity` | integer | yes | 1–999 |
| `currency` | string | yes | ISO 4217 (e.g. `USD`) |

### Response

**`201 Created`**

```json
{
  "id": "ord_01H8XA...",
  "status": "pending",
  "total_cents": 4998,
  "currency": "USD",
  "created_at": "2026-05-07T12:34:56Z"
}
```

| Status | When |
|---|---|
| `201 Created` | Order accepted; processing started |
| `400 Bad Request` | Validation failed |
| `401 Unauthorized` | Missing or invalid token |
| `403 Forbidden` | Token lacks `orders:write` scope |
| `409 Conflict` | Idempotency-Key reused with different body |
| `422 Unprocessable Entity` | Customer not found or item out of stock |
| `429 Too Many Requests` | Rate limit hit |

### Errors

```json
{
  "type": "https://api.example.com/errors/out-of-stock",
  "title": "Item out of stock",
  "status": 422,
  "detail": "SKU-1234 has 0 units available",
  "instance": "/v1/orders",
  "sku": "SKU-1234"
}
```

| `type` slug | Status | Recovery |
|---|---|---|
| `validation-failed` | 400 | Fix payload per `errors[]` array |
| `out-of-stock` | 422 | Retry later or remove item |
| `rate-limited` | 429 | Honor `Retry-After` header |

### Rate limits

- 100 req/min per token
- 1000 req/min per customer
- `X-RateLimit-Remaining` and `Retry-After` headers returned

### Examples

**curl:**

```bash
curl -X POST https://api.example.com/v1/orders \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: $(uuidgen)" \
  -d '{"customer_id":"cus_01H8X9","items":[{"sku":"SKU-1234","quantity":2}],"currency":"USD"}'
```

**Python (requests):**

```python
import requests, uuid

resp = requests.post(
    "https://api.example.com/v1/orders",
    headers={
        "Authorization": f"Bearer {token}",
        "Idempotency-Key": str(uuid.uuid4()),
    },
    json={
        "customer_id": "cus_01H8X9",
        "items": [{"sku": "SKU-1234", "quantity": 2}],
        "currency": "USD",
    },
    timeout=10,
)
resp.raise_for_status()
order = resp.json()
```

**JavaScript (fetch):**

```js
const resp = await fetch("https://api.example.com/v1/orders", {
  method: "POST",
  headers: {
    "Authorization": `Bearer ${token}`,
    "Content-Type": "application/json",
    "Idempotency-Key": crypto.randomUUID(),
  },
  body: JSON.stringify({
    customer_id: "cus_01H8X9",
    items: [{ sku: "SKU-1234", quantity: 2 }],
    currency: "USD",
  }),
});
if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
const order = await resp.json();
```

### Related endpoints

- `GET /v1/orders/{id}` — fetch order by id
- `POST /v1/orders/{id}/cancel` — cancel pending order
- `GET /v1/customers/{id}/orders` — list a customer's orders

---

> Repeat the **Endpoint** block above for every route. Keep section
> headings identical so the table-of-contents stays predictable.
