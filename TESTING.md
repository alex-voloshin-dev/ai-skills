# Testing

This repository has no automated test suite. It contains only Markdown, JSON, Python hook scripts, and shell installers — not application code.

## Validation Approach

Quality is maintained through manual review and the parity matrix.

### What to Check

**Markdown assets:**
- YAML frontmatter is syntactically valid
- File size stays under 12,000 characters for rules and skills
- Internal cross-references resolve (relative paths, `@skill-name` mentions)
- No project-specific paths or assumptions leak into shared assets
- Content is in English

**Hook scripts:**
- Python scripts run without syntax errors: `python3 -c "import ast; ast.parse(open('<script>').read())"`
- Exit code 2 blocks correctly, exit code 0 allows correctly
- Pattern lists cover intended cases without false positives

**Parity:**
- Every role exists in `.claude/agents/`, `.codex/roles/`, `.windsurf/rules/roles/`
- Every skill exists in `.claude/skills/`, `.agents/skills/`, `.windsurf/skills/`
- Every guardrail rule exists in `.claude/rules/`, `.codex/rules/`, `.windsurf/rules/`
- `review/parity-matrix.md` reflects the current state

**Installers:**
- `install.sh` and `install.ps1` sync all four directories
- Hook path rewriting produces valid absolute paths
- Stale file removal does not delete unrelated user files

### How to Validate Hook Scripts

```bash
# Syntax check all hook scripts
for f in .claude/hooks/scripts/*.py; do
  python3 -c "import ast; ast.parse(open('$f').read())" && echo "OK: $f"
done

# Test a hook with sample input
echo '{"tool_name":"Bash","tool_input":{"command":"rm -rf /"}}' | \
  python3 .claude/hooks/scripts/block-dangerous-commands.py
# Expected: exit code 2, stdout contains block reason
```

### Asset Validation Skill

The `@asset-validation` skill provides a structured checklist for reviewing AI asset changes. Use it when editing or adding skills, rules, or roles.
