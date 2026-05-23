# /knowledge-sync — Keep a repo's knowledge tree in sync with its code

A pair of skills that keeps an internal `knowledge/` documentation tree current as code and a few opt-in external sources change. `/knowledge-sync-init` does the one-time setup; `/knowledge-sync` is the recurring daily run.

## When to use

- You keep living docs in a `knowledge/` tree and want them updated when the code they describe changes, without doing it by hand.
- You want a daily pass that only touches the doc areas affected by recent commits, and costs almost nothing on quiet days.
- You want generated doc changes to arrive as a draft PR for review rather than land directly.

This is for **internal, non-public** knowledge read by teammates and AI agents. It is not a content pipeline: there is no humanizer, SEO, GEO, or schema pass. Public-facing content belongs in `/content-creation` or `/marketing`.

## Not for

- Authoring net-new docs or designing the information architecture from scratch → [`/docs-pack`](docs-pack.md) or `/docs`.
- Public-facing blog, landing, or marketing content → `/content-creation`, `/marketing`.
- Editing source code, configs, or infrastructure. `/knowledge-sync` writes markdown only, inside the knowledge tree.

## How it works

`/knowledge-sync` reads `knowledge/.knowledge-sync.yml`, computes what changed in git since the last recorded baseline, maps those changed paths to the doc areas they feed, and updates only those areas. Each affected area is handled by a `Agent(content-writer)` (with an optional read-only stack role for technical accuracy). By default the result is a draft PR. The baseline only advances when the run finishes cleanly, so a failed or partial run is re-attempted on the next pass rather than dropped.

The plugin does the work; Claude Code's schedule routine runs the clock. There is no cron built into the plugin — the recurring routine's prompt is just `/knowledge-sync`.

## One-time setup: `/knowledge-sync-init`

Run this once per repo. It is interactive and refuses to overwrite an existing config unless you pass `--force`.

```bash
/knowledge-sync-init            # interactive setup; refuses if config already exists
/knowledge-sync-init --force    # re-initialize; preserves the baseline + watermarks unless reset
```

What it does:

