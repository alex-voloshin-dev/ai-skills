# Rollback Procedure

Step-by-step rollback instructions for production deployments. Execute immediately when post-deployment verification fails.

## Decision: When to Rollback

Rollback immediately if ANY of these conditions are met:

| Condition | Threshold | Action |
|---|---|---|
| Error rate spike | > 2x pre-deploy baseline | Immediate rollback |
| Latency degradation | P95 > 2x SLO target | Immediate rollback |
| Health check failure | Any pod CrashLoopBackOff | Immediate rollback |
| Data corruption | Any data integrity issue | Immediate rollback + incident |
| Critical user journey broken | Core flow non-functional | Immediate rollback |

## Rollback Steps

### 1. Application Rollback

**Kubernetes (kubectl):**
```bash
# Undo the last deployment
kubectl rollout undo deployment/<name> -n production

# Verify rollback
kubectl rollout status deployment/<name> -n production
```

**Helm:**
```bash
# List release history
helm history <release> -n production

# Rollback to previous revision
helm rollback <release> <previous-revision> -n production

# Verify
helm status <release> -n production
```

**Docker Compose:**
```bash
# Redeploy with previous image tag
docker compose -f docker-compose.production.yml up -d
```

### 2. Database Migration Rollback (if applicable)

Only if the deployment included database migrations:

**Flyway:**
```bash
flyway undo -url=<db-url>
```

**Alembic (Python):**
```bash
alembic downgrade -1
```

**EF Core (.NET):**
```bash
dotnet ef database update <previous-migration> --project src/Api
```

**Rails:**
```bash
rails db:rollback STEP=1
```

**⚠️ WARNING**: Database rollbacks may cause data loss if new columns were populated. Assess data impact before rolling back migrations.

### 3. Post-Rollback Verification

After rollback completes:

- [ ] All pods healthy and running
- [ ] Health endpoint returns 200
- [ ] Error rate returned to pre-deploy baseline
- [ ] Latency returned to normal
- [ ] Core user journeys functional
- [ ] No data corruption detected
- [ ] Logs clean (no new errors)

### 4. Communication

After successful rollback:

1. **Notify team**: Post in incident channel with rollback details
2. **Create incident ticket**: Document what happened, when, and impact
3. **Root cause analysis**: Investigate why the deployment failed
4. **Fix forward**: Address the root cause before re-deploying

## Rollback Communication Template

```
## Production Rollback — [timestamp]

**What**: Rolled back [service] from v[new] to v[old]
**Why**: [error rate spike / latency / health check failure / etc.]
**Impact**: [duration of degraded service, affected users/features]
**Current status**: [stable / monitoring]
**Next steps**: [investigation plan, timeline for re-deploy]
**Incident ticket**: [link]
```

## Prevention

After every rollback, evaluate:

- Was staging testing sufficient?
- Were the right metrics monitored?
- Could the issue have been caught by canary deployment?
- Are rollback procedures documented and practiced?
- Should deployment strategy change (rolling → canary)?
