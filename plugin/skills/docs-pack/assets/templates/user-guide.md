# `<product-name>` — User Guide

> Hybrid layout from the **Diátaxis** framework
> (https://diataxis.fr): a **Tutorial** (learning-oriented) followed by
> a set of **How-to guides** (problem-oriented). Reference and
> Explanation belong in separate documents.

## Audience

Builders evaluating or onboarding to `<product-name>` for the first time.

---

# Tutorial — Send your first invoice in 10 minutes

> **Diátaxis quadrant:** Tutorial. Goal is **learning by doing**.
> The reader should finish with a working artifact, not a deep
> understanding of the system.

## Goal

By the end of this tutorial you will have:

- Created an `Acme Co.` workspace.
- Added one customer (`Globex Inc.`).
- Sent a real (test-mode) invoice for `$420.00`.

## Prerequisites

- A web browser (Chrome 120+, Firefox 121+, Safari 17+).
- An email address you can receive mail at.
- 10 minutes.

You do **not** need a credit card. Test mode is free.

## Steps

### 1. Sign up

1. Open https://app.example.com/signup.
2. Enter your email and a password (12+ chars).
3. Click **Create workspace** and name it `Acme Co.`.

### 2. Add a customer

```text
Sidebar → Customers → + New customer
```

Fill in:

- **Name:** `Globex Inc.`
- **Email:** `billing@globex.test`
- **Country:** `US`

Click **Save**.

### 3. Send your first invoice

```text
Sidebar → Invoices → + New invoice
```

1. Pick `Globex Inc.` as the customer.
2. Add a line item: `Consulting — May 2026`, qty `1`, price `420.00`.
3. Toggle **Test mode** on (top-right banner).
4. Click **Send invoice**.

## Verify success

You should see:

- Invoice `INV-0001` listed under **Invoices** with status **Sent**.
- A test-mode email at `billing@globex.test` (visible in the
  workspace's **Test inbox** tab).

## What you learned

- The three core objects: **Workspace → Customer → Invoice**.
- How **test mode** isolates dry-run data from production.
- The basic shape of the navigation: Sidebar → object list → detail.

Next: pick a how-to below for the specific job you actually came to do.

---

# How-to guides

> **Diátaxis quadrant:** How-to. Each guide answers a single
> **"how do I … ?"** question. Assumes you have completed the tutorial
> (or are otherwise oriented) and now need to get a real job done.

## How to import customers from a CSV

1. Prepare a CSV with the headers `name`, `email`, `country`.
2. Go to **Customers → Import**.
3. Click **Upload CSV** and select your file.
4. Map columns if prompted (auto-detected for the headers above).
5. Click **Import**. A progress bar shows N of M rows.
6. Failed rows download as `customers-errors.csv` — fix and re-import.

## How to schedule a recurring invoice

1. Open the customer record.
2. Click **Actions → New recurring invoice**.
3. Pick a cadence: weekly, monthly, or every N days.
4. Set the start date and (optional) end date.
5. Add line items as in the tutorial.
6. Click **Activate**. The next run shows up on the dashboard.

To pause: open the recurring invoice → **Pause**. Past invoices are
unaffected.

## How to connect a payment provider

1. Go to **Settings → Payments**.
2. Choose `Stripe` (other providers in beta).
3. Click **Connect** and complete the OAuth flow.
4. Back in `<product-name>`, click **Verify connection**.
5. Toggle **Accept card payments** on.

Test it: send a test-mode invoice to yourself and click **Pay** — use
card `4242 4242 4242 4242`, any future expiry, any CVC.

## How to invite a teammate

1. **Settings → Members → Invite member.**
2. Enter their email and pick a role (`admin`, `editor`, `viewer`).
3. Click **Send invite** — they get an email with a 7-day link.
4. Once accepted, their name shows up in the member list.

## How to export your data

1. **Settings → Data → Export.**
2. Pick the objects to export (customers, invoices, payments).
3. Pick the format: `CSV` or `JSON`.
4. Click **Generate export** — large exports run in the background.
5. Download the file from the **Recent exports** list (or the email
   link). Files are kept for 30 days.

---

## Where to next

- **Reference:** full schema and field-level docs → `API-REFERENCE.md`.
- **Explanation:** how billing cycles and proration work →
  `concepts/billing.md`.
- **Operator runbook:** for self-hosted installs → `RUNBOOK.md`.
