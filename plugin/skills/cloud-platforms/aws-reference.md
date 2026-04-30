# Amazon Web Services Reference

Platform-specific patterns for **AWS**. Load this module when the project's CLAUDE.md declares AWS, EKS, RDS, CodePipeline, or related services.

## 1. Core Platform

<aws_core>
- **Account structure**: Separate AWS accounts per environment (dev, staging, prod) via AWS Organizations. Use SCPs for org-level guardrails
- **IAM**: IAM roles with least privilege. Prefer IRSA (IAM Roles for Service Accounts) for EKS workloads. Never use long-lived access keys in production
- **Networking**: VPC with public/private subnets across AZs. Security Groups for instance-level filtering. NACLs for subnet-level. NAT Gateway for private subnet egress
- **Secrets**: AWS Secrets Manager or SSM Parameter Store (SecureString). Reference via `aws_secretsmanager_secret_version` data source in Terraform or External Secrets Operator in K8s
- **Tags**: Every resource tagged: `Environment`, `Team`, `ManagedBy = "terraform"`, `Project`, `CostCenter`
</aws_core>

### Terraform State Backend

```hcl
terraform {
  backend "s3" {
    bucket         = "<project>-terraform-state"
    key            = "<environment>/terraform.tfstate"
    region         = "<region>"
    dynamodb_table = "<project>-terraform-locks"
    encrypt        = true
  }
}
```

Separate state per environment. Enable S3 versioning and encryption. DynamoDB for state locking.

## 2. Container Orchestration — EKS

<eks>
- **Cluster**: Private API endpoint with authorized CIDR blocks. Managed node groups preferred. Use EKS add-ons for core components (CoreDNS, kube-proxy, VPC CNI)
- **Node groups**: Separate managed node groups per workload type. Cluster Autoscaler or Karpenter for auto-scaling. Use Spot Instances for non-critical workloads
- **IRSA**: Enable IAM Roles for Service Accounts. Map K8s service accounts to IAM roles via OIDC provider. Never mount AWS credentials as secrets
- **Network policies**: Use Calico or VPC CNI network policies. Default deny ingress, explicit allow per service
- **Pod Security**: Pod Security Standards (restricted). Use OPA/Gatekeeper or Kyverno for policy enforcement
- **Upgrades**: Plan version upgrades carefully. Update add-ons, then control plane, then node groups. Use PDBs during node group updates
</eks>

### EKS Diagnostic Commands

```bash
# List clusters
aws eks list-clusters --output table

# Cluster details
aws eks describe-cluster --name <cluster> --query "cluster.{status:status,version:version,endpoint:endpoint}"

# Node groups
aws eks list-nodegroups --cluster-name <cluster> --output table
aws eks describe-nodegroup --cluster-name <cluster> --nodegroup-name <ng> --query "nodegroup.{status:status,desiredSize:scalingConfig.desiredSize}"

# Update kubeconfig
aws eks update-kubeconfig --name <cluster> --region <region>
```

## 3. Managed Database — RDS / Aurora

<rds>
- **High availability**: Multi-AZ deployment for production. Aurora with read replicas for high-throughput workloads
- **Backups**: Automated snapshots with PITR (1–35 day retention). Cross-region snapshot copy for DR
- **Connectivity**: Deploy in private subnets. Security Group allows only application subnets. Never expose via public endpoint in production
- **Maintenance**: Configure maintenance window during off-peak. Enable auto-minor-version upgrades
- **Parameter groups**: Configure `max_connections`, `shared_buffers`, `work_mem` via custom parameter groups
- **Users**: Application-specific DB users with minimum required privileges. Use IAM DB authentication where possible
- **Connection management**: RDS Proxy for connection pooling. Handles failover transparently
</rds>

### RDS Diagnostic Commands

