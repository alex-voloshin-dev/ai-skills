# `AGENTS.md` Template: Java Spring Boot

```md
# [Service Name] Guidelines

## Stack

- Java [version]
- Spring Boot [version]
- Build: Maven
- Database: [PostgreSQL / other]

## Hard Rules

- controllers stay thin
- business logic belongs in services
- persistence details stay in repositories
- validate request inputs and emit structured errors

## Structure

- `src/main/java/.../controller`
- `src/main/java/.../service`
- `src/main/java/.../repository`
- `src/main/java/.../dto`
- `src/test/java`

## Commands

- Build: `[./mvnw clean package]`
- Run: `[./mvnw spring-boot:run]`
- Test: `[./mvnw test]`

## API Rules

- context path: `[path]`
- OpenAPI or Swagger location: `[path]`
- error contract: [Problem Details or project standard]

## Data Rules

- document migration workflow
- never mix schema changes with undocumented rollout steps
```
