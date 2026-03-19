# Google Cloud Platform Reference

Platform-specific patterns for **GCP**. Load this module when the project's `AGENTS.md` or infrastructure files indicate GCP, Google Cloud, GKE, Cloud SQL, Cloud Build, or related services.

## 1. Core Platform

<gcp_core>
- **Project structure**: Separate GCP projects per environment (dev, staging, prod). Use folder hierarchy for org-level policies
- **IAM**: Use custom roles or predefined roles (never primitive roles in production). Prefer Workload Identity over service account keys
- **Networking**: VPC with private subnets. Private Google Access enabled. Cloud NAT for egress. Firewall rules: default deny, explicit allow
- **Secrets**: Google Secret Manager for all secrets. Reference via `data "google_secret_manager_secret_version"` in Terraform
- **Labels**: Every resource labeled: `env`, `team`, `managed_by = "terraform"`, `project`
</gcp_core>

### Terraform State Backend

```hcl
terraform {
  backend "gcs" {
    bucket = "<project>-terraform-state"
    prefix = "env/<environment>"
  }
}
```

Separate state per environment. Encrypt at rest. Enable state locking.

## 2. Container Orchestration — GKE

<gke>
- **Cluster**: Private cluster with authorized networks. Release channel: `REGULAR` or `STABLE`
- **Node pools**: Separate pools per workload type (general, cpu-intensive, memory-intensive). Auto-scaling enabled
- **Workload Identity**: Always enable. Map Kubernetes service accounts to GCP service accounts. Never mount service account keys
- **Network policies**: Enable and enforce. Default deny ingress, explicit allow per service
- **Pod Security**: Use Pod Security Standards (restricted). No privileged containers in production
- **Upgrades**: Enable auto-upgrade on node pools. Maintenance windows during off-peak
</gke>

### GKE Diagnostic Commands

```bash
# Cluster info
gcloud container clusters list --format="table(name,location,status,currentMasterVersion,currentNodeCount)"

# Authenticate to cluster
gcloud container clusters get-credentials <cluster> --region <region> --project <project>

# Node pool status
gcloud container node-pools list --cluster <cluster> --region <region>
```

## 3. Managed Database — Cloud SQL

<cloud_sql>
- **High availability**: Enable HA for production (`availability_type = "REGIONAL"`)
- **Backups**: Automated daily backups with point-in-time recovery enabled. Test restores regularly
- **Connectivity**: Private IP only via VPC peering. Never expose via public IP in production
- **Maintenance**: Set maintenance window during off-peak. Enable auto-minor-version upgrades
- **Flags**: Configure `max_connections`, `shared_buffers`, `work_mem` based on instance size
- **Users**: Application-specific DB users with minimum required privileges. Never use `postgres` superuser in app
- **Connection management**: Cloud SQL Auth Proxy. Max connections per instance tier
</cloud_sql>

### Cloud SQL Diagnostic Commands

```bash
# List instances
gcloud sql instances list --format="table(name,state,databaseVersion,settings.tier,settings.availabilityType)"

# Instance details
gcloud sql instances describe <instance> --format="yaml(state,settings.backupConfiguration,settings.databaseFlags,settings.ipConfiguration)"

# Connect via proxy
cloud-sql-proxy <project>:<region>:<instance> --port 5432
```

### Cloud SQL Reliability

- **HA**: `availability_type = "REGIONAL"` for production. Auto failover
- **Backups**: Automated daily + PITR. Test restore quarterly
- **Monitoring**: CPU utilization, connections, replication lag, disk usage
- **Maintenance**: Lowest traffic windows. Monitor post-maintenance regression

## 4. CI/CD — Cloud Build

<cloud_build>
- **Config**: `cloudbuild.yaml` with explicit steps. Pin builder image versions
- **Triggers**: Branch-based (push to main → deploy staging, tag → deploy prod). PR triggers for validation
- **Substitutions**: Use `_ENVIRONMENT`, `_PROJECT_ID` — never hardcode environment-specific values
- **Artifacts**: Push images to Artifact Registry with SHA-based tags. Tag with git SHA + semver
- **Secrets**: Use `secretManager` in Cloud Build steps. Never pass secrets as build args
</cloud_build>

## 5. Observability — Cloud Monitoring & Logging

<monitoring>
- **Cloud Monitoring**: Custom dashboards per service. Metrics: latency (p50/p95/p99), error rate, traffic, saturation (CPU, memory, disk, connections)
- **Four Golden Signals**: Latency, traffic, errors, saturation — dashboard every service with these
- **Custom metrics**: Use OpenTelemetry SDK to emit business metrics (orders/sec, payments processed)
- **Log-based metrics**: Create metrics from Cloud Logging for events not captured by standard instrumentation
- **Uptime checks**: HTTP(S) checks for all public endpoints. Alert on consecutive failures (≥2)
</monitoring>

