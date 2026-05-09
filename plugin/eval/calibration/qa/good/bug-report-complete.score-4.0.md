# Bug Report — Checkout fails when shipping address contains apostrophe

## Mode: bug-report

## Title
Order placement returns HTTP 500 when shipping `firstName` or `lastName` contains an apostrophe (e.g., O'Brien)

## Severity: S2 (significant — checkout is a primary revenue path; user-visible failure)
## Priority: P1 (immediate fix — affects an estimated 0.4% of all orders by name distribution; revenue impact)

> Severity is the impact of the bug on the system; Priority is the urgency of the fix. They are NOT the same. This bug is mid-impact (S2 — user can use a workaround like "OBrien") but high-priority (P1 — money is on the line).

## Environment
- Web client: Chrome 132, Firefox 134, Safari 17.4 — reproduces on all
- Backend: api-gateway v3.18.2 (production tag, deployed 2026-05-04)
- DB: PostgreSQL 16.2 (managed), connection pool size 20

## Steps to Reproduce (STR)
1. Sign in as any registered user (used `qa+e2e@example.com` for repro).
2. Add any product to cart.
3. Go to Checkout.
4. In Shipping Address, set First Name = `Patrick`, Last Name = `O'Brien`.
5. Fill remaining fields with valid values.
6. Click "Place order".

## Expected
Order is placed; user is redirected to `/orders/<id>`; confirmation email queued.

## Actual
HTTP 500 from `POST /api/orders`. Error toast: "Something went wrong, please try again." User cart is preserved. Order is NOT created (verified in DB).

Server log:
```
ERROR  org.postgresql.util.PSQLException: ERROR: syntax error at or near "Brien"
       at OrderRepository.insertShippingAddress(OrderRepository.java:142)
```

## Reproduction Rate
10 / 10 (100% with the input above). Same with `D'Angelo`, `O'Connor`. Names without apostrophes succeed normally.

## Workaround
End-user: omit the apostrophe (`OBrien`). Not acceptable long-term — names are personal data and should round-trip correctly.

## First-Failure Data Preserved
- Server log line + stack trace: `qa-evidence/order-500-2026-05-09.log`
- Request body (redacted): `qa-evidence/order-500-2026-05-09.req.json`
- Trace ID: `01HZ8K3NX9P2QY5R0WMGHE6V8T` (Honeycomb link in evidence dir)

## Suspected Class
SQL injection-shaped failure, but inside our own code — likely string concatenation in `OrderRepository.insertShippingAddress` instead of a prepared statement. This is a correctness bug AND a latent security issue. Flagging for `/security-audit` follow-up.

## Handoff
- Fix: → `/bugfix` (developer + reviewer + QA pipeline; prepared-statement migration)
- Security review of nearby string-concat sites: → `/security-audit --scope sql`
- Regression test design (covering names with `'`, `"`, `\\`, unicode): → `/test-strategy` then `/run-tests`
