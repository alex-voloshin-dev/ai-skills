# `AGENTS.md` Template: Python FastAPI

```md
# [Service Name] Guidelines

## Stack

- Python [version]
- FastAPI
- Dependency manager: [pip / uv / poetry]
- Test framework: pytest

## Hard Rules

- validate request and response models
- keep route handlers thin
- separate integration code from domain logic
- never hardcode secrets or provider keys

## Structure

- `src/` — application code
- `tests/` — pytest suites
- `[config path]` — runtime config

## Commands

- Install: `[pip install -e ".[dev]"]`
- Run: `[uvicorn src.main:app --reload --port 8080]`
- Test: `[pytest]`

## API Rules

- define typed request and response models
- capture integration failure behavior explicitly
- document auth and rate limiting expectations
```
