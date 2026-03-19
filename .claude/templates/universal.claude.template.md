# CLAUDE.md

## Project Overview

[PROJECT_NAME] is a [BRIEF_DESCRIPTION — 1-3 sentences: what this project does, who it's for, key domain concepts].

**Architecture**: See [ARCHITECTURE.md](./ARCHITECTURE.md) for system design, component relationships, data flows, and deployment topology.

## Setup Commands

```bash
# Install dependencies
[INSTALL_COMMAND]

# Start development server
[DEV_COMMAND]

# Run tests
[TEST_COMMAND]

# Build for production
[BUILD_COMMAND]

# Lint and format
[LINT_COMMAND]
```

## Tech Stack

- **Language**: [e.g., TypeScript 5.x, Java 21, Python 3.12, Go 1.22]
- **Framework**: [e.g., Next.js 15, Spring Boot 3, FastAPI, Gin]
- **Database**: [e.g., PostgreSQL 16, MongoDB 7, Redis 7]
- **Infrastructure**: [e.g., Docker, Kubernetes, Terraform, AWS/GCP/Azure]
- **CI/CD**: [e.g., GitHub Actions, GitLab CI, Jenkins]

## Code Style and Conventions

- [Language version and strict mode settings]
- [Naming conventions: files, classes, functions, variables]
- [Import organization rules]
- [Error handling patterns]
- [Logging conventions]
- [Key architectural patterns used (e.g., hexagonal, layered, CQRS)]

## Project Structure

```
[PROJECT_ROOT]/
├── [dir1]/          # [Brief description]
├── [dir2]/          # [Brief description]
│   ├── [subdir]/    # [Brief description]
│   └── [subdir]/    # [Brief description]
├── [dir3]/          # [Brief description]
├── [config_file]    # [Brief description]
└── [config_file]    # [Brief description]
```

## Testing Instructions

**Full testing guide**: See [TESTING.md](./TESTING.md) for complete testing documentation — test types, infrastructure, credentials, per-service guides, and CI/CD pipeline.

- **Unit tests**: [framework, command, naming convention]
- **Integration tests**: [framework, command, setup requirements]
- **E2E tests**: [framework, command, if applicable]
- **Coverage target**: [e.g., 80%+ for business logic]
- Run all tests before committing: `[TEST_COMMAND]`

## Content Architecture

<!-- Remove this section if the project has no static content management -->

| Content File | Sections / Exports | Used By Pages |
|---|---|---|
| `[content-file-path]` | `[exported sections]` | `[page routes]` |

### SEO Metadata Locations

| Page | SEO Metadata In | Structured Data (JSON-LD) |
|---|---|---|
| `/` | `[page.tsx or layout.tsx path]` | `[schema types]` |

### Content Sync Rules
- When updating visible text, also update: SEO metadata, OpenGraph, JSON-LD structured data
- If page shows a subset of a larger collection (e.g., homepage FAQ subset), both sources must stay in sync
- See `content-creation` skill → `seo-content-sync-checklist.md` for the full checklist

### Blog Content

<!-- Remove this sub-section if the project has no file-based blog content -->

- **Blog directory**: `[e.g., content/blog/, posts/, app/blog/]`
- **File format**: `[.mdx / .md]`
- **File naming**: `kebab-case[.mdx/.md]` — derived from URL slug
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

- **Cover images**: `[e.g., public/blog/covers/]` — naming: `[slug].webp`
- **Valid tags/categories**: `[list or path to config]`
- **Cross-linking**: Minimum 3 internal links per post. Descriptive anchor text
- **Discovery assets**:
  - `llms.txt`: `[path, e.g., public/llms.txt]` — update when adding posts
  - Sitemap: `[path, e.g., app/sitemap.ts]` — auto-generated / manual
- **Workflows**: Use `/blog-post` for new posts, `/docs` for content fixes

## UI Conventions

<!-- Remove this section if not applicable -->

- **Component library**: [e.g., shadcn/ui, MUI, Chakra UI, custom]
- **Icon set**: [e.g., Lucide, Solar, Phosphor, Heroicons] — variant: [e.g., outline, bold-duotone]
- **Icon registry**: [path to icon registry file, if applicable]
- **Styling**: [e.g., Tailwind CSS, CSS Modules, styled-components]
- **Animation library**: [e.g., framer-motion, GSAP, CSS transitions only]
- **Animation pattern**: [e.g., viewport-triggered with `whileInView`, page transitions, none]
- **Design tokens**: [path to token config, e.g., `tailwind.config.ts`, `tokens/`]

## Context Engineering

<!-- Remove this section if the project has no AI/LLM features. Add if project includes RAG, agents, memory, or LLM integrations. -->

- **Context stack policy**: [How context is organized — which layers are used, token budget allocation per layer]
- **Memory approach**: [Which memory types are used: session, working, long-term, organizational, tool-output. Storage backend. Conflict resolution policy]
- **RAG pipeline**: [Retrieval architecture: embedding model, vector store, reranking approach, chunking strategy]
- **Tool result handling**: [How tool outputs are normalized and wrapped before context injection]
- **Multi-tenant isolation**: [How tenant boundaries are enforced at retrieval and memory layers]
- **Production checklists**: Use `context-engineering` skill → `production-checklists.md` (8 checklists) before AI feature launch

## AI Tooling Notes

<!-- Remove this section if not applicable -->

- **Ignored paths**: [paths blocked by `.codeiumignore` or `.cursorignore` that AI tools cannot read/write]
- **Screenshot storage**: `qa/screenshots/` (add `qa/screenshots/*.png` to `.gitignore`)
- **Dev server command**: [exact command to start dev server for browser preview]
- **Browser preview URL**: [e.g., `http://localhost:3000`]

## Security Considerations

- Never log sensitive data (passwords, tokens, PII)
- Store secrets in environment variables or secret managers — never in source code
- Validate all external inputs
- [Project-specific auth approach]
- [Project-specific data protection requirements]

## PR Instructions

- Title format: `[component] Brief description`
- Run lint and tests before committing
- Include migration scripts if DB schema changes
- Ensure backward compatibility for API changes
- [Project-specific PR checklist items]
