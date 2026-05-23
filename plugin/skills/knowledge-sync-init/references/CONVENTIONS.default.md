---
title: Knowledge base conventions
area: meta
owner: "<TODO: team or person who owns these conventions>"
last_reviewed: "<YYYY-MM-DD>"
source_refs:
  - ai-skills knowledge-sync (default template)
---

# Knowledge base conventions

> Seeded by `/knowledge-sync-init` from the ai-skills default template. **Edit it
> to fit this repo** — `/knowledge-sync` reads this file and **strictly enforces
> it on every run**. This is *internal* knowledge: optimize for accuracy,
> indexability, and accessibility — not for public reach.
>
> Placeholders marked `<...>` and `<!-- knowledge-sync-init: ... -->` are filled
> in when init *generates* a tailored guide; when init only *templates*, leave
> them for a human to complete.

## Stance: this is internal, non-public knowledge

The `knowledge/` tree is read by teammates and by AI agents doing work — not by
search engines or prospects. So the public-content pipeline does **not** apply:
**no humanizer, no SEO/GEO/AEO, no schema.org/JSON-LD, no marketing voice.**
Public-facing content belongs elsewhere (`/content-creation`, `/marketing`).

Every rule below serves one of three goals:

- **Accuracy** — a doc faithfully reflects its sources and never silently drifts.
- **Indexability** — an agent, `grep`, or a future semantic index finds the right
  doc and the right passage fast.
- **Accessibility** — a doc is cheap to read in full and predictable in shape.

## Required front-matter

Every synced doc MUST begin with YAML front-matter. These keys are the
**non-overridable minimum**: `title`, `area`, `last_reviewed`, `source_refs`.

```yaml
---
title: <human title, matches the H1>
area: <one of the configured areas, e.g. product | tech-docs | runbooks>
owner: <team or person accountable for this doc>
last_reviewed: <YYYY-MM-DD>     # bumped whenever the doc is verified against source
source_refs:                    # what this doc is derived from — enables drift detection
  - <path/glob, ticket, URL, or doc id>
status: current                 # optional: current | draft | deprecated
tags: []                        # optional: free-form retrieval hints
---
```

`source_refs` is what makes `/knowledge-sync` able to tell *which* doc a change
affects — keep it accurate. `last_reviewed` is how staleness is measured.

## Document size

Size is a signal, not a goal: **split by topic, not by length.** An over-cap doc
almost always holds more than one topic.

| Bound | Value | What happens |
|---|---|---|
| Target | **~1 500 words** (~2 000 tokens) | read verbatim by writers/readers; clean retrieval boundaries |
| Soft cap | **~2 000 words** | `/knowledge-sync` flags "consider splitting" in the PR |
| **Hard cap** | **3 000 words** | `/knowledge-sync` MUST split the doc — non-overridable floor |

Default split strategy: **by H2 topic** (each H2 section becomes its own doc, with
a short index doc linking them).

## One topic, one mode, per doc

- **One topic per doc.** If a title needs "and", it is probably two docs.
- **One Diátaxis mode per doc.** Do not mix modes — it blocks both reading and
  retrieval. Pick one:

| Mode | Answers | Example title |
|---|---|---|
| **Tutorial** | "Teach me, step by step" | `getting-started-with-billing.md` |
| **How-to** | "Help me do X" | `rotate-api-keys.md` |
| **Reference** | "Tell me the facts" | `billing-api-reference.md` |
| **Explanation** | "Help me understand why" | `why-we-chose-event-sourcing.md` |

## Structure

- **Single H1** per doc, matching the front-matter `title`.
- **Answer-first.** The first sentence under each H2 fully answers the section's
  implied question; detail follows.
- **≤ 9 H2 sections.** More usually means the doc holds several topics — split.
- **Table of contents** for any doc over ~1 200 words.
- **One idea per paragraph.** Do not join unrelated points with "however"/"but".
- **Name the entity.** Do not open a paragraph with `It`, `This`, or `They`
  referring back across sections — name the thing, so the passage stands alone.

## Naming

- **Files:** `kebab-case.md` (e.g. `rotate-api-keys.md`).
- **One H1 per file**; headings are sentence case.
- **Stable anchors:** do not rename headings casually — links and retrieval depend
  on them. When you must rename, update referrers in the same change.

## Accuracy & consistency rules

- **Cite the source.** Every non-obvious fact traces to a `source_refs` entry.
- **Link, don't duplicate.** State a fact in exactly one canonical doc; elsewhere,
  link to it. Duplication is how a KB starts to contradict itself.
- **No dead docs.** Mark superseded docs `status: deprecated` with a link to the
  replacement, or remove them — do not leave silently-wrong docs in place.
- **Bump `last_reviewed`** whenever you verify a doc against its source.

## What `/knowledge-sync` enforces, and how

Before writing any generated/updated doc, `/knowledge-sync` runs a conformance
check against this file:

- front-matter present and valid (required keys above),
- doc within the hard cap (else split by the configured strategy),
- single H1; filename matches the naming pattern,
- one topic / one Diátaxis mode per doc.

Outcomes:

- **Deterministic violations** (missing front-matter key, wrong filename case,
  over-cap) → **auto-fixed or split**.
- **Non-deterministic violations** (mixed topics, internal contradiction) → the
  area **fails** and is **flagged in the draft PR** for a human.
- Under `enforcement: strict` (the default), a non-conforming doc is **never
  written** — it is corrected first, or the area is flagged.

## The non-overridable floor

A repo may make these conventions **stricter**, never weaker than:

- required front-matter keys: `title`, `area`, `last_reviewed`, `source_refs`;
- the **3 000-word hard cap**;
- **propose-only** writes by default (changes arrive as a draft PR for review).

## Excluded from sync

These are human-owned and not rewritten by `/knowledge-sync`:

- this `CONVENTIONS.md`,
- `README.md` / index scaffolding you mark as manual,
- anything outside the configured `knowledge_root`,
- the deny-listed paths (`SECURITY.md`, `LICENSE`, `CONTRIBUTING.md`, `CODEOWNERS`).

## Areas in this repo

<!-- knowledge-sync-init: fill from .knowledge-sync.yml doc_areas; one row per area -->

| Area | Path | Default mode | Owner |
|---|---|---|---|
| `<area>` | `knowledge/<area>/**` | `<reference\|how-to\|…>` | `<owner>` |

> Keep this table in sync with `doc_areas` in `knowledge/.knowledge-sync.yml`.
