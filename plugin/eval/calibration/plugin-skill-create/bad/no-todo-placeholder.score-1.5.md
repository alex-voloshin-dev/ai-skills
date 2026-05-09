# Plugin Skill Create Output — `cache-warmup` (audit guard missing)

> Invocation: `/plugin-skill-create cache-warmup --type workflow --invocable`

## Generated SKILL.md Frontmatter (excerpt)

```yaml
---
name: cache-warmup
description: Warms application caches on startup. Use when bootstrapping production workloads.
context: fork
argument-hint: "[--cache <name>]"
---
```

## What Went Wrong

The description has no `TODO —` placeholder marker. The scaffolder generated a description that *looks* finished — it has a what-clause and a use-when-clause and reads grammatically — so the user is likely to leave it as-is.

This breaks the audit-guard contract documented in the `/plugin-skill-create` skill body itself:

> "The `TODO —` token is a hard guard: `plugin-skill-audit` fails (CRITICAL severity) on any skill description that still contains `TODO`. This forces the scaffolded description to be edited before merge. Removing the literal `TODO` from your description is the gate that flips the audit from failing to passing."

When the placeholder is missing:

1. `/plugin-skill-audit cache-warmup` will report PASS on the spec check (the description meets length and naming rules)
2. The user has no forcing function to revisit and refine the description
3. The description was never tailored to the actual purpose — "Warms application caches on startup" is generic boilerplate that the scaffolder guessed from the skill name
4. The skill ships with weak trigger keywords; agents pattern-matching against it will under-trigger or trigger on wrong contexts

## Impact

`cache-warmup` will land in production with a description that:
- Was never reviewed by a human as a description (only as the skill name)
- Has no project-specific trigger phrases ("warm Redis after deploy", "preload cache on container start", etc.)
- Cannot be distinguished by `/plugin-skill-audit` from a properly-curated description

This is the audit-guard-bypass anti-pattern listed in the rubric for `plugin-skill-create`:

> "Generated description omits the literal `TODO —` token (audit guard bypass — placeholder would pass `/plugin-skill-audit` unedited)"

## Severity

HIGH. The scaffolder must be patched to always seed the literal `TODO —` prefix in the description. The companion `plugin-skill-audit` MUST then enforce that marker as CRITICAL fail. Both halves of the contract are required for the guard to function.

Recovery: rewrite the `cache-warmup` description manually before merge; patch the scaffolder; add a regression test asserting `description.startswith("TODO —")` for every freshly-scaffolded skill.
