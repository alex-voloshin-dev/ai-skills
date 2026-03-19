# Windsurf Asset Validation Checklist

## Structure

- [ ] required directories exist
- [ ] each skill has a `SKILL.md`
- [ ] hooks and shared support resources point to existing files

## Content Rules

- [ ] English only
- [ ] no secrets or credentials
- [ ] no installer-specific commands
- [ ] no application-specific commands copied from another repository

## Cross-References

- [ ] skill mentions resolve
- [ ] role references resolve
- [ ] hook script paths resolve
- [ ] workflow references resolve

## Runtime Readiness

- [ ] paths assume Windsurf runtime layout under `.windsurf/`
- [ ] hook configs use `.windsurf/hooks/scripts/...`
- [ ] no Claude-only settings or launch assumptions remain

## Naming

- [ ] agent files use `kebab-case.md`
- [ ] skill folders use `kebab-case/`
- [ ] workflow files use `kebab-case.md`

## Outcome

- [ ] ready for parity review
- [ ] parity-impacting changes reflected in `../../../review/parity-matrix.md`
