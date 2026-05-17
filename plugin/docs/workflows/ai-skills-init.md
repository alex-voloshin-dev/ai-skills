# /ai-skills-init — Bootstrap a target repository

One-time (or re-runnable) setup. Creates `CLAUDE.md` scaffold + `.ai-skills-memory/` tree + `.gitignore` rules. Idempotent.

## When to use

- First run of any ai-skills workflow on a fresh repo
- Adopting the ai-skills plugin in an existing repo (new for the team)
- After upgrading the plugin to a version that adds new memory paths or templates

## Not for

- Re-initializing only memory (use `/memory-init` for that)
- Modifying an existing `CLAUDE.md` (manual edit — this skill never overwrites without `--overwrite`)

## How to invoke

```bash
/ai-skills-init
/ai-skills-init --codebase-type python-flask
/ai-skills-init --overwrite                  # rare; only when CLAUDE.md is empty/stale
```

| Flag | Default | Effect |
|---|---|---|
| `--codebase-type` | auto-detect | `python-flask`, `python-fastapi`, `nodejs-express`, `nodejs-nextjs`, `java-spring`, `go`, `ruby-rails`, `rust`, `dotnet`, `mixed`, `generic` |
| `--overwrite` | false | If `CLAUDE.md` exists, OVERWRITE with fresh scaffold |

## What you get

- `<repo>/CLAUDE.md` — scaffolded with codebase type, empty sections for you to fill (skipped if already exists)
- `<repo>/AGENTS.md` — empty template listing the 26 plugin agents (skipped if exists)
- `<repo>/.ai-skills-memory/` directory tree (per [`/memory-init`](feature-design.md))
- `<repo>/.gitignore` — appended `.ai-skills-memory/` rule (preserved if already present)

## How it works

1. **Auto-detect codebase type** — checks for Pipfile, package.json, pom.xml, go.mod, Cargo.toml, Gemfile, *.csproj
2. **Generate CLAUDE.md scaffold** — Overview, Tech Stack (auto-filled), Directory Layout (detected), Key Decisions (blank), Constraints (blank), Getting Started (blank)
3. **Generate AGENTS.md** — lists 26 plugin agents with brief role descriptions
4. **Create .ai-skills-memory/ tree** — gitignore template, .committed/ subdir with allowlist, config.json stub, learnings.md template, workflow subdirs
5. **Update root .gitignore** — adds `.ai-skills-memory/` rule + `.committed/` exception (negation)
6. **Print summary** — files created vs skipped + next steps

No RALF — scaffolding is one-pass + idempotent.

## Idempotence

Re-running on a fully-set-up repo is a no-op. The skill detects existing files and skips them, reporting "skipped: <path>" rather than overwriting. The only override is `--overwrite` for `CLAUDE.md` specifically.

## Common questions

**Will it overwrite my CLAUDE.md?**
No — never without `--overwrite`. Default behavior on existing CLAUDE.md is to skip and report.

**What if my codebase type isn't auto-detected?**
Defaults to `mixed` or `generic` with a warning. You can pass `--codebase-type <type>` to override.

**What if I run this in the wrong directory?**
The skill creates files relative to cwd. If you ran in the wrong dir, delete the new `CLAUDE.md` + `.ai-skills-memory/` and re-run in the right dir. Nothing destructive happened to your existing files.

**What's in `.committed/` and why?**
`.committed/` is opt-in versioned memory: team-confirmed conventions, ADRs, eval baselines, security incident records. Allowlist-validated by `pre-tool-use-committed-write.py` hook — only files matching `committed-allowlist.txt` patterns are accepted.

**Why is `.ai-skills-memory/` gitignored by default?**
Most of it is session-local state that doesn't belong in version control. The `.committed/` subdir is the explicit exception — a curated subset of memory the team chooses to share.

## Examples

### First-time setup on a Python FastAPI project
```bash
cd /path/to/my-fastapi-project
/ai-skills-init
```
Auto-detects `python-fastapi`. Creates CLAUDE.md scaffold, AGENTS.md, `.ai-skills-memory/` tree. Appends `.gitignore`.

### Existing CLAUDE.md but missing memory tree
```bash
/ai-skills-init
```
Reports "skipped: CLAUDE.md (exists)" and proceeds to create just the memory tree. Idempotent.

### Force-refresh CLAUDE.md (rare)
```bash
/ai-skills-init --overwrite
```
Overwrites CLAUDE.md. Use only when the existing file is empty or grossly stale; you'll lose any custom content.

### Specify codebase type explicitly
```bash
/ai-skills-init --codebase-type java-spring
```
Skip auto-detection. Use when auto-detection picks `mixed` but you want one specific scaffold.

## Related

- [`/memory-init`](feature-design.md) — memory tree only (sub-step of `/ai-skills-init`)
- [`/plugin-doctor`](feature-design.md) — verify plugin install + new repo setup
- [Memory](../concepts/memory.md) — what gets created and why
- [Getting Started](../getting-started.md) — full tutorial including this step
