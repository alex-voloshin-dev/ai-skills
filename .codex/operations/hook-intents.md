# Hook Intents

This file captures the operational intent of `.claude/hooks/scripts`.

| Claude hook script | Intent | Codex equivalent |
|---|---|---|
| `block-dangerous-commands.py` | Stop obviously risky shell actions | hard rules in `AGENTS.md` and explicit approval flow |
| `block-secrets-in-code.py` | Prevent secret leaks during edits | security rules in `AGENTS.md`, review checklists, and `security-scan` |
| `block-sensitive-files.py` | Avoid reading sensitive files casually | read only what is needed and follow repo security boundaries |
| `detect-tool-loops.py` | detect repeated failing tool usage | failure recovery rules in `.codex/rules/failure-recovery.md` |
| `log-actions.py` | create an audit trail of tool activity | explicit commentary updates and optional local verification scripts |
| `normalize-tool-results.py` | keep tool outputs clean before reuse | summarize tool output before turning it into prompts or assets |

## Content Guardrails

| Claude rule | Intent | Codex equivalent |
|---|---|---|
| `humanize-content.md` | Enforce humanizer pass on all public-facing text | `humanize-content` rule in `.codex/rules/` plus `humanizer` skill in `.agents/skills/` |

## Codex Rule

If a hook intent is safety-critical, express it in `AGENTS.md`, skills, or validation scripts.
Do not assume a hidden hook runtime exists.
