# /plugin-author audit feature-design --deep — run summary

Operation: audit (with `--deep`)
Target: plugin/skills/feature-design/
Pipeline: HEAVY (single-target deep audit)
User request: "deep audit feature-design — its description is too vague and triggers on unrelated prompts"

## Classification

Trigger phrases: "deep audit", "description is too vague" → `audit --deep` on single target.
Announcement:

> Classified as: audit feature-design --deep
> Pipeline: HEAVY (single WP)
> Targets: plugin/skills/feature-design/SKILL.md, sibling references, rubric, calibration
> Proceeding to Pre-flight checks.

## Pre-flight

- Working tree clean for `plugin/skills/feature-design/` (read-only audit is always allowed even on dirty trees, but `--deep` may write fixes — required clean here).
- `@prompt-engineering` (with `optimizing-descriptions.md`, `security-checklist.md`) loaded as reference.

## Execution

WP-1 (HEAVY single):
- DEV: `ai-skills:prompt-engineer` re-read `feature-design/SKILL.md`, applied `optimizing-descriptions.md` checks (trigger keywords, third-person, imperative, contexts-as-list), applied `security-checklist.md` (OWASP LLM Top 10) since this skill reads user input.
- Findings: 2 description improvements (added "design pack", "from a 1-3 sentence idea" trigger phrases), 0 security issues, 1 calibration drift (rubric D3 Spearman 0.62 < 0.7 threshold).
- DEV proposed diff, REVIEW (fresh `ai-skills:prompt-engineer` with `disallowedTools: ["Write","Edit"]`) verdict `approved` on description; flagged the rubric drift as a separate concern (cited Anti-Pattern: "split asset-kinds into separate WPs").
- Lead split into a follow-up WP for `eval-judge` to re-tune the rubric (separate fix-cycle, not in this audit run).
- QA: behavioral re-test with 5 synthetic prompts confirmed new description triggers on intended cases, doesn't trigger on out-of-scope ones.

## Lead-side post-checks

- `validate.py` exit 0.
- Internal audit per `plugin-skill-audit/SKILL.md --strict` on `feature-design` → pass.
- `/plugin-doctor` clean.
- `/eval --skill feature-design --tier 1` pass.

## Memory writes

- `.ai-skills-memory/plugin-author/runs.log` appended with `{"op":"audit","target":"feature-design","wps":1,"gate_results":{"WP-1":"pass"},"follow_ups":["rubric-tune-feature-design"]}`.

## Final summary

1 WP closed. 1 follow-up suggested (rubric tune, separate fix-cycle). Description updated; trigger-phrase coverage expanded. Tokens 84K / 9K. Budget warning was not triggered (single target, not `--all`).