1. **Detects the knowledge root.** It reads `CLAUDE.md` / `AGENTS.md` for a link to your docs tree, defaults to `./knowledge` if none is found, and asks you to confirm.
2. **Maps doc areas to source globs.** It inspects the tree and proposes default mappings (for example, `tech-docs` fed by `src/**`, `product` fed by `docs/prd/**`). You confirm or edit each area. Every area needs a `path` and at least one `sources` glob.
3. **Records opt-in external sources.** Linear, Notion, and a changelog (via WebFetch) are offered, all **disabled by default**. A source is only contacted if you explicitly enable it. Credentials never go in the config — auth lives in your environment or MCP layer.
4. **Sets the baseline.** It records the current `HEAD` as `last_scanned_sha` so the first real run only looks at what changed afterward.
5. **Sets the update policy.** The default is `propose` (branch + draft PR). Per-area `direct` is offered only as an explicit, low-risk opt-in.
6. **Writes or seeds `knowledge/CONVENTIONS.md`.** This is the git-versioned style guide the recurring run enforces. If the tree has enough structure, init tailors one; otherwise it seeds the bundled default for you to fill in.
7. **Provisions the L4 memory dir** for per-run logs (`.ai-skills-memory/knowledge-sync/`, gitignored).
8. **Offers to register the daily routine.** It does not auto-schedule. See [Scheduling](#scheduling) below.

Init writes exactly two git-versioned files — `knowledge/.knowledge-sync.yml` and `knowledge/CONVENTIONS.md` — plus the gitignored L4 dir. It never touches source code, configs, or infrastructure.

## The recurring run: `/knowledge-sync`

```bash
/knowledge-sync             # compute delta → update affected areas → propose changes
/knowledge-sync --dry-run   # compute and report the plan; spawn nothing, write nothing
```

If `knowledge/.knowledge-sync.yml` is missing, the run refuses and tells you to run `/knowledge-sync-init` first.

A run goes through these steps:

1. **Read the config** and acquire a run-lock (a second run that finds a fresh lock exits safely).
2. **Compute the git delta** — the read-only diff between `last_scanned_sha` and `HEAD`. A fresh config with no baseline does a bounded first-run backfill instead of regenerating the whole tree.
3. **Query enabled external sources** since their last watermark. A source that is unreachable is skipped (logged, no watermark advance) and the run continues.
4. **Map changes to affected areas** via each area's `sources` globs and each external source's `maps_to`.
5. **Early-exit if nothing is affected.** A quiet day costs one `git diff` and a one-line log — no agent spawns, no PR.
6. **Update each affected area** by spawning one content-writer per area, capped at `budgets.max_areas_per_run` (default 5). The rest queue for the next run; they are not dropped.
7. **Run the pre-write gates** (see [Safety](#safety)) and apply the [conventions](#conventions-enforcement) check before any file is written.
8. **Apply the update policy** — `propose` opens a draft PR; `direct` leaves edits in the working tree.
9. **Advance the baseline only on a clean run**, then write the L4 run record.

`--dry-run` is the safe way to verify your area mapping and config before going live: it reports the delta and the areas it *would* touch, and changes nothing.

## Scheduling

Scheduling is delegated to Claude Code, not built into the plugin. The recurring routine's prompt is simply `/knowledge-sync`. Init offers to register it but never schedules silently.

| Option | Survives Claude Code exiting? | Use it for |
|---|---|---|
| **Remote routine** (recommended) | Yes | A genuinely unattended "every day" run. Init steers you here. |
| Local cron (`CronCreate`) | Only fires on an idle REPL, and recurring jobs auto-expire after 7 days | An always-on dev box, for testing the flow — not true unattended use. |

Init records the chosen `schedule.mechanism` in the config and sets `schedule.registered: true` on acceptance. If you decline, it leaves `registered: false` and tells you how to register later.

## Safety

`/knowledge-sync` is an unattended agent that reads untrusted content and writes files, so several controls are wired in by default.

- **Propose by default.** Changes arrive as a draft PR on an isolated branch. `direct` (in-place edits, left for you to commit) is a per-area opt-in only. The plugin never runs `git commit` or `push` itself — `propose` delegates branch and push to [`/create-pr`](#related).
- **Untrusted content is wrapped at one choke-point.** Every git diff, existing doc read, external-source return, and subagent return passes through the G1 `untrusted-content-wrapping` rule before any agent reasons over it. Injected instructions inside that content are treated as data, never commands.
- **Secret-scan and output-validation gates** run on generated content before any write. A doc containing a secret, or raw `<script>` / `javascript:` markup, is blocked.
- **Path deny-list and traversal guard.** Writes are confined to the knowledge tree. `SECURITY.md`, `LICENSE`, `CONTRIBUTING.md`, and `CODEOWNERS` are always blocked, along with anything you add to `denied_paths` and anything outside `knowledge_root`.
- **External sources are read-only and opt-in.** The run never creates, updates, or deletes on Linear or Notion, and WebFetch only fetches a URL listed in `webfetch_url_allowlist`. A URL found *inside* fetched content is never followed.
- **Budgets hard-abort.** Per-run and per-day token caps, plus the per-run area cap, stop the run before an overrun. An aborted run advances nothing.
- **Baseline advances only on success.** Any block, failure, or partial run leaves `last_scanned_sha` and the source watermarks where they were, so the next run re-attempts the same delta.

## Conventions enforcement

`knowledge/CONVENTIONS.md` is a hard contract on every generated doc, interpreted through the `conventions:` block in the config. Before a doc is written, the run checks it for:

- required front-matter (`title`, `area`, `last_reviewed`, `source_refs` are the non-removable floor; the shipped default adds `owner`),
- a single H1 matching the title, and a kebab-case filename,
- one topic and one Diátaxis mode per doc,
- the **3000-word hard cap** (also non-removable).

Under the default `strict` enforcement, deterministic problems (a missing front-matter key, a wrong filename, an over-cap doc) are auto-fixed or split, then re-checked. Problems that can't be safely auto-fixed — mixed topics, a mixed mode, an internal contradiction — fail the area, so nothing is written for it and the issue is flagged in the draft PR for a human. The `advisory` mode warns instead of blocking. Security gates block regardless of this mode.

## Worked example

Set up once:

```bash
$ /knowledge-sync-init
# Detects knowledge_root: ./knowledge (confirm)
# Proposes area map:
#   tech-docs ← src/**, **/*.proto
#   product   ← docs/prd/**
# External sources: Linear / Notion / changelog — all left disabled
# Baseline last_scanned_sha set to current HEAD
# CONVENTIONS.md generated; offers to register the daily remote routine
# → writes knowledge/.knowledge-sync.yml + knowledge/CONVENTIONS.md
```

A later daily run, after some commits land under `src/`:

```bash
$ /knowledge-sync
# git diff <baseline>..HEAD → 6 changed paths
# affected areas: tech-docs (src/** matched)
# spawns 1 content-writer for tech-docs
# pre-write gates pass; conventions check passes
# opens draft PR: knowledge-sync/2026-05-23T0800-a1b2c3d
# advances last_scanned_sha → HEAD; writes L4 run record
```

A quiet day:

```bash
$ /knowledge-sync
# git diff → no changes mapping to any area
# nothing to update — no fan-out, no PR, baseline unchanged
```

## Config snippet

A trimmed `knowledge/.knowledge-sync.yml`. Init writes the full annotated version.

```yaml
version: 1
knowledge_root: ./knowledge

doc_areas:
  tech-docs:
    path: knowledge/tech-docs/**
    sources:
      - src/**
      - "**/*.proto"
    update_policy: propose
    role_hint: backend-engineer
    enabled: true
  product:
    path: knowledge/product/**
    sources:
      - docs/prd/**
    update_policy: propose
    enabled: true

external_sources:
  linear:
    enabled: false              # opt-in; off means never contacted
    tool: mcp__claude_ai_Linear
    scope: read-only
    watermark: null
    maps_to: [product]

last_scanned_sha: "a1b2c3d4e5f6"

update_policy:
  default: propose              # secure default — branch + draft PR
  pr:
    base: main
    draft: true
    branch_prefix: knowledge-sync/

budgets:
  max_areas_per_run: 5
  max_tokens_per_run: 50000
  max_tokens_per_day: 200000

schedule:
  cadence: daily
  mechanism: remote-routine
  registered: true
```

The only fields `/knowledge-sync` ever writes back are `last_scanned_sha` and each `external_sources[*].watermark`. Everything else is yours.

## Related

- `/knowledge-sync-init` — the one-time setup that writes the config this workflow reads.
- `/create-pr` — opens the draft PR for the `propose` policy.
- `/docs` — the markdown-only doc-update model `/knowledge-sync` reuses for authoring net-new docs.
- [`/docs-pack`](docs-pack.md) — for user-facing documentation packs rather than an internal knowledge tree.
