---
name: concise-pr
description: Terse, change-focused output style for /develop PR descriptions. Forces summary-first, bullet-listed changes, minimal narrative. Use when generating PRs from /develop or /create-pr workflows where reviewers need to scan quickly.
---

# Concise PR Output Style

Output discipline for PR descriptions: lead with the one-sentence summary, list changes as scannable bullets, omit narrative.

## Format

```
## Summary
<one sentence: what this PR does and why>

## Changes
- <file or area>: <one-line change>
- <file or area>: <one-line change>
- ...

## Type
<one of: feat | fix | refactor | chore | docs | test | perf | ci | breaking>

## Testing
<one bullet per test layer touched: unit / integration / e2e / manual>

## Risk
<low | medium | high — one sentence on what could break>

## Checklist
- [x] / [ ] items per project's PR template
```

## Hard rules

- **One-line bullets.** No multi-sentence change descriptions; split into separate bullets if needed.
- **No narrative paragraphs.** Reviewers want diffs + risk; paragraphs go in commit body or design docs.
- **No emoji decoration.** Plain Markdown headers.
- **No "I'm excited to" / "I'm humbled to"** openings — `humanize-content` rule applies.
- **Risk is mandatory** — never omit; "low" with one sentence is acceptable.
- **Type is mandatory** — picks the conventional-commit prefix per `git-conventions` rule.

## When NOT to use

- Long-form release notes (use `release` skill default style with sections)
- Architecture decision records (use `design-pack` output style)
- User-facing changelog entries (those go in `CHANGELOG.md` per project format)

## Used by

`/create-pr` (PR description generation), `/develop` REVIEW-LOG.md → `/create-pr` ingestion path.
