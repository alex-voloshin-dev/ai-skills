# Hook Intents

This file captures the operational intent of the current Claude hook scripts and their visible Codex equivalents.

| Claude hook script | Intent | Codex equivalent |
|---|---|---|
| `block-dangerous-commands.py` | Stop obviously risky shell actions before execution | hard rules in `AGENTS.md`, explicit approval flow, and visible command scrutiny |
| `block-secrets-in-code.py` | Prevent secret leakage during edits | security rules in `AGENTS.md`, asset validation, and `security-scan` |
| `block-sensitive-files.py` | Prevent casual reads of credentials and secret material | read only what is needed and keep sensitive-path boundaries explicit |
| `log-actions.py` | Create an audit trail of tool activity | concise commentary updates and explicit verification summaries |

## Content Guardrails

| Claude rule | Intent | Codex equivalent |
|---|---|---|
| `humanize-content.md` | Enforce humanizer pass on all public-facing text | `humanize-content` rule in `.codex/rules/` plus `humanizer` skill in `.agents/skills/` |

## Codex Rule

If a hook intent is safety-critical, express it in `AGENTS.md`, skills, rules, or validation checklists.
Do not assume a hidden hook runtime exists.