```bash
# List instances
aws rds describe-db-instances --query "DBInstances[].{id:DBInstanceIdentifier,status:DBInstanceStatus,engine:Engine,class:DBInstanceClass,az:AvailabilityZone,multiAZ:MultiAZ}" --output table

# Instance details
aws rds describe-db-instances --db-instance-identifier <instance> --output yaml

# CloudWatch metrics (CPU)
aws cloudwatch get-metric-statistics --namespace AWS/RDS --metric-name CPUUtilization --dimensions Name=DBInstanceIdentifier,Value=<instance> --start-time $(date -u -d '-1 hour' +%Y-%m-%dT%H:%M:%S) --end-time $(date -u +%Y-%m-%dT%H:%M:%S) --period 300 --statistics Average

# Connection count
aws cloudwatch get-metric-statistics --namespace AWS/RDS --metric-name DatabaseConnections --dimensions Name=DBInstanceIdentifier,Value=<instance> --start-time $(date -u -d '-1 hour' +%Y-%m-%dT%H:%M:%S) --end-time $(date -u +%Y-%m-%dT%H:%M:%S) --period 300 --statistics Maximum
```

### RDS Reliability

- **HA**: Multi-AZ for production. Aurora with failover priority for read replicas
- **Backups**: Automated snapshots + PITR. Test restore quarterly. Cross-region for DR
- **Monitoring**: CPU, connections, read/write IOPS, replica lag, storage usage
- **Maintenance**: Off-peak windows. Monitor post-maintenance regression

## 4. CI/CD — CodePipeline / CodeBuild / GitHub Actions

<aws_cicd>
- **CodePipeline**: Source (CodeCommit/GitHub) → Build (CodeBuild) → Deploy (CodeDeploy/EKS). Use manual approval for production stage
- **CodeBuild**: `buildspec.yml` in repo. Pin runtime versions. Use cache for dependencies. ECR for container image storage
- **GitHub Actions with AWS**: Use `aws-actions/configure-aws-credentials@v4` with OIDC. Never store AWS access keys as GitHub secrets
- **Container Registry**: Amazon ECR. Enable image scanning on push. Lifecycle policies for cleanup. Cross-region replication for DR
- **Artifacts**: Push images to ECR with SHA-based tags. Tag with git SHA + semver. Immutable image tags in production
- **Secrets**: AWS Secrets Manager or SSM Parameter Store linked to CodeBuild. Never pass secrets as plaintext environment variables
</aws_cicd>

## 5. Observability — CloudWatch

<aws_monitoring>
- **CloudWatch Metrics**: Custom dashboards per service. Built-in metrics for all AWS resources. Custom metrics via CloudWatch agent or OpenTelemetry SDK
- **Four Golden Signals**: Latency, traffic, errors, saturation — CloudWatch dashboard per service
- **X-Ray**: Distributed tracing for service-to-service calls. Auto-instrumentation via X-Ray SDK or OpenTelemetry with X-Ray exporter
- **Container Insights**: Enable for EKS. Pod-level metrics, cluster-level metrics, log aggregation
- **Custom metrics**: OpenTelemetry SDK → CloudWatch via EMF (Embedded Metric Format) or X-Ray
</aws_monitoring>

<aws_alerting>
- **CloudWatch Alarms**: Metric alarms for resource-level, composite alarms for multi-signal, anomaly detection alarms for ML-based thresholds
- **SNS routing**: P1/P2 → PagerDuty/OpsGenie via SNS. P3/P4 → Slack/email via SNS. Use SNS filter policies for routing
- **Alert quality**: Every alarm must have: description, severity tag, runbook link, appropriate evaluation period. No alarms without runbooks
- **EventBridge**: Use for event-driven alerting (state changes, API calls, scheduled rules)
</aws_alerting>

<aws_logging>
- **Structured logging**: JSON format. Use language-specific structured logging libraries
- **CloudWatch Logs**: Log groups per service. Log Insights for querying. Subscription filters for streaming to S3/OpenSearch
- **Log levels**: ERROR, WARN, INFO, DEBUG. Disable DEBUG in production
- **Correlation**: X-Ray trace ID propagated across services. Link logs → traces → metrics via CloudWatch ServiceLens
</aws_logging>

### Observability Diagnostic Commands

