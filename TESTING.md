# Testing

This repository has no application code. The two delivery formats (`plugin/` for Claude Code, `.codex/` + `.windsurf/` + `.agents/` for Codex/Windsurf) are validated through targeted scripts plus manual review.

## Plugin validation (Claude Code)

The plugin ships its own structural validator:

```bash
python3 plugin/dev/validate.py
# Expected: 23 pass / 0 warn / 0 fail
```

It checks JSON syntax, Python parsing, manifest required fields + userConfig shape, structural counts (agents=26, skills=53, rules=12, hooks=18, rubrics=45, calibration samples=270, etc.), agent/skill frontmatter, hook lib imports, hooks.json command resolution, calibration sample counts, eval runners, and g1g2 attack-surface fixtures.

The plugin also ships two eval runners:

```bash
# Tier 1 — fast linters (no API key required)
python3 plugin/eval/runner.py --tier 1

# Tier 2 — Haiku judge calibration smoke (~$0.05, requires ANTHROPIC_API_KEY)
python3 plugin/eval/runner.py --tier 2

# G1/G2 attack-surface — structural check that untrusted-content envelope wraps prompt-injection payloads
python3 plugin/eval/g1g2/runner.py --structural
```

## Codex + Windsurf validation

Quality for these packages is maintained through manual review and the parity matrix.

### What to Check

**Markdown assets:**
- YAML frontmatter is syntactically valid
- File size stays under 12,000 characters for rules and skills
- Internal cross-references resolve (relative paths, `@skill-name` mentions)
- No project-specific paths or assumptions leak into shared assets
- Content is in English

**Hook scripts (Windsurf only — Codex has no native hooks):**
- Python scripts run without syntax errors: `python3 -c "import ast; ast.parse(open('<script>').read())"`
- Exit code 2 blocks correctly, exit code 0 allows correctly
- Pattern lists cover intended cases without false positives

**Parity** (see [PARITY.md](PARITY.md) for full model and validation commands):
- Every role exists in `.codex/roles/` AND `.windsurf/rules/roles/`
- Every skill exists in `.agents/skills/` AND `.windsurf/skills/` (shared corpus)
- Every guardrail rule exists in `.codex/rules/` AND `.windsurf/rules/`
- `review/parity-matrix.md` reflects the current state

**Installers:**
- `install.sh` and `install.ps1` sync `.agents/`, `.codex/`, `.windsurf/` (Claude Code is no longer installed via these scripts as of v0.2.0 — use `claude --plugin-dir ./plugin`)
- Stale file removal does not delete unrelated user files

### How to Validate Hook Scripts

```bash
# Syntax check all Windsurf hook scripts
for f in .windsurf/hooks/scripts/*.py; do
  python3 -c "import ast; ast.parse(open('$f').read())" && echo "OK: $f"
done

# Syntax check all plugin hook scripts (18 + _lib.py)
for f in plugin/hooks/scripts/*.py; do
  python3 -c "import ast; ast.parse(open('$f').read())" && echo "OK: $f"
done

# Test a hook with sample input (works for plugin and Windsurf scripts alike)
echo '{"tool_name":"Bash","tool_input":{"command":"rm -rf /"}}' | \
  python3 plugin/hooks/scripts/block-dangerous-commands.py
# Expected: exit code 2, stdout contains block reason
```

### Asset Validation Skill

The `@asset-validation` skill (Codex/Windsurf packages) provides a structured checklist for reviewing AI asset changes. Use it when editing or adding skills, rules, or roles. For plugin assets, run `python3 plugin/dev/validate.py` instead.
