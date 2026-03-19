# Asset Validation

Systematic validation of Cascade AI assets. Use after batch creation or modification and before accepting assets into the shared package baseline.

## When to Use

- After creating or modifying one or more Claude assets
- During a package-wide validation pass
- When investigating broken references or activation issues

## Validation Layers

### 1. File Size

Every hot-path Markdown asset should stay within Claude-friendly size limits.

### 2. Frontmatter

Check required fields:

- rule files use the frontmatter expected by the Windsurf runtime
- `SKILL.md` contains `name` and `description`
- `AGENTS.md` stays plain Markdown

### 3. Cross-References

Verify:

- `@skill-name` targets an existing folder in `skills/`
- agent references target an existing file in `agents/`
- hook script paths resolve under `hooks/scripts/`
- `settings.json` commands reference valid scripts

### 4. Runtime Readiness

Confirm:

- assets assume the `.windsurf/` runtime layout
- hook configs use `.windsurf/hooks/scripts/...`
- `settings.json` remains consistent with hook scripts
- no installer-specific commands remain

### 5. Naming

- agent files use `kebab-case.md`
- skill folders use `kebab-case/`
- template files use `*.claude.template.md`

## Report Format

Return:

- Summary
- Passed checks
- Findings
- Required follow-up

Use `validation-checklist.md` for the detailed manual checklist.