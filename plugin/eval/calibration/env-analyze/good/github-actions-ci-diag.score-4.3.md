# Environment Diagnostic — GitHub Actions CI workflow

> Scope: ci-workflow:test | Auto-fix: disabled

## Summary

Test workflow (`.github/workflows/test.yml`) completed 12/12 jobs successfully. 3 warnings identified: slow Node.js cache, deprecated action version, disk usage trend. No blocking issues.

## Workflow Status

| Job | Status | Duration | Cache Hit | Conclusion |
|---|---|---|---|---|
| lint | passed | 1m 23s | yes | success |
| unit-tests | passed | 3m 47s | yes | success |
| integration-tests | passed | 8m 12s | partial (50%) | success |
| type-check | passed | 2m 15s | no (cold start) | success |
| coverage | passed | 1m 34s | yes | success |
| docker-build | passed | 12m 44s | partial (image cache) | success |

Total run time: 28m 55s (acceptable)

## Log Warnings (parsed)

1. **Node.js cache miss on `type-check` job**
   ```
   Warning: Cache entry not found for Node dependencies
   Re-installed dependencies (takes ~90s)
   Caching new dependencies for next run
   ```
   Indicates `node_modules` cache key mismatched (likely `package-lock.json` changed)

2. **Deprecated action in workflow**
   ```
   Warning: actions/setup-node@v2 is deprecated, use v4 (current: v4.0.1 recommended)
   ```
   Action still works but security patches lag

3. **Disk usage trending high**
   ```
   Disk usage: 89% of 14GB (after docker-build job)
   Trend: +3% per run (last 5 runs)
   ```
   If trend continues, workspace cleanup needed within ~5 runs

## Resource Usage

- CPU: 100% (runner maxed during docker-build, expected)
- Memory: 7.2GB / 8GB (peak during docker-build)
- Disk: 12.6GB / 14GB (docker images + node_modules)
- Network: 45MB down (dependencies), 60MB up (logs)

## Identified Anomalies

| Anomaly | Severity | Evidence | Class |
|---|---|---|---|
| Node cache miss on type-check | LOW | One job re-installed node_modules (90s overhead) | Cache drift |
| Deprecated action version | LOW | Setup-node@v2 → v4 available; security risk low | Deprecation |
| High disk usage trend | MEDIUM | 89% today, trending +3%/run; workspace fills in ~5-6 runs | Capacity |

## Root Causes

1. **Node cache miss:** `package-lock.json` was updated in a recent commit. Cache key includes lock file hash, so mismatch triggered cache miss. Next run will cache the new lock.

2. **Deprecated action:** Workflow uses `actions/setup-node@v2`. v4 is available. v2 still receives patches but slower cadence.

3. **Disk usage trend:** Docker images accumulate (`docker system prune` not called between runs). After ~6 runs, disk cleanup needed.

## Recommended Actions (manual)

1. **Update action version:**
   ```bash
   sed -i 's/actions\/setup-node@v2/actions\/setup-node@v4/' .github/workflows/test.yml
   git commit -am "chore(ci): upgrade setup-node to v4"
   ```
   Reversibility: high — prior action still available.

2. **Add explicit disk cleanup to workflow:**
   ```yaml
   - name: Cleanup Docker images
     run: docker system prune -af --volumes
   ```
   Add before docker-build job. Saves ~2-3GB per run.

3. **Monitor disk trend:**
   - Check disk usage on next 2 runs
   - If still trending up despite cleanup, investigate docker image layering

## Workflow Metrics (last 10 runs)

- Success rate: 100%
- Avg duration: 28.2 min (stable)
- Disk usage trend: +3% per run (as noted)

## Out-of-Scope

- Runner machine upgrade (would require org-level settings)
- GitHub Actions parallelism limit (6 concurrent jobs max for our org)

## Memory Write

Baseline saved to `.ai-skills-memory/env-reports/ci-test-<run-id>/`.
