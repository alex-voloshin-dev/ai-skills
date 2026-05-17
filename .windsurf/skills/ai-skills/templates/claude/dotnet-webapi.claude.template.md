# AGENTS.md

## Project Overview

This is a .NET Web API application built with ASP.NET Core. [DESCRIBE YOUR PROJECT PURPOSE HERE].

**Architecture**: See [ARCHITECTURE.md](./ARCHITECTURE.md) for system design, component relationships, data flows, and deployment topology.

## Setup Commands

```bash
# Restore dependencies
dotnet restore

# Build the project
dotnet build

# Run the application
dotnet run --project src/Api

# Run tests
dotnet test

# Run a specific test project
dotnet test tests/Api.UnitTests

# Run with watch mode (hot reload)
dotnet watch run --project src/Api

# Apply EF Core migrations
dotnet ef database update --project src/Api
```

## Code Style and Conventions

- .NET 8+ with ASP.NET Core minimal APIs or controllers
- Follow Microsoft C# coding conventions (PascalCase for public members, camelCase for locals)
- Use nullable reference types (`<Nullable>enable</Nullable>`)
- Use records for DTOs and immutable data
- Use `IResult` return types for minimal APIs or `ActionResult<T>` for controllers
- Dependency injection via constructor — register in `Program.cs` or extension methods
- Use `FluentValidation` or Data Annotations for input validation
- Use `IOptions<T>` pattern for configuration binding
- Entity Framework Core for data access — never expose DbContext directly from controllers
- Use async/await throughout — all I/O operations must be async

## Project Structure

```
src/
├── Api/                    # Web API host
│   ├── Program.cs          # Application entry point and DI registration
│   ├── Endpoints/          # Minimal API endpoint groups (or Controllers/)
│   ├── Middleware/          # Custom middleware
│   ├── Filters/            # Action/exception filters
│   └── appsettings.json    # Configuration
├── Application/            # Business logic layer
│   ├── Services/           # Application services
│   ├── DTOs/               # Data transfer objects (records)
│   ├── Interfaces/         # Service contracts
│   ├── Validators/         # FluentValidation validators
│   └── Mappings/           # AutoMapper profiles or manual mapping
├── Domain/                 # Domain layer
│   ├── Entities/           # Domain entities
│   ├── ValueObjects/       # Value objects
│   ├── Enums/              # Domain enumerations
│   └── Exceptions/         # Domain exceptions
└── Infrastructure/         # Infrastructure layer
    ├── Data/               # EF Core DbContext and configurations
    ├── Repositories/       # Repository implementations
    ├── Migrations/         # EF Core migrations
    └── ExternalServices/   # Third-party API clients

tests/
├── Api.UnitTests/          # Unit tests for services and logic
├── Api.IntegrationTests/   # Integration tests with WebApplicationFactory
└── Api.ArchTests/          # Architecture tests (optional)
```

## Testing Instructions

- Unit tests: xUnit + Moq/NSubstitute for service layer
- Integration tests: `WebApplicationFactory<Program>` with Testcontainers for DB
- API tests: `HttpClient` from `WebApplicationFactory` for endpoint testing
- Architecture tests: NetArchTest for enforcing layer dependencies
- Run all tests before committing: `dotnet test`
- Naming: `MethodName_Scenario_ExpectedResult`

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
- **Dev server command**: `dotnet run --project src/Api` → `https://localhost:5001`
- **API docs**: [e.g., Swagger UI at `https://localhost:5001/swagger`]

## Security Considerations

- Never log sensitive data (passwords, tokens, PII)
- Use ASP.NET Core Identity or JWT Bearer authentication
- Validate all request inputs (FluentValidation or Data Annotations)
- Use parameterized queries (EF Core handles this by default)
- Store secrets in environment variables or Azure Key Vault / User Secrets — never in appsettings.json
- Enable CORS with specific origins only
- Use HTTPS redirection and HSTS in production

## PR Instructions

- Title format: `[component] Brief description`
- Include EF Core migration if DB schema changes
- Ensure backward compatibility for API changes
- Run `dotnet format` before committing
