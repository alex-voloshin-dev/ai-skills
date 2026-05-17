# AGENTS.md

## Project Overview

This is a Python FastAPI application. [DESCRIBE YOUR PROJECT PURPOSE HERE].

**Architecture**: See [ARCHITECTURE.md](./ARCHITECTURE.md) for system design, component relationships, data flows, and deployment topology.

## Setup Commands

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Run the application
uvicorn app.main:app --reload

# Run tests
pytest

# Run tests with coverage
pytest --cov=app --cov-report=term-missing

# Lint and format
ruff check .
ruff format .
```

## Code Style and Conventions

- Python 3.11+ with FastAPI
- Use type hints everywhere — function signatures, variables, return types
- Use Pydantic models for request/response schemas
- Use async/await for I/O-bound operations
- Follow PEP 8, enforced by ruff
- Use dependency injection via FastAPI's `Depends()`
- Use `snake_case` for functions/variables, `PascalCase` for classes
- Keep route handlers thin — delegate to service layer

## Project Structure

```
app/
├── main.py              # FastAPI app creation and startup
├── config.py            # Settings via pydantic-settings
├── routers/             # API route modules
├── services/            # Business logic
├── repositories/        # Data access layer
├── models/              # SQLAlchemy/database models
├── schemas/             # Pydantic request/response models
├── dependencies/        # Shared FastAPI dependencies
├── exceptions/          # Custom exceptions and handlers
└── utils/               # Utility functions
tests/
├── conftest.py          # Shared fixtures
├── test_routers/        # API endpoint tests
├── test_services/       # Service layer tests
└── test_repositories/   # Data layer tests
```

## Testing Instructions

- Use pytest with pytest-asyncio for async tests
- Use httpx.AsyncClient for API tests
- Fixtures in conftest.py for shared test setup
- Naming: `test_<what>_<condition>_<expected>`
- All new code must have tests. Bug fixes require regression tests.

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
- **Dev server command**: `uvicorn app.main:app --reload` → `http://localhost:8000`
- **API docs**: Swagger UI at `http://localhost:8000/docs`, ReDoc at `http://localhost:8000/redoc`

## Security Considerations

- Never commit `.env` files or secrets
- Use pydantic-settings for environment configuration
- Validate all inputs via Pydantic models
- Use parameterized queries (SQLAlchemy handles this)
- Apply rate limiting on public endpoints

## PR Instructions

- Title format: `[component] Brief description`
- Include Alembic migration if DB schema changes
- Run `ruff check .` and `pytest` before submitting
