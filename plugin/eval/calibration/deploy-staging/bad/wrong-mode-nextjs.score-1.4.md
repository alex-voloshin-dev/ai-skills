# Staging deploy: marketing-site (Next.js)

## Detect

Next.js project (`next.config.js`, `package.json` → "next": "^15.0.2").

## Build

```bash
$ npm run build
> next build
✓ Compiled successfully

$ npx next export
✓ Exported HTML to ./out
```

## Deploy

```bash
$ aws s3 sync ./out s3://marketing-staging.acme.dev --delete
$ aws cloudfront create-invalidation --distribution-id E2QH... --paths "/*"
```

Static site deployed to S3 + CloudFront.

---

**What's wrong with this output**:

1. **`next export` runs but the project uses dynamic features**. Inspecting `app/blog/[slug]/page.tsx` shows `export const dynamic = 'force-dynamic'` AND `app/api/contact/route.ts` exists (server-only API route). Static export drops both — the blog will 404 on every dynamic slug; the contact form returns the static HTML of the form page, not the API response.
2. **Skill's Step 1c row says "Static site (Next.js, Vite) → CDN / static hosting"** — but Next.js has multiple deploy modes (static / ISR / RSC streaming / Edge runtime). Picking the right mode requires inspecting the app, not the project type alone:
   - **Static export** (`output: 'export'`): only when ALL routes are statically generatable
   - **Node server**: full SSR + API routes; deploy as container or Vercel Node runtime
   - **Edge runtime**: middleware + edge routes; deploy to Vercel Edge / Cloudflare Workers
   - **ISR** (Incremental Static Regeneration): server-side revalidation; needs persistent cache
3. This Next.js 15 app needs the **Node server** path. Container deploy via the project's `Dockerfile` was the right answer, not S3 static hosting.
4. **Smoke would have caught it.** Even a 1-line `curl https://marketing-staging.acme.dev/api/contact -X POST -d '{...}'` would have shown the broken API route. Skill's smoke step skipped.
