# operation-router.md — /plugin-author classifier and dispatch table

This document is the routing brain of `/plugin-author`. The Lead reads it during the Classify step. Trigger phrases match against the user's natural-language input (case-insensitive, word-boundary aware). On match, the listed operation is selected and its required flags pre-filled.

## Trigger-phrase → operation table

| User phrasing (substring or close paraphrase) | Operation | Auto-flags |
|---|---|---|
| "new skill", "create a skill", "scaffold", "add a workflow", "start a new agent", "add a hook", "register a rule", "spin up a rubric" | `create` | infer `--type` from noun (skill / agent / rule / hook / rubric) |
| "audit", "lint", "check this skill", "review the skill", "validate frontmatter", "spec compliance" | `audit` | none (`--deep` opt-in) |
| "deep audit", "full audit", "review prompt quality", "is the description triggering", "rubric coverage", "calibration drift" | `audit` | `--deep` |
| "fix the feedback report", "address findings", "fix-feedback", presence of `--from <path>` | `fix-feedback` | `--from <path>` (required) |
| "improve", "tune", "polish", "this isn't triggering", "rubric is fuzzy", "description is weak", "rephrase trigger keywords" | `improve` | infer `--scope` from object |
| "refactor", "split", "extract references", "shrink this SKILL.md", "progressive disclosure", "too long" | `refactor` | none |
| "migrate", "update to current spec", "rebaseline", "modernize", "upgrade to agentskills v…", "bring to current conventions" | `migrate` | none |

If two operations match, pick the broader and pass the narrower as a flag:

- "audit and fix" → `audit --fix`
- "fix the findings and rewrite descriptions" → `fix-feedback` (the report itself drives the rewrites; `improve`-style WPs are emitted per finding)
- "refactor this skill and update spec" → `refactor` first, then suggest a follow-up `migrate` if needed

## Auto-flag inference

| Cue in input | Flag |
|---|---|
| `--from <path>` literal | `--from <path>` (forces `fix-feedback`) |
| "all skills", "every skill", "the whole plugin" | `--all` |
| "ci", "strict", "fail on warn" | `--strict` |
| "fix safely", "auto-fix", "apply safe fixes" | `--fix` |
| "remember this", "save the pattern", "user-global" | `--learnings` |
| Asset noun: skill / agent / rule / hook / rubric / schema | `--type <noun>` (`create` only) |
| Sub-target noun: description / body / rubric / calibration | `--scope <noun>` (`improve` only) |

## Disambiguation rules

1. Never silently pick when two unrelated operations match. Examples:
   - "create a skill that audits other skills" → ambiguous (`create` of a skill named `*-audit` vs `audit` operation). Ask: "Are you scaffolding a new skill, or auditing an existing one?"
   - "fix this skill's rubric and write a feedback report" → ambiguous (`improve` rubric vs producing a `/feedback` report, which is not this skill's job). Clarify scope; if user wants `/feedback`, dispatch to that skill instead.
2. Ask exactly ONE clarifying question, then proceed. Do not chain clarifications.
3. If the input contains both `--from <path>` AND another operation phrase, `--from` wins — operation is `fix-feedback`, and the other phrase is treated as a constraint on which findings to address.
4. Empty input (`/plugin-author` with no args) → ask once: "create, audit, fix-feedback, improve, refactor, or migrate? You can also pass `--from <report>` to start a fix-cycle." Single round-trip.

## Anti-routing (when NOT to take the request)

If any of the following match, refuse and point at the correct workflow:

| Input cue | Correct destination |
|---|---|
| "fix the application bug", "the API returns 500" | `/bugfix` |
| "implement the PRD", "build feature X" | `/develop` or `/feature-design` |
| "audit dependencies for CVEs" | `/security-scan` or `/security-audit` |
| "produce a feedback report", "scan recent sessions" | `/feedback` (this skill consumes the output of `/feedback`, it does not produce it) |
| "run the plugin doctor", "check plugin health" | `/plugin-doctor` directly |
| "update Codex / Windsurf mirror" | parity-matrix workflow (out of plugin scope) |

Refusal message template:

> `/plugin-author` covers authoring and maintenance of plugin assets only. Your request looks like `<short label>` — try `<correct command>`. If you wanted plugin-asset work that mentions `<X>`, rephrase as: `<example phrasing>`.

## Pipeline-shape decision after classification

| Operation + flags | Pipeline shape |
|---|---|
| `audit` (no `--deep`) | SIMPLE (inline read of `plugin-skill-audit/SKILL.md`, run checks, print report) |
| `audit --fix` (no `--deep`) | SIMPLE + write applied fixes per safe-fix table |
| `audit --deep` (single target) | HEAVY — 1 WP, DEV = `prompt-engineer` + optional `eval-judge` |
| `audit --all --deep` | HEAVY — N WPs, wave-sized, opt-in budget warning |
| `create` (trivial scaffold, no interview wanted) | SIMPLE (inline read of `plugin-skill-create/SKILL.md`) |
| `create` (default — with interview) | HEAVY — scaffold + interview + DEV pass + eval-judge rubric stub |
| `fix-feedback` | HEAVY — 1 WP per finding, grouped per `feedback-parser.md` |
| `improve` | HEAVY — 1 WP per affected asset |
| `refactor` | HEAVY — 2–4 WPs, equivalence gate on rubric eval |
| `migrate` | HEAVY — 1 WP per migrated skill, sequential to avoid spec-drift races |

## Output of the Classify step

After classification, the Lead announces:

```text
Classified as: <op> [flags...]
Pipeline: <SIMPLE | HEAVY (Path B preferred)>
Targets: <list of asset paths or names>
WPs (pre-wave): <count>
Proceeding to <Pre-flight checks | clarifying question>.
```

This announcement is informational, not a gate — the orchestrator continues immediately unless the user interrupts (Esc / "stop and revise"), per the `/develop` no-approval pattern.

## Edge cases and overrides

- **`--strict` on every op**: warnings become failures at every gate (Lead-side and subagent-side). Use in CI.
- **`--from` with both `.md` and `.json`**: prefer `.json`. If `--md` is explicitly passed, use `.md` and emit `provenance: md-fallback` on every WP.
- **`audit` against a hidden (absorbed) skill** (e.g., `plugin-skill-create`, `plugin-skill-audit`): allowed — these are still plugin assets and still subject to spec checks. They simply are not user-invocable anymore.
- **`create` against a name that collides with an absorbed skill**: refuse — these are reserved.
- **No matching trigger phrase**: ask the clarifying question; do not default silently.
