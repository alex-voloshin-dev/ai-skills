# `AGENTS.md` Template: Go Service

```md
# [Service Name] Guidelines

## Stack

- Go [version]
- Framework: [Gin / Echo / net/http]
- Build tool: `go`

## Hard Rules

- keep handlers thin
- propagate context correctly
- wrap errors with actionable context
- keep package boundaries simple

## Structure

- `cmd/` — entrypoints
- `internal/` — non-exported application packages
- `pkg/` — reusable packages if needed
- `*_test.go` — tests

## Commands

- Build: `[go build ./...]`
- Test: `[go test ./...]`
- Run: `[go run ./cmd/[service]]`

## Quality

- avoid global mutable state
- define interfaces at the consumer side
- document configuration and environment variables
```
