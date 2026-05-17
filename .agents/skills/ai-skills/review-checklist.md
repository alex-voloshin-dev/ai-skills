# AI Asset Review Checklist

Use this checklist after creating or editing Codex-facing assets.

## Universal Checks

1. Instructions are direct and testable.
2. Critical rules are near the top.
3. Policy and reference material are separated.
4. The asset does not rely on unsupported Claude-specific primitives.
5. Cross-references resolve.
6. The asset is concise enough to justify its token cost.

## Codex Checks

1. `AGENTS.md` content contains repository or directory policy, not task-specific noise.
2. `SKILL.md` content is executable as a reusable workflow.
3. Templates are reusable and not overfit to one repo state.
4. Scripts are explicit, optional, and safe to run locally.
5. Codex-specific docs point to `.agents` and `.codex`, not `.claude` runtime paths.
6. Source-library sync scripts stage vendor assets instead of overwriting Codex runtime assets directly.

## Validation Checks

- File names are consistent and readable.
- English only.
- No secrets or environment-specific credentials.
- No broken links or missing companion files.
- Expected behavior is clear from one read-through.
