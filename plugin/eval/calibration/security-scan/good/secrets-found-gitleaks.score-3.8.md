# Security scan: payments-service — gitleaks finding

## Hardcoded credential scan (Step 3)

```bash
$ gitleaks detect --source . --redact -v
Finding:     AKIA****************
Match:       AKIA****************
RuleID:      aws-access-token
Entropy:     3.987
File:        config/aws-staging.yml
Line:        14
Commit:      9f3a2b1c (3 weeks ago, by alex.v)

1 leak found.
```

The credential was committed 3 weeks ago in a config file. Since git history retains the value even after deletion, just removing the line in HEAD is **insufficient**.

## Remediation steps

1. **Rotate immediately**: revoke the IAM access key in AWS Console; cut a new one; update the staging deployment's vault.
2. **Verify rotation**: `aws iam get-access-key-last-used --access-key-id AKIA****` should show no recent usage of the old key.
3. **Scrub history** if the repo is private and small: `git filter-repo --path config/aws-staging.yml --invert-paths` (or BFG). For public repos, assume the credential is compromised — only rotation matters; history scrub is for hygiene.
4. **Move to vault**: `config/aws-staging.yml` should reference a vault (AWS Secrets Manager, SOPS+age, sealed-secrets, etc.), not contain plaintext.
5. **Add pre-commit hook**: `.pre-commit-config.yaml` should run gitleaks on every commit so this doesn't recur.

## Step 2: Dependency audit (passed, summary)

Ran `osv-scanner --lockfile=poetry.lock`. 0 KEV-listed CVEs; 1 high-EPSS CVE in transitive `requests` (track for next release).

## Score rationale

Gitleaks ran (4), finding correctly classified as critical (4), full remediation chain explained including history-scrub caveat (4), pre-commit follow-up suggested (3). Avg 3.8.
