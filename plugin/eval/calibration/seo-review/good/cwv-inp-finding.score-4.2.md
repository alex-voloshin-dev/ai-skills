# SEO Audit Report — example.com/pricing (Core Web Vitals deep dive)

> Date: 2026-04-28
> Scope: /pricing
> Role applied: seo-engineer
> Audit type: performance (CWV + transport)

## Page Reviewed: 1

## Findings

### Critical: INP regression — 312ms (target < 200ms)

PageSpeed Insights field data shows p75 INP at 312ms over the last 28-day window, regressed from 174ms two months ago. CrUX confirms.

**Root cause traced:**

1. Lighthouse trace shows main-thread block of 218ms on the `mouseover` event of the pricing toggle button.
2. The handler triggers a synchronous initialization of the embedded Calendly widget — added in PR #2104 on 2026-03-12 (matches regression onset).
3. Calendly's `widget.js` parses 240KB of JS on mount. Mounting on `mouseover` rather than `click` makes every hover incur the cost.

**Fix:** lazy-mount Calendly on `click`, not `mouseover`. Defer the script tag with `defer` and use `IntersectionObserver` to preconnect when the booking section enters viewport.

**Code change** (delegate: frontend-engineer):
```jsx
// Before — mounts on hover, blocks INP
<button onMouseEnter={initCalendly}>Book a demo</button>

// After — mounts on click, preconnects when visible
<button onClick={openCalendly}>Book a demo</button>
<link rel="preconnect" href="https://calendly.com" />
```

**Verification:** re-run PageSpeed Insights after deploy, confirm INP < 200ms; monitor field data for 14 days.

### LCP — 1.9s (PASS, < 2.5s target)
Hero image is `<img loading="eager" fetchpriority="high">` with WebP at 1280w. Good.

### CLS — 0.04 (PASS, < 0.1 target)
Reserved space for the pricing table; no layout shift after font swap.

### Transport baseline

`curl -I --http3 https://example.com/pricing` returns:
- `:status: 200`
- `alt-svc: h3=":443"; ma=86400`  → HTTP/3 advertised
- TLS 1.3 negotiated (verified via `openssl s_client -tls1_3`)
- `strict-transport-security: max-age=63072000; includeSubDomains; preload` → HSTS set

All transport-baseline checks pass.

## Scores

- LCP: 1.9s
- INP: 312ms (FAIL — fix above)
- CLS: 0.04
- HTTP/3: enabled
- TLS 1.3: served
- HSTS: set with preload

## Sub-steps applied
3e only (CWV + Mobile + Transport, audit type scoped to performance per user request).
