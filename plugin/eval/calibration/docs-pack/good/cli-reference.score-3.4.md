# CLI Reference — Deploy Tool

> Audience: operator | Template: api-reference (adapted for CLI)

## Overview

The Deploy CLI (`deploy`) manages application releases to staging and production. All commands require a valid CI/CD token in `$DEPLOY_TOKEN` environment variable.

Version: 1.4.2 (released 2026-04-10)

## Quickstart

```bash
# List available releases
deploy release list

# Deploy to staging
deploy release deploy staging --version 1.2.3

# Monitor deployment
deploy deployment status --id deploy_abc123
```

Tested 2026-04-18 against production.

## Commands

### `deploy release list`

List all available releases.

**Options:**
- `--limit` (default: 20) — max results to return
- `--status` (default: all) — filter by `ready`, `building`, `failed`

**Output:**
```
ID            VERSION  STATUS   CREATED_AT
rel_001       1.2.3    ready    2026-04-18T10:00:00Z
rel_002       1.2.2    ready    2026-04-17T15:30:00Z
```

### `deploy release deploy ENVIRONMENT --version VERSION`

Deploy a release to an environment.

**Arguments:**
- `ENVIRONMENT` — `staging` or `production` (required)
- `--version` — release version, e.g., `1.2.3` (required)

**Options:**
- `--dry-run` — print plan without executing
- `--wait` — block until deployment completes (timeout 30min)
- `--skip-smoke-tests` — skip post-deploy smoke tests (not recommended)

**Response:**
```json
{
  "id": "deploy_abc123",
  "status": "in-progress",
  "release_version": "1.2.3",
  "environment": "staging"
}
```

**Errors:**
- `version_not_found` — release doesn't exist or is still building
- `insufficient_capacity` — environment has no available slots
- `previous_deployment_in_progress` — wait for active deployment to finish

### `deploy deployment status DEPLOYMENT_ID`

Check deployment status.

**Response:**
```json
{
  "id": "deploy_abc123",
  "status": "succeeded",
  "release_version": "1.2.3",
  "started_at": "2026-04-18T10:00:00Z",
  "completed_at": "2026-04-18T10:15:32Z",
  "notes": "Smoke tests passed. 0 error logs."
}
```

**Statuses:** `pending`, `in-progress`, `succeeded`, `failed`, `rolled-back`

### `deploy rollback ENVIRONMENT --to-version VERSION`

Rollback environment to previous release.

**Arguments:**
- `ENVIRONMENT` — `staging` or `production`
- `--to-version` — version to rollback to

**Safety checks:**
- Production rollbacks require approval from on-call (slack notification sent; wait up to 5min)
- Staging rollbacks are immediate

## Environment Variables

- `DEPLOY_TOKEN` (required) — CI/CD token for authentication
- `DEPLOY_TIMEOUT` (optional, default 1800) — max seconds to wait for deployment

## Exit Codes

- `0` — success
- `1` — general error
- `2` — invalid arguments
- `3` — not authorized (token invalid or lacks permission)

## Examples

```bash
# Deploy v1.3.0 to staging and wait for completion
deploy release deploy staging --version 1.3.0 --wait

# Dry-run production deployment
deploy release deploy production --version 1.3.0 --dry-run

# Check specific deployment
deploy deployment status deploy_abc123

# Rollback staging to previous version
deploy rollback staging --to-version 1.2.3
```

## Troubleshooting

**"insufficient_capacity"**
- Staging/prod environment is at max parallel deployments
- Wait for active deployments to finish: `deploy deployment list --environment prod`

**"version_not_found"**
- Verify version exists: `deploy release list | grep 1.3.0`
- Wait for build to complete if release is recent (check CI status)

**Deployment times out**
- Increase `DEPLOY_TIMEOUT`: `DEPLOY_TIMEOUT=3600 deploy release deploy ...`
- Check environment health: `deploy environment health prod`

