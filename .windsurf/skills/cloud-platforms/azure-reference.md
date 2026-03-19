# Microsoft Azure Reference

Platform-specific patterns for **Azure**. Load this module when the project's AGENTS.md declares Azure, AKS, Azure SQL, Azure DevOps, or related services.

## 1. Core Platform

<azure_core>
- **Subscription structure**: Separate subscriptions per environment (dev, staging, prod). Use Management Groups for org-level policies
- **IAM**: Azure RBAC with custom or built-in roles. Prefer Managed Identity over service principals with secrets. Entra ID (Azure AD) for authentication
- **Networking**: VNet with private subnets. NSGs for network filtering. Azure Private Link for PaaS services. Azure Firewall or NVA for egress control
- **Secrets**: Azure Key Vault for all secrets. Reference via `azurerm_key_vault_secret` data source in Terraform or Key Vault CSI driver in K8s
- **Tags**: Every resource tagged: `env`, `team`, `managed_by = "terraform"`, `project`, `cost_center`
</azure_core>

### Terraform State Backend

```hcl
terraform {
  backend "azurerm" {
    resource_group_name  = "<rg>-terraform-state"
    storage_account_name = "<sa>terraformstate"
    container_name       = "tfstate"
    key                  = "<environment>.terraform.tfstate"
  }
}
```

Separate state per environment. Enable blob versioning and soft delete. Use Azure RBAC for access control.

## 2. Container Orchestration — AKS

<aks>
- **Cluster**: Private cluster with authorized IP ranges. Use system and user node pools. Automatic channel upgrades (`stable` or `rapid`)
- **Node pools**: Separate pools per workload type. Auto-scaling enabled. Use Spot VMs for non-critical workloads
- **Workload Identity**: Enable via Azure Workload Identity (federated credentials). Map K8s service accounts to Managed Identities. Never mount service principal secrets
- **Network policies**: Azure Network Policy or Calico. Default deny ingress, explicit allow per service
- **Pod Security**: Pod Security Standards (restricted). Azure Policy for Kubernetes for compliance enforcement
- **Upgrades**: Enable auto-upgrade channel. Plan upgrade windows. Use PDBs during upgrades
</aks>

### AKS Diagnostic Commands

```bash
# List clusters
az aks list -o table

# Get credentials
az aks get-credentials --resource-group <rg> --name <cluster> --overwrite-existing

# Node pool status
az aks nodepool list --resource-group <rg> --cluster-name <cluster> -o table

# Cluster health
az aks show --resource-group <rg> --name <cluster> --query "{status:provisioningState,k8sVersion:kubernetesVersion,nodeCount:agentPoolProfiles[0].count}"
```

## 3. Managed Database — Azure SQL / Azure Database for PostgreSQL

<azure_sql>
- **High availability**: Zone-redundant deployment for production. Auto-failover groups for geo-redundancy
- **Backups**: Automated backups with PITR (7–35 day retention). Geo-redundant backup storage for production
- **Connectivity**: Private Endpoint only. Never expose via public endpoint in production. VNet service endpoints as fallback
- **Maintenance**: Configure maintenance window during off-peak. Enable auto-minor-version upgrades
- **Firewall**: Deny all by default. Allow only via Private Endpoint or specific VNet rules
- **Users**: Application-specific DB users with minimum required privileges. Use Entra ID authentication where possible
- **Connection management**: Connection pooling via PgBouncer (built-in for Flexible Server) or application-level pooling
</azure_sql>

### Azure SQL Diagnostic Commands

```bash
# List servers
az postgres flexible-server list -o table
# or for Azure SQL
az sql server list -o table

# Show server details
az postgres flexible-server show --resource-group <rg> --name <server>

# List databases
az postgres flexible-server db list --resource-group <rg> --server-name <server> -o table

# Connection test
az postgres flexible-server connect --name <server> --admin-user <user> --admin-password <pass> --database <db>
```

### Azure SQL Reliability

- **HA**: Zone-redundant for production. Auto-failover groups for cross-region
- **Backups**: Automated with PITR. Test restore quarterly. Geo-redundant for DR
- **Monitoring**: CPU, DTU/vCore utilization, connections, deadlocks, storage usage
- **Maintenance**: Configure preferred window. Monitor post-maintenance regression

## 4. CI/CD — Azure DevOps / GitHub Actions

<azure_cicd>
- **Azure DevOps Pipelines**: YAML pipelines in repo (`azure-pipelines.yml`). Use stages, jobs, templates for reusability
- **GitHub Actions with Azure**: Use `azure/login@v1` with OIDC (federated credentials). No static service principal secrets
- **Container Registry**: Azure Container Registry (ACR). Geo-replication for multi-region. Content trust for image signing
- **Artifacts**: Push images to ACR with SHA-based tags. Tag with git SHA + semver. Use ACR Tasks for in-cloud builds
- **Secrets**: Use Azure Key Vault linked to pipeline. Never pass secrets as plain environment variables
- **Environments**: Use deployment environments with approval gates and checks
</azure_cicd>

