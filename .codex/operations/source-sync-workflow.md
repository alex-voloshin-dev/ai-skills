# Source Sync Workflow

Use this workflow when the Claude package changes and Codex plus Windsurf assets need to stay aligned.

1. compare affected assets between `../.claude/`, `../.agents/skills/`, `../.codex/`, and `../.windsurf/`
2. identify whether the change requires a Codex-native role, rule, operation, checklist, template, or skill update
3. identify whether the same change requires a Windsurf rule, workflow, hook, or skill-resource update
4. translate the intent into the correct runtime-native primitive for each package
5. update `../review/parity-matrix.md` if capability coverage changed
6. run a structural review for broken references and project-specific assumptions

## Rule

Do not treat Claude assets as runtime-ready Codex or Windsurf assets without first translating them into runtime-native primitives.
