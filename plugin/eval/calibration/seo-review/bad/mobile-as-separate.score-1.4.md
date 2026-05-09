# SEO Audit Report — Mobile Optimization Section

## 3f. Mobile Optimization

- Mobile-friendly test (Google): PASS
- Viewport meta tag: present
- Tap targets: ≥48px (OK)
- Font sizes: ≥16px on mobile (OK)
- No horizontal scroll on 360px viewport (OK)

## 3g. Mobile Performance

Separately measured:
- Mobile LCP: 2.1s (good)
- Mobile FID: 80ms (good)

## 3e. Desktop Core Web Vitals

- Desktop LCP: 1.4s (good)
- Desktop CLS: 0.05 (good)

(Mobile LCP / desktop LCP measured separately — see Mobile section.)

---

**What's wrong with this output**:

1. **Mobile Optimization is a separate section**. Per the v2026 audit-criteria refresh, mobile-first indexing is universal in 2026 — Google has indexed via the mobile crawler since 2020 and dropped the desktop crawler entirely. There is no longer a meaningful distinction between "mobile" and "desktop" SEO; the mobile experience IS the SEO experience. Section 3f should be folded into 3e Core Web Vitals.
2. **FID measured.** First Input Delay was deprecated in March 2024 and removed from Core Web Vitals. INP (Interaction to Next Paint) replaced it. Reporting FID as if it were live shows the audit is using stale 2023-vintage criteria.
3. **No INP measurement**. INP < 200ms is the modern responsiveness gate; absent here.
4. **Desktop / mobile split for LCP** is the old framing. Single LCP measurement is what matters now. A site that's slow on mobile but fast on desktop fails the whole audit because Google ranks based on mobile.
5. **No HTTP/3 / TLS 1.3 / HSTS** check (modern transport baseline).
