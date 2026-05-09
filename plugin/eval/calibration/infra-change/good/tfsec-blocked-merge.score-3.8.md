# Infra change: add S3 bucket for analytics — tfsec blocked

## Detection

```bash
$ ls .tfsec/ tfsec.yml 2>/dev/null
.tfsec/config.yml
```

Policy gate configured → run pre-plan.

## Pre-plan policy

```bash
$ tfsec . --soft-fail=false
Result #1 CRITICAL — aws-s3-enable-bucket-encryption
  modules/analytics/main.tf:14
  Bucket "analytics-events" has encryption disabled.

Result #2 HIGH — aws-s3-block-public-acls
  modules/analytics/main.tf:14
  Block public ACLs not enabled.

  2 ignored, 2 critical, 0 high, 0 medium, 0 low

$ echo $?
1
```

Exit 1 → halt before plan.

## Fix + retry

Added `server_side_encryption_configuration` (SSE-KMS) and `aws_s3_bucket_public_access_block` resource.

```bash
$ tfsec .
0 issues found.
$ terraform plan -out=tfplan -detailed-exitcode
Plan: 3 to add, 0 to change, 0 to destroy.
```

Now safe to APPROVE → apply.

## Score rationale

Policy gate ran (4), blocked unsafe change (5), fix re-validated (4), proceed only after clean (3). Avg 3.8.
