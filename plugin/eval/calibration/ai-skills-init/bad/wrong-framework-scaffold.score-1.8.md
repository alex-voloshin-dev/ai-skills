# AI Assets Init Output — Framework Mismatch

Stack detected: Node.js project

## Problem

Generated Python/Django scaffold for a Node.js/Express project.

CLAUDE.md references Django models, views, migrations, but project uses Express and doesn't have those.

.ai-skills-memory/ created with Python-specific notes (requirements.txt vs package.json).

## What's Wrong

- Scaffold suggests `@python-skills` for a Node.js project
- Database config references Django ORM (project uses Sequelize)
- Test framework guidance for pytest (project uses Jest)
- Memory context includes Python conventions, not JavaScript conventions

## Result

Scaffold is unusable for this project. User has to manually fix or re-run with `--framework express`.
