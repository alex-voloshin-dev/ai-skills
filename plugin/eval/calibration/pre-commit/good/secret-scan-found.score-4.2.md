# Pre-Commit — gitleaks blocked commit on hardcoded API key

## Step 0: framework detection

`.pre-commit-config.yaml` present. Routed there.

```yaml
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.21.2
    hooks:
      - id: gitleaks
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.4
    hooks:
      - id: ruff-check
        args: [--fix]
      - id: ruff-format
```

`pre-commit autoupdate --dry-run` showed all hooks current.

## Stage executed: `pre-commit`

```
$ git commit -m "feat(integrations): add Stripe webhook handler"
gitleaks................................................................Failed
- hook id: gitleaks
- exit code: 1

   Finding:     STRIPE_API_KEY = "<REDACTED-LIVE-KEY>"
   RuleID:      stripe-access-token
   Entropy:     5.2
   File:        app/integrations/stripe.py
   Line:        14
   Commit:      n/a (staged)

ruff-check..............................................................Skipped
ruff-format.............................................................Skipped
```

## Action: blocked, surfaced finding

A live-looking Stripe token was detected on staged content. Commit blocked. Skipping the gate via `--no-verify` would require explicit user APPROVE — not granted, not used.

The repo's `.gitleaks.toml` allowlist was checked — no matching entry; this is a real positive, not a known false positive. The actual key value is intentionally not reproduced here.

## Remediation steps presented to user

1. Remove the hardcoded key from `app/integrations/stripe.py:14`
2. Move it to env: `STRIPE_API_KEY = os.environ["STRIPE_API_KEY"]`
3. Add to `.env.example` (without the value)
4. Rotate the leaked key in Stripe dashboard immediately — the key already lives in the working tree on disk and may have been pushed in a draft branch. Treat as compromised even though commit was blocked.
5. Re-stage and re-run `git commit`

## Per-gate result

| Gate       | Status   | Notes                                 |
| ---------- | -------- | ------------------------------------- |
| gitleaks   | **fail** | live Stripe token (redacted)          |
| ruff-check | skipped  | downstream of gitleaks fail           |
| ruff-format| skipped  | downstream of gitleaks fail           |

## Verdict

**Not ready to commit.** Real secret found; rotation of the Stripe key is the priority before any further work. Will not propose a final commit message; commit must not happen with this content staged.
