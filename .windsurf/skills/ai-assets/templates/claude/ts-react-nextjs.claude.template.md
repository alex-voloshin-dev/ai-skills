# AGENTS.md

## Project Overview

This is a TypeScript React/Next.js application. [DESCRIBE YOUR PROJECT PURPOSE HERE].

**Architecture**: See [ARCHITECTURE.md](./ARCHITECTURE.md) for system design, component relationships, data flows, and deployment topology.

## Setup Commands

```bash
# Install dependencies
pnpm install

# Run development server
pnpm dev

# Build for production
pnpm build

# Run tests
pnpm test

# Lint
pnpm lint

# Type check
pnpm typecheck
```

## Code Style and Conventions

- TypeScript strict mode enabled
- React 18+ with functional components and hooks only
- Next.js App Router (app/ directory)
- Use named exports, not default exports
- File naming: `ComponentName.tsx`, `useHookName.ts`, `utilName.ts`
- Use CSS Modules or Tailwind CSS for styling
- Use `interface` for object shapes, `type` for unions/intersections
- Prefer `const` over `let`, never use `var`
- Use early returns to reduce nesting

## Project Structure

```
app/
├── layout.tsx           # Root layout
├── page.tsx             # Home page
├── (routes)/            # Route groups
│   └── dashboard/
│       ├── page.tsx
│       └── layout.tsx
├── api/                 # API routes
│   └── [resource]/
│       └── route.ts
components/
├── ui/                  # Reusable UI primitives
├── features/            # Feature-specific components
└── layouts/             # Layout components
lib/
├── api/                 # API client functions
├── hooks/               # Custom React hooks
├── utils/               # Utility functions
└── types/               # Shared TypeScript types
```

## Testing Instructions

- Unit tests: Vitest + React Testing Library
- Test files: `ComponentName.test.tsx` next to component
- Focus on user behavior, not implementation details
- Use `screen.getByRole()` over `getByTestId()` where possible
- Run `pnpm test` before committing

## Content Architecture

<!-- Remove this section if the project has no static content files -->

### Static Content Files

| Content File | Sections / Exports | Used By Pages |
|---|---|---|
| `src/lib/static-content/[name]-content.ts` | `[exported objects/arrays]` | `[page routes]` |

### SEO Metadata Locations

| Page | SEO Metadata In | Structured Data (JSON-LD) |
|---|---|---|
| `/` | `app/(home)/page.tsx` — `metadata` export | `[WebSite, Organization, FAQPage, etc.]` |
| `/[page]` | `app/[page]/page.tsx` — `metadata` or `generateMetadata()` | `[schema types]` |

### Content Sync Rules
- When updating visible text, also update: `metadata` export, OpenGraph, JSON-LD schemas
- If homepage shows a curated subset (e.g., 5 of 20 FAQs), both the subset array and full content file must stay in sync
- JSON-LD `FAQPage` must contain ONLY the questions visible on that specific page
- See `content-creation` skill → `seo-content-sync-checklist.md` for the full checklist

### Blog Content

<!-- Remove this sub-section if the project has no file-based blog content -->

- **Blog directory**: `[e.g., content/blog/]`
- **File format**: `.mdx` (MDX with React components) / `.md`
- **File naming**: `kebab-case.mdx` — derived from URL slug. Route: `/blog/[slug]`
- **Frontmatter format**:

| Field | Type | Required | Example |
|---|---|---|---|
| `title` | string | yes | `"How to Optimize API Performance"` |
| `description` | string | yes | `"Learn practical techniques for..."` |
| `author` | string | yes | `"Jane Smith"` |
| `[date field]` | date | yes | `2025-01-15` |
| `[tags field]` | string[] | no | `["performance", "api"]` |
| `[image field]` | string | no | `"/blog/covers/api-perf.webp"` |
| `[status field]` | string | yes | `"published"` / `"draft"` |

- **Cover images**: `public/blog/covers/` — naming: `[slug].webp`. Use `next/image` with `width`/`height`
- **Valid tags/categories**: `[list or path to config]`
- **Cross-linking**: Minimum 3 internal links per post. Descriptive anchor text
- **MDX components**: `[e.g., Callout, CodeBlock, Image — imported from components/mdx/]`
- **Discovery assets**:
  - `llms.txt`: `public/llms.txt` — update when adding posts
  - Sitemap: `app/sitemap.ts` — `[auto-generated / manual entries needed]`
  - RSS: `[e.g., app/feed.xml/route.ts — auto / manual]`
- **Structured data**: `BlogPosting` JSON-LD — `[auto-injected by layout / manual per post]`
- **Workflows**: Use `/blog-post` for new posts, `/docs` for content fixes

## UI Conventions

- **Component library**: [e.g., shadcn/ui, Radix UI primitives, custom]
- **Icon set**: [e.g., Lucide, Solar, Phosphor] — variant: [e.g., outline, bold-duotone]
- **Icon registry**: [e.g., `src/components/ui/icon-sets.ts` — all icons must be registered here before use]
- **Styling**: Tailwind CSS — config in `tailwind.config.ts`
- **Animation library**: [e.g., framer-motion] — pattern: [e.g., viewport-triggered with `whileInView`, requires scroll-through for screenshots]
- **Design tokens**: `tailwind.config.ts` (colors, spacing, typography)
- **Image optimization**: `next/image` with WebP/AVIF. Static assets in `public/`

## Context Engineering

<!-- Remove this section if the project has no AI/LLM features -->

- **Context stack policy**: [Token budget allocation per layer, cacheable prefix design]
- **Memory approach**: [Memory types used, storage backend, conflict resolution]
- **RAG pipeline**: [Embedding model, vector store, reranking, chunking strategy]
- **Tool result handling**: [Normalization and untrusted wrapping policy]
- **Multi-tenant isolation**: [Retrieval-time tenant filtering approach]
- **Production checklists**: Use `context-engineering` skill → `production-checklists.md` before AI feature launch

## AI Tooling Notes

- **Ignored paths**: [e.g., `.next/`, `node_modules/`, paths in `.codeiumignore`]
- **Screenshot storage**: `qa/screenshots/` (not `tmp/` — blocked by `.codeiumignore`). Add `qa/screenshots/*.png` to `.gitignore`
- **Dev server**: `pnpm dev` → `http://localhost:3000`
- **SPA animation note**: Pages with framer-motion viewport-triggered animations require scroll-through before full-page Playwright capture (see `ui-ux-design` skill → `visual-audit-checklist.md`)

## Security Considerations

- Never expose API keys on the client — use server-side API routes
- Sanitize user input before rendering (React handles XSS by default, but watch `dangerouslySetInnerHTML`)
- Use `next/headers` for secure cookie handling
- Validate API inputs with Zod schemas

## PR Instructions

- Title format: `[component] Brief description`
- Run `pnpm lint && pnpm typecheck && pnpm test` before submitting