<alerting>
- **Multi-window burn rate alerts**: Fast burn (5 min window, 10x rate) for pages. Slow burn (6h window, 2x rate) for tickets
- **Alert routing**: P1/P2 → PagerDuty (page on-call). P3/P4 → Slack channel (ticket)
- **Alert quality**: Every alert must have: summary, impact description, runbook link, severity. No alerts without runbooks
- **Alert fatigue prevention**: Review alert frequency monthly. Tune or remove alerts that fire > 5x/week without action
</alerting>

<logging>
- **Structured logging**: JSON format with `severity`, `message`, `timestamp`, `trace_id`, `span_id`, `labels`
- **Cloud Logging**: Route logs to appropriate sinks. Archive to GCS for long-term. BigQuery for analysis
- **Log levels**: ERROR (action needed), WARNING (degradation), INFO (state changes), DEBUG (diagnostic, disabled in prod)
- **Correlation**: Trace ID propagated across all services. Link logs → traces → metrics
</logging>

### Observability Diagnostic Commands

```bash
# List dashboards
gcloud monitoring dashboards list --format="table(displayName,name)"

# Read logs (last 1h, errors only)
gcloud logging read 'severity>=ERROR AND resource.type="k8s_container" AND resource.labels.namespace_name="<namespace>"' --limit=50 --format=json --freshness=1h

# List alerting policies
gcloud alpha monitoring policies list --format="table(displayName,enabled,conditions.displayName)"

# Metrics query
gcloud monitoring time-series list --filter='metric.type="custom.googleapis.com/<metric>"' --interval-start-time=$(date -u -d '-1 hour' +%Y-%m-%dT%H:%M:%SZ)
```

## 6. CLI Reference — gcloud

### Authentication and Context

```bash
# Current project
gcloud config get-value project

# Active account
gcloud auth list --filter=status:ACTIVE --format="value(account)"

# Switch project
gcloud config set project <project-id>

# Application default credentials
gcloud auth application-default login
```

### Common Operations

```bash
# Compute instances
gcloud compute instances list --format="table(name,zone,status,machineType)"

# IAM bindings
gcloud projects get-iam-policy <project> --flatten="bindings[].members" --format="table(bindings.role,bindings.members)"

# Secret Manager
gcloud secrets list
gcloud secrets versions access latest --secret=<secret-name>

# Cloud Run (if applicable)
gcloud run services list --format="table(name,region,status,url)"
```

### Data Extraction (for ML/analytics)

```bash
# Cloud SQL query via proxy
gcloud sql connect <instance> --user=<user> --database=<db>

# BigQuery
bq query --use_legacy_sql=false 'SELECT ...'

# GCS
gsutil ls gs://<bucket>/
gsutil cp gs://<bucket>/<path> ./local/

# Cloud Monitoring metrics
gcloud monitoring time-series list --filter='metric.type="<metric>"'
```

## 7. Security and Compliance

- **Audit logging**: Enable Cloud Audit Logs for all GCP services. Export to Cloud Logging / BigQuery
- **Network security**: VPC Service Controls for sensitive projects. Private endpoints everywhere
- **Image scanning**: Artifact Analysis for container images. Block deployment of images with critical CVEs
- **RBAC**: Kubernetes RBAC aligned with GCP IAM. Review permissions quarterly
- **Encryption**: All data encrypted at rest (Google-managed or CMEK) and in transit (TLS)
- **Quota management**: Track GCP quotas. Request increases proactively

## 8. Production Analysis Workflow

When diagnosing production issues on GCP, follow this sequence:

1. **Verify context**: `gcloud config get-value project` + `kubectl config current-context`
2. **Cluster health**: `gcloud container clusters list` + `kubectl get nodes -o wide`
3. **Pod status**: `kubectl get pods -n <ns> -o wide` + check for non-Running pods
4. **Pod details**: `kubectl describe pod` + `kubectl logs --tail=200`
5. **Resources**: `kubectl top pods` + `kubectl get hpa`
6. **Cloud SQL**: `gcloud sql instances list` + connection/CPU metrics
7. **Networking**: `kubectl get ingress,svc,endpoints`
8. **Events**: `kubectl get events --field-selector type!=Normal`
9. **Monitoring**: Check Cloud Monitoring dashboards for SLI degradation

### Common GCP Production Issues

- **Cloud SQL connection exhaustion**: Too many connections from pods, connection leak in app, pool size misconfigured, proxy not configured
- **GKE deployment stuck**: Image pull error (wrong tag, Artifact Registry auth), failed readiness probe, PDB blocking rollout, insufficient quota
- **Network unreachable**: NetworkPolicy blocking traffic, VPC firewall rule, Cloud NAT exhaustion
