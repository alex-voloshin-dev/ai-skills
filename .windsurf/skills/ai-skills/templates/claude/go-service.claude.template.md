# AGENTS.md

## Project Overview

This is a Go service application. [DESCRIBE YOUR PROJECT PURPOSE HERE].

**Architecture**: See [ARCHITECTURE.md](./ARCHITECTURE.md) for system design, component relationships, data flows, and deployment topology.

## Setup Commands

```bash
# Download dependencies
go mod download

# Build the application
go build -o bin/app ./cmd/api

# Run the application
go run ./cmd/api

# Run tests
go test ./...

# Run tests with coverage
go test -coverprofile=coverage.out ./... && go tool cover -func=coverage.out

# Run a specific test
go test -run TestFunctionName ./path/to/package

# Lint
golangci-lint run ./...

# Generate code (mocks, protobuf, etc.)
go generate ./...
```

## Code Style and Conventions

- Go 1.22+ with standard library preferred over third-party where practical
- Follow Effective Go and Go Code Review Comments guidelines
- Use `gofmt` / `goimports` for formatting (enforced by CI)
- Error handling: always check errors, wrap with `fmt.Errorf("context: %w", err)`
- Use `context.Context` as first parameter for functions that do I/O
- Prefer interfaces at the consumer side (accept interfaces, return structs)
- Use table-driven tests with `t.Run` subtests
- Use dependency injection via constructor functions — avoid global state
- Naming: short, descriptive names. Avoid stuttering (e.g., `user.User` not `user.UserStruct`)
- Package names: short, lowercase, singular (e.g., `handler`, `store`, `config`)

## Project Structure

```
cmd/
├── api/                    # Application entry point
│   └── main.go             # Wires dependencies, starts HTTP server
internal/                   # Private application code (not importable)
├── config/                 # Configuration loading (env, flags, files)
├── handler/                # HTTP handlers (or gRPC service implementations)
├── middleware/              # HTTP middleware (auth, logging, recovery)
├── service/                # Business logic layer
├── store/                  # Data access layer (repositories)
│   ├── postgres/           # PostgreSQL implementations
│   └── redis/              # Redis implementations
├── model/                  # Domain models and entities
├── dto/                    # Request/response types for API layer
└── pkg/                    # Shared internal utilities
    ├── httputil/            # HTTP helpers
    ├── validate/            # Input validation
    └── testutil/            # Test helpers and fixtures
pkg/                        # Public library code (if any)
migrations/                 # SQL migration files
api/                        # OpenAPI specs or protobuf definitions
deployments/                # Docker, Kubernetes, Helm files
```

## Testing Instructions

- Unit tests: Standard `testing` package + testify for assertions
- Integration tests: Build tag `//go:build integration` + Testcontainers
- HTTP tests: `httptest.NewServer` for handler testing
- Mocks: Use `mockery` or `gomock` for interface mocking
- Run all tests before committing: `go test ./...`
- Naming: `TestFunctionName_Scenario_ExpectedResult` with table-driven subtests
- Use `t.Parallel()` where safe for faster execution
- Use `t.Helper()` in test utility functions

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
- **Dev server command**: `go run ./cmd/api` → `http://localhost:8080`
- **API docs**: [e.g., Swagger at `http://localhost:8080/swagger/index.html` if using swaggo]

## Security Considerations

- Never log sensitive data (passwords, tokens, PII)
- Validate and sanitize all user input
- Use parameterized queries for SQL (database/sql placeholders or ORM)
- Store secrets in environment variables — never hardcode
- Use `crypto/rand` for random generation — never `math/rand` for security
- Set timeouts on HTTP clients and servers
- Use `net/http` `MaxBytesReader` to limit request body size

## PR Instructions

- Title format: `[package] Brief description`
- Run `go vet ./...` and `golangci-lint run` before submitting
- Include migration files if DB schema changes
- Ensure backward compatibility for API changes
