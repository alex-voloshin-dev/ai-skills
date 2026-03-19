# CLAUDE.md

## Project Overview

This is a Terraform infrastructure-as-code project. [DESCRIBE YOUR INFRASTRUCTURE HERE].

**Architecture**: See [ARCHITECTURE.md](./ARCHITECTURE.md) for system design, component relationships, data flows, and deployment topology.

## Setup Commands

```bash
# Initialize Terraform
terraform init

# Validate configuration
terraform validate

# Plan changes
terraform plan -out=tfplan

# Apply changes
terraform apply tfplan

# Format code
terraform fmt -recursive

# Run linter
tflint --recursive
```

## Code Style and Conventions

- Terraform 1.5+ with HCL syntax
- Use modules for reusable infrastructure components
- Use `snake_case` for all resource names and variables
- Use descriptive resource names: `aws_s3_bucket.app_data` not `aws_s3_bucket.bucket1`
- Pin provider versions in `versions.tf`
- Use variables with type constraints and descriptions
- Use locals for computed values to reduce repetition
- Tag all resources with: `project`, `environment`, `managed_by = "terraform"`

## Project Structure

```
├── main.tf              # Root module resources
├── variables.tf         # Input variable declarations
├── outputs.tf           # Output value declarations
├── versions.tf          # Provider and Terraform version constraints
├── terraform.tfvars     # Variable values (DO NOT COMMIT SECRETS)
├── backend.tf           # Remote state configuration
├── modules/             # Reusable modules
│   ├── networking/
│   ├── compute/
│   ├── storage/
│   └── monitoring/
└── environments/        # Environment-specific configs
    ├── dev/
    ├── staging/
    └── production/
```

## Testing Instructions

- Always run `terraform validate` before committing
- Always run `terraform plan` and review output before applying
- Use `terraform fmt -check` in CI to enforce formatting
- Test modules independently with minimal tfvars
- Never apply directly to production without plan review

## Context Engineering

<!-- Remove this section if the project has no AI/LLM features -->

- **Context stack policy**: [Token budget allocation per layer, cacheable prefix design]
- **Memory approach**: [Memory types used, storage backend, conflict resolution]
- **RAG pipeline**: [Embedding model, vector store, reranking, chunking strategy]
- **Tool result handling**: [Normalization and untrusted wrapping policy]
- **Multi-tenant isolation**: [Retrieval-time tenant filtering approach]
- **Production checklists**: Use `context-engineering` skill → `production-checklists.md` before AI feature launch

## AI Tooling Notes

- **Ignored paths**: [paths blocked by `.codeiumignore` or `.cursorignore` that AI tools cannot read/write]
- **State files**: Remote state only — never let AI tools read or modify `.tfstate` files locally

## Security Considerations

- NEVER commit `.tfvars` files with secrets — use environment variables or secret managers
- State files contain sensitive data — always use encrypted remote backend
- Enable encryption at rest and in transit for all storage resources
- Use least-privilege IAM policies
- Enable logging and monitoring for all resources

## PR Instructions

- Title format: `[module/env] Brief description`
- Always include `terraform plan` output in PR description
