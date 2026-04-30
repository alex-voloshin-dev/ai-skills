# Webhook Integration Guide

> Audience: developer | Template: user-guide

## Overview

Webhooks allow your application to receive real-time notifications when events occur in our system. This guide covers setup, event types, delivery guarantees, and error handling.

Base URL: `https://api.example.com/webhooks/v1`

## Quickstart

1. **Create an endpoint** that accepts POST requests with JSON body:
   ```python
   from flask import Flask, request, jsonify
   
   app = Flask(__name__)
   
   @app.route('/webhook', methods=['POST'])
   def handle_webhook():
       event = request.json
       print(f"Received event: {event['type']}")
       return jsonify({"status": "ok"}), 200
   ```

2. **Register the endpoint:**
   ```bash
   curl -X POST https://api.example.com/webhooks/v1/subscriptions \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "url": "https://yourapp.example.com/webhook",
       "events": ["order.created", "order.shipped"]
     }'
   ```

3. **Your endpoint will receive events** as they occur.

Tested 2026-04-18 against staging.

## Event Types

| Event | Triggers | Payload |
|---|---|---|
| `order.created` | New order submitted | `{"type": "order.created", "order": {...}, "timestamp": "2026-04-20T10:00:00Z"}` |
| `order.shipped` | Order marked shipped | `{"type": "order.shipped", "order_id": "ord_123", "tracking_url": "..."}` |
| `payment.failed` | Payment declined | `{"type": "payment.failed", "order_id": "ord_123", "reason": "card_declined"}` |

## Delivery Guarantees

- **At-least-once delivery:** We retry failed deliveries 5 times with exponential backoff (1s, 2s, 4s, 8s, 16s). After all retries fail, the event is logged but not retried further.
- **In-order delivery:** Events for the same order are delivered in sequence. Events for different orders may arrive out of global order.

## Error Handling

If your endpoint returns 5xx or times out (30s), we count it as a failure and retry. Return 200-299 to confirm successful processing.

**Don't process duplicate events:** Each event has a unique `id` field. Store processed event IDs to detect replays from our retries.

```python
# Example: track processed events
processed_events = set()

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    event = request.json
    if event['id'] in processed_events:
        return jsonify({"status": "ok"}), 200  # Already processed
    processed_events.add(event['id'])
    # Process event...
```

## Security

Every request includes a `X-Webhook-Signature` header. Verify it using your webhook secret:

```python
import hmac
import hashlib

def verify_signature(payload_bytes, signature_header, secret):
    expected = hmac.new(secret.encode(), payload_bytes, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature_header)
```

## Testing

Use the dashboard or API to resend past events to your endpoint for testing. No rate limits on manual resend.

## Troubleshooting

**Not receiving events?**
- Check subscription status: `GET /webhooks/v1/subscriptions/{id}`
- Verify endpoint returns 200 (check our logs on dashboard)
- Check firewall/security group allows inbound from our IP range (documented in dashboard)

**Receiving duplicates?**
- Implement the idempotency check shown above
- Events will retry if your endpoint times out or returns 5xx

