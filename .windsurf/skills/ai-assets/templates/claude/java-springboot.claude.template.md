# AGENTS.md

## Project Overview

This is a Java Spring Boot application. [DESCRIBE YOUR PROJECT PURPOSE HERE].

**Architecture**: See [ARCHITECTURE.md](./ARCHITECTURE.md) for system design, component relationships, data flows, and deployment topology.

## Setup Commands

```bash
# Build the project
./mvnw clean install

# Run the application
./mvnw spring-boot:run

# Run tests
./mvnw test

# Run a specific test class
./mvnw test -Dtest=ClassName

# Run integration tests
./mvnw verify -P integration-tests
```

## Code Style and Conventions

- Java 17+ with Spring Boot 3.x
- Follow standard Java naming conventions (camelCase for methods/variables, PascalCase for classes)
- Use constructor injection over field injection
- Use `@Service`, `@Repository`, `@Controller` stereotypes appropriately
- DTOs for API input/output, entities for persistence — never expose entities directly
- Use `Optional` instead of null returns
- Use records for immutable data carriers (DTOs, value objects)
- Validate inputs with Jakarta Bean Validation (`@Valid`, `@NotNull`, etc.)

## Project Structure

```
src/
├── main/java/com/example/app/
│   ├── config/          # Spring configuration classes
│   ├── controller/      # REST controllers
│   ├── service/         # Business logic
│   ├── repository/      # Data access layer
│   ├── model/           # Entity classes
│   ├── dto/             # Data transfer objects
│   ├── exception/       # Custom exceptions and handlers
│   └── util/            # Utility classes
├── main/resources/
│   ├── application.yml  # Main configuration
│   └── db/migration/    # Flyway/Liquibase migrations
└── test/java/           # Test classes mirror main structure
```

## Testing Instructions

- Unit tests: JUnit 5 + Mockito for service layer
- Integration tests: `@SpringBootTest` with Testcontainers for DB
- API tests: `@WebMvcTest` with MockMvc for controllers
- Run all tests before committing: `./mvnw test`
- Naming: `ClassName_methodName_expectedBehavior`

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
- **Dev server command**: `./mvnw spring-boot:run` → `http://localhost:8080`
- **API docs**: [e.g., Swagger UI at `http://localhost:8080/swagger-ui.html`]

## Security Considerations

- Never log sensitive data (passwords, tokens, PII)
- Use Spring Security for authentication/authorization
- Validate all request inputs
- Use parameterized queries (JPA handles this, but watch for native queries)
- Store secrets in environment variables, not in application.yml

## PR Instructions

- Title format: `[component] Brief description`
- Include migration scripts if DB schema changes
- Ensure backward compatibility for API changes
