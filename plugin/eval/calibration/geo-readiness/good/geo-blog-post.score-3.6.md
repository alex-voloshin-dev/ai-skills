# What is a feature flag, and when should you use one?

> Updated 2026-04-22 · 6 min read

**A feature flag is a runtime switch that lets you enable or disable code paths without redeploying.** Most teams use them for three purposes: gradually rolling out new features, killing broken features fast, and running experiments. The first use — gradual rollout — is by far the most common in 2026 production systems.

## How does a feature flag work?

**A feature flag wraps a block of code in a runtime check.** When the flag is on, the new code path runs; when off, the old path runs (or the feature is hidden). The check reads from a flag service (LaunchDarkly, Unleash, ConfigCat, or a homegrown table) on each request.

A typical implementation:

```python
if flags.is_enabled("new_checkout", user=current_user):
    return new_checkout_flow(request)
return old_checkout_flow(request)
```

The flag service evaluates rules — for example, "enable for 10% of users in the US" — and returns true or false. According to a 2024 LaunchDarkly survey, **78% of engineering teams using flags report fewer rollback incidents** compared to deploy-only release strategies.

## When should you reach for a feature flag?

**Use a feature flag when the code change carries non-zero rollback cost.** For trivial changes (typo fixes, cosmetic CSS), the deploy is the rollout. For anything touching business logic, payment flow, data writes, or external integrations, a flag pays for itself the first time you need to disable a broken feature in 30 seconds instead of 30 minutes.

| Situation | Use a flag? |
|---|---|
| Renaming a CSS class | No |
| Adding a new payment method | Yes (kill switch) |
| Refactoring an internal helper | No |
| Changing checkout flow | Yes (gradual rollout) |
| A/B testing copy | Yes (experimentation) |
| Adding a new endpoint | Sometimes (off-by-default) |

## What's the cost of using flags?

**Every flag adds a runtime branch and a cleanup obligation.** The runtime cost is negligible (microseconds per check). The cleanup cost is real: stale flags accumulate, code becomes a maze of `if`s, and removed flags can leak through to dead code.

A 2026 industry benchmark from the State of Feature Flags report indicates teams average **47 stale flags per service** — flags whose rollout completed but that were never removed. Best practice: every flag created has a removal owner and a target removal date.

## How do you avoid flag debt?

**Build a removal pipeline.** When a flag is created, file a follow-up issue with a target date. When the rollout reaches 100% and bakes for two weeks, the issue triggers a PR to remove the flag and its dead code path. Some teams automate this via flag-service annotations.

Specific practices that work:

- **Tag every flag with an expiry date in the flag service itself**
- **Run a monthly "flag debt" report** showing flags older than 60 days
- **Block new flag creation** by individual engineers when their open-flag count exceeds a threshold (e.g., 5)

## Frequently asked questions

**Should flags live in the database or in code?**
Flags should live in a flag service or a hot-reloadable config. Storing flag state in your application database means you can't toggle without a deploy — defeats the point.

**How often should flag values be evaluated?**
Per request for user-targeted flags. Per session start for session-scoped flags. Cache aggressively at the service-client level (1–5 second TTL is typical).

**Can flags replace canary deployments?**
Partially. Flags handle code-level rollout. Canary deployments handle infrastructure-level rollout (new container image, new region). The two complement each other.

**What happens if the flag service goes down?**
Configure your flag client with a default value per flag. When the service is unreachable, the client uses the default. Most modern flag SDKs cache the last-known state too.

## Key takeaways

- A feature flag is a runtime switch that decouples deploy from rollout
- Use one when the change has non-zero rollback cost
- Every flag needs an owner and a removal date
- Stale flags compound into technical debt
- Flag service downtime should default to a safe state per flag
