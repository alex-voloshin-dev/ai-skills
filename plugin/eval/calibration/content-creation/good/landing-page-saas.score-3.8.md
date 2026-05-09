---
title: "Acme Telemetry — Landing Page"
slug: telemetry
status: published
date: 2026-04-29
dateModified: 2026-04-29
author: marketing-team
tags: [landing, observability]
canonical: https://acme.dev/telemetry
---

# Stop hunting for the bad request

Acme Telemetry is a request tracer for FastAPI and Express that records every inbound request, the SQL it triggered, and the response code — then makes them searchable by header, body, or status. One install, no agents, no sampling.

Three platform engineers tried it on their staging clusters last quarter. They found a stuck N+1 query in 12 minutes, a misrouted feature flag in 4 minutes, and a third-party rate-limit error that had been ignored for 6 weeks.

## What you get above the fold

- **Full request capture** — headers, body, SQL, response, in one record
- **Searchable by anything** — header value, body field, status code, latency bucket
- **Self-hosted or cloud** — same binary, your choice

[Start the 14-day trial](#trial) — no credit card, your data stays in your VPC.

## Why teams switch from APM

Traditional APM samples 1% of traffic. The bad request is in the other 99%. Acme captures everything and indexes it; the storage cost is a flat $40/month per service for the first 100GB.

## How it works

**1. Drop in the middleware.** One line for FastAPI, one for Express. The middleware ships records to Acme over a local socket.

**2. Search.** Open the dashboard, type the request ID, header, or status. Results in under 200ms across 30 days of traffic.

**3. Replay.** Click a request to see the full trace. Hit "replay against staging" to reproduce the bug.

## FAQ

**Does it slow my service down?** Median overhead is 0.4ms per request, measured across 12 production deployments.

**What about PII?** Field-level redaction config; the middleware drops marked fields before the record leaves your process.

**Can I self-host?** Yes — single Docker image, Postgres backend, no external dependencies.

## Trial CTA

Run `pip install acme-telemetry` and add three lines to your app. The trial is wired in 5 minutes; cancel any time during the 14 days.

[Start the trial](https://acme.dev/trial)

---

```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "Acme Telemetry",
  "description": "Request tracer for FastAPI and Express",
  "offers": {"@type": "Offer", "price": "40", "priceCurrency": "USD"}
}
```

## Pipeline notes

- Conversion-centred design (single primary CTA above fold, second after the FAQ).
- GEO + humanizer applied. Definition opener 78 words.
- Step 8 off-site: HN + r/devops short post linking to the page.
