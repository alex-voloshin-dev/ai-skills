# `AGENTS.md` Template: .NET Web API

```md
# [Service Name] Guidelines

## Stack

- .NET [version]
- ASP.NET Core Web API
- Test framework: [xUnit / NUnit]

## Hard Rules

- keep controllers thin
- use dependency injection consistently
- validate request models
- separate domain, application, and infrastructure concerns

## Structure

- `Controllers/`
- `Services/` or `Application/`
- `Domain/`
- `Infrastructure/`
- `Tests/`

## Commands

- Restore: `[dotnet restore]`
- Build: `[dotnet build]`
- Run: `[dotnet run --project ...]`
- Test: `[dotnet test]`

## API Rules

- document auth strategy
- keep error responses consistent
- call out migration and configuration requirements
```