## 5. Observability — Azure Monitor

<azure_monitoring>
- **Azure Monitor**: Centralized monitoring. Metrics Explorer for resource metrics. Log Analytics workspace for logs and queries (KQL)
- **Four Golden Signals**: Latency, traffic, errors, saturation — create workbooks per service
- **Application Insights**: Enable for application-level telemetry. Auto-instrumentation where possible. Custom metrics via OpenTelemetry SDK
- **Container Insights**: Enable for AKS. Pod-level metrics, logs, and live diagnostics
- **Custom metrics**: OpenTelemetry SDK → Application Insights or Azure Monitor custom metrics
</azure_monitoring>

<azure_alerting>
- **Alert rules**: Metric alerts for resource-level, log alerts (KQL) for complex conditions, Activity Log alerts for control plane
- **Action groups**: Route to PagerDuty, Slack, email, Azure Functions. Severity-based routing
- **Alert quality**: Every alert must have: description, severity, runbook link, action group. Suppress duplicate alerts
- **Smart detection**: Enable Application Insights smart detection for anomaly-based alerting
</azure_alerting>

<azure_logging>
- **Structured logging**: JSON format. Use `ILogger` (.NET), structured logging libraries for other stacks
- **Log Analytics**: Centralized workspace. KQL for querying. Diagnostic settings on all resources to route logs
- **Log levels**: Error, Warning, Information, Debug. Disable Debug in production
- **Correlation**: Use Application Insights correlation (operation ID, parent ID). Distributed tracing via W3C Trace Context
</azure_logging>

### Observability Diagnostic Commands

```bash
# List Log Analytics workspaces
az monitor log-analytics workspace list -o table

# Query logs (KQL)
az monitor log-analytics query --workspace <workspace-id> --analytics-query "ContainerLog | where LogEntry contains 'error' | top 50 by TimeGenerated"

# List alert rules
az monitor metrics alert list --resource-group <rg> -o table

# Resource metrics
az monitor metrics list --resource <resource-id> --metric "CpuPercentage" --interval PT1H
```

## 6. CLI Reference — az

### Authentication and Context

```bash
# Login
az login

# Current subscription
az account show --query "{name:name, id:id, tenantId:tenantId}" -o table

# Switch subscription
az account set --subscription <subscription-id>

# List subscriptions
az account list -o table
```

### Common Operations

```bash
# Resource groups
az group list -o table

# AKS clusters
az aks list -o table

# Key Vault secrets
az keyvault list -o table
az keyvault secret list --vault-name <vault> -o table

# Container Registry
az acr list -o table
az acr repository list --name <registry> -o table
```

### Data Extraction (for ML/analytics)

```bash
# Azure SQL query
az sql db show --resource-group <rg> --server <server> --name <db>

# Azure Storage (Blob)
az storage blob list --container-name <container> --account-name <account> -o table
az storage blob download --container-name <container> --name <blob> --file ./local --account-name <account>

# Azure Monitor metrics
az monitor metrics list --resource <resource-id> --metric <metric-name>
```

## 7. Security and Compliance

- **Audit logging**: Azure Activity Log + Diagnostic Settings on all resources → Log Analytics workspace
- **Network security**: Azure Private Link for all PaaS. NSGs + Azure Firewall. DDoS Protection for public endpoints
- **Image scanning**: Microsoft Defender for Containers. Vulnerability assessment in ACR
- **RBAC**: Azure RBAC + Kubernetes RBAC aligned. Entra ID integration for AKS. Conditional Access policies
- **Encryption**: All data encrypted at rest (platform-managed or CMK via Key Vault) and in transit (TLS)
- **Compliance**: Azure Policy for guardrails. Microsoft Defender for Cloud for security posture management

## 8. Production Analysis Workflow

When diagnosing production issues on Azure, follow this sequence:

1. **Verify context**: `az account show` + `kubectl config current-context`
2. **Cluster health**: `az aks show` + `kubectl get nodes -o wide`
3. **Pod status**: `kubectl get pods -n <ns> -o wide` + check for non-Running pods
4. **Pod details**: `kubectl describe pod` + `kubectl logs --tail=200`
5. **Resources**: `kubectl top pods` + `kubectl get hpa`
6. **Azure SQL/PostgreSQL**: `az postgres flexible-server show` + connection/CPU metrics
7. **Networking**: `kubectl get ingress,svc,endpoints` + NSG rules
8. **Events**: `kubectl get events --field-selector type!=Normal`
9. **Monitoring**: Check Azure Monitor / Application Insights for SLI degradation

### Common Azure Production Issues

- **Azure SQL connection exhaustion**: Too many connections, PgBouncer misconfigured, connection leak, Managed Identity token refresh issues
- **AKS deployment stuck**: ACR image pull error (RBAC, network), failed readiness probe, PDB blocking rollout, quota exceeded
- **Network unreachable**: NSG blocking traffic, Private Endpoint DNS resolution, Azure Firewall rule, VNet peering issue
