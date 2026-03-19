# Claude Asset Validation Checklist

## Structure

- [ ] required directories exist
- [ ] each skill has a `SKILL.md`
- [ ] settings and hook configs point to existing scripts

## Content Rules

- [ ] English only
- [ ] no secrets or credentials
- [ ] no installer-specific commands
- [ ] no application-specific commands copied from another repository

## Cross-References

- [ ] skill mentions resolve
- [ ] agent references resolve
- [ ] hook script paths resolve
- [ ] `settings.json` commands resolve

## Runtime Readiness

- [ ] paths assume Claude runtime layout under `.claude/`
- [ ] hook configs use `.claude/hooks/scripts/...`
- [ ] `settings.json` remains consistent with hook scripts

## Naming

- [ ] agent files use `kebab-case.md`
- [ ] skill folders use `kebab-case/`
- [ ] template files use `*.claude.template.md`

## Outcome

- [ ] ready for parity review
- [ ] parity-impacting changes reflected in `../../../review/parity-matrix.md`