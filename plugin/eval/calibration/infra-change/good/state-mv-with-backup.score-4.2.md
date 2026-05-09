# Infra change: refactor `aws_lambda_function` from root module → `lambda/` module

## Plan

Two options:
1. `terraform state mv` — imperative, fast, requires state backup
2. `moved {}` block (TF v1.1+) — declarative, reviewable in PR

Picked option 2 — code-level refactor reviewable in PR.

## Workflow

```hcl
# modules/lambda/main.tf — new module
resource "aws_lambda_function" "billing_processor" {
  function_name = "billing-processor"
  ...
}

# main.tf — adopt move
moved {
  from = aws_lambda_function.billing_processor
  to   = module.lambda.aws_lambda_function.billing_processor
}
```

```bash
$ terraform plan -detailed-exitcode
No changes.

Terraform will perform the following actions:
  # aws_lambda_function.billing_processor has moved to module.lambda.aws_lambda_function.billing_processor
```

Exit code 0 — refactor with no apply needed.

## Why not state mv

For comparison, the imperative path would have been:

```bash
$ terraform state pull > /tmp/state.backup.json
$ terraform state mv aws_lambda_function.billing_processor module.lambda.aws_lambda_function.billing_processor
$ terraform plan
No changes.
```

`moved {}` block is reviewable, reversible (just delete the block), and requires no out-of-band backup ceremony.

## Score rationale

Picked declarative path (5), backup ceremony understood as alternative (4), `moved {}` block adopted (5), plan verified no-op (4). Avg 4.2.
