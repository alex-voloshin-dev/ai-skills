# Infra change: tweak prod RDS instance class

## Plan

Need to change `aws_db_instance.primary` from `db.r6g.xlarge` → `db.r6g.2xlarge`. Other resources in the module changed too (irrelevant), so used `-target` to scope:

```bash
$ terraform plan -out=tfplan -target=aws_db_instance.primary
Plan: 0 to add, 1 to change, 0 to destroy.

$ terraform apply tfplan
aws_db_instance.primary: Modifying... [id=db-primary]
aws_db_instance.primary: Still modifying... [10s elapsed]
aws_db_instance.primary: Modification complete after 8m22s
```

Done.

---

**What's wrong with this output**:

1. **`-target` in production is an anti-pattern** (skill explicitly says so). It silently breaks the dependency graph: any other resources that should have re-planned in light of related changes (e.g., security-group rules, parameter groups, monitoring alarms tied to instance class) are now stale. The next normal `terraform apply` will surface those drifts as if they appeared from nowhere.
2. **No state backup**. The skill's State Operations section requires backup for state-touching ops; while this isn't `state mv`, modifying the primary DB still warrants a snapshot first.
3. **No APPROVE gate** for a HIGH-risk production change. The skill mandates explicit user APPROVE for destructive or production-touching operations. RDS instance modification with 8min downtime qualifies.
4. **No rollback plan**. If the new instance class triggers a regression, recovery is "modify back" — but `-target` made the original plan opaque. The plan should have shown the FULL diff (including all changes) so reviewers could spot side-effects.

Result: a plan that worked on its narrow scope and now leaves the rest of the module in inconsistent state.