```bash
# List CloudWatch dashboards
aws cloudwatch list-dashboards --output table

# Query logs (CloudWatch Logs Insights)
aws logs start-query --log-group-name <log-group> --start-time $(date -u -d '-1 hour' +%s) --end-time $(date -u +%s) --query-string 'fields @timestamp, @message | filter @message like /error/i | sort @timestamp desc | limit 50'

# List alarms
aws cloudwatch describe-alarms --state-value ALARM --output table

# Get metric statistics
aws cloudwatch get-metric-statistics --namespace <namespace> --metric-name <metric> --start-time <start> --end-time <end> --period 300 --statistics Average
```

## 6. CLI Reference — aws

### Authentication and Context

```bash
# Current identity
aws sts get-caller-identity

# Current region
aws configure get region

# Switch profile
export AWS_PROFILE=<profile>

# SSO login
aws sso login --profile <profile>
```

### Common Operations

```bash
# EC2 instances
aws ec2 describe-instances --query "Reservations[].Instances[].{id:InstanceId,type:InstanceType,state:State.Name,name:Tags[?Key=='Name']|[0].Value}" --output table

# IAM roles
aws iam list-roles --query "Roles[].{name:RoleName,arn:Arn}" --output table

# Secrets Manager
aws secretsmanager list-secrets --output table

# ECR repositories
aws ecr describe-repositories --output table
```

### Data Extraction (for ML/analytics)

```bash
# RDS connection (via bastion or SSM Session Manager)
aws ssm start-session --target <bastion-instance-id> --document-name AWS-StartPortForwardingSessionToRemoteHost --parameters '{"host":["<rds-endpoint>"],"portNumber":["5432"],"localPortNumber":["5432"]}'

# S3
aws s3 ls s3://<bucket>/
aws s3 cp s3://<bucket>/<path> ./local/

# Athena (serverless SQL)
aws athena start-query-execution --query-string "SELECT ..." --result-configuration OutputLocation=s3://<bucket>/results/

# CloudWatch metrics
aws cloudwatch get-metric-data --metric-data-queries file://query.json --start-time <start> --end-time <end>
```

## 7. Security and Compliance

- **Audit logging**: AWS CloudTrail enabled for all regions. S3 bucket with versioning for trail storage. CloudTrail Lake for querying
- **Network security**: VPC with private subnets. Security Groups (stateful) + NACLs (stateless). AWS WAF for public endpoints. AWS Shield for DDoS
- **Image scanning**: ECR image scanning on push. Amazon Inspector for runtime vulnerability assessment
- **RBAC**: IRSA for EKS workloads. IAM policies with least privilege. Permission boundaries for delegated admin. AWS SSO for human access
- **Encryption**: All data encrypted at rest (AWS-managed or CMK via KMS) and in transit (TLS). Enforce via S3 bucket policies, RDS encryption
- **Compliance**: AWS Config Rules for guardrails. AWS Security Hub for security posture. AWS Trusted Advisor for best practices

## 8. Production Analysis Workflow

When diagnosing production issues on AWS, follow this sequence:

1. **Verify context**: `aws sts get-caller-identity` + `kubectl config current-context`
2. **Cluster health**: `aws eks describe-cluster` + `kubectl get nodes -o wide`
3. **Pod status**: `kubectl get pods -n <ns> -o wide` + check for non-Running pods
4. **Pod details**: `kubectl describe pod` + `kubectl logs --tail=200`
5. **Resources**: `kubectl top pods` + `kubectl get hpa`
6. **RDS/Aurora**: `aws rds describe-db-instances` + CloudWatch CPU/connections metrics
7. **Networking**: `kubectl get ingress,svc,endpoints` + Security Group rules
8. **Events**: `kubectl get events --field-selector type!=Normal`
9. **Monitoring**: Check CloudWatch dashboards + X-Ray traces for SLI degradation

### Common AWS Production Issues

- **RDS connection exhaustion**: Too many connections, RDS Proxy misconfigured, connection leak, IRSA token refresh issues
- **EKS deployment stuck**: ECR image pull error (IRSA permissions, VPC endpoint), failed readiness probe, PDB blocking rollout, service quota exceeded
- **Network unreachable**: Security Group blocking traffic, VPC endpoint DNS resolution, NAT Gateway limit, NACLs blocking response traffic
