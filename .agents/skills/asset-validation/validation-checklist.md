# Codex Asset Validation Checklist

## Structure

- [ ] required directories exist
- [ ] each skill has a `SKILL.md`
- [ ] required role overlays exist for every referenced `codex-roles` value

## Content Rules

- [ ] English only
- [ ] no secrets or credentials
- [ ] no installer-specific commands
- [ ] no application-specific commands copied from another repository

## Cross-References

- [ ] skill mentions resolve
- [ ] role references resolve
- [ ] hook script paths resolve
- [ ] operation and template references resolve

## Runtime Readiness

- [ ] paths assume the Codex runtime layout under `.agents/skills/` and `.codex/`
- [ ] operation docs stay aligned with current hook and settings intent

## Naming

- [ ] role files use `kebab-case.md`
- [ ] skill folders use `kebab-case/`
- [ ] template files use the current Codex naming convention

## Outcome

- [ ] ready for parity review
- [ ] parity-impacting changes reflected in `../../../review/parity-matrix.md`
