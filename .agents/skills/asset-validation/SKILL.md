---
name: asset-validation
description: Validate Codex AI assets for size limits, frontmatter correctness, cross-reference integrity, runtime readiness, and parity safety after structural changes.
user-invocable: false
---

# Asset Validation

Use this skill after modifying `.agents/skills/` or `.codex/` assets and before accepting a parity-impacting change.

## Validation Layers

### 1. Structure

Confirm the expected runtime layout exists:

- `.agents/skills/<name>/SKILL.md`
- `.codex/roles/*.md`
- `.codex/rules/*.md`
- `.codex/operations/*.md`
- `.codex/templates/*.md` and `.codex/checklists/*.md` when applicable

### 2. Frontmatter and Format

Check:

- `SKILL.md` contains at least `name` and `description`
- optional `codex-roles` values resolve to both role and overlay files
- `AGENTS.md` stays plain Markdown
- markdown assets stay within repository size guidance where required

### 3. Cross-References

Verify:

- skill references resolve to existing folders under `.agents/skills/`
- role references resolve to existing files under `.codex/roles/`
- overlay references resolve under `.codex/rules/role-overlays/`
- operation docs point to existing Codex files and not stale Claude runtime paths

### 4. Runtime Readiness

Confirm:

- assets assume the Codex runtime layout under `.agents/skills/` and `.codex/`
- Claude hook and settings behavior is translated into visible operation docs, not implied hidden automation
- no installer-specific or machine-specific commands remain

### 5. Naming

- role files use `kebab-case.md`
- overlay files use the same role id as the matching role file
- skill folders use `kebab-case/`
- template files use consistent Codex naming

## Report Format

Return:

- Summary
- Passed checks
- Findings
- Required follow-up

Use `validation-checklist.md` for the detailed checklist.
