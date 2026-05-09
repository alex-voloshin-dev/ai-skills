# Migration Tools by Stack — Quick Reference

Detect the stack, pick the canonical migration tool, follow stack conventions. Combine with `references/expand-contract.md` — one tool's "migration file" usually maps to one expand-contract phase.

---

## Stack → Tool table

| Stack signal | Default tool | Migration location | Generate / apply |
|---|---|---|---|
| Java + Spring Data (`pom.xml` has `spring-boot-starter-data-jpa`) | **Flyway** | `src/main/resources/db/migration/V<N>__<name>.sql` | auto on app start; `mvn flyway:migrate` |
| Java + Spring Data (alt) | **Liquibase** | `src/main/resources/db/changelog/db.changelog-master.xml` | `mvn liquibase:update` |
| Java + JPA / Hibernate (no Spring Boot) | **Liquibase** (XML/YAML changesets) | `db/changelog/*.xml` | `liquibase update`; `liquibase diff` for auto-gen |
| Python + SQLAlchemy | **Alembic** | `alembic/versions/<rev>_<slug>.py` | `alembic revision --autogenerate -m "..."`, `alembic upgrade head` |
| Python + Django | **built-in** | `<app>/migrations/<NNNN>_<name>.py` | `manage.py makemigrations`, `manage.py migrate` |
| Node + Prisma | **prisma migrate** | `prisma/migrations/<ts>_<name>/migration.sql` | `npx prisma migrate dev` (dev), `npx prisma migrate deploy` (prod) |
| Node + TypeORM | **typeorm** | `src/migrations/<ts>-<Name>.ts` | `typeorm migration:generate`, `typeorm migration:run` |
| Node + Drizzle | **drizzle-kit** | `drizzle/<ts>_<slug>.sql` + `meta/` | `drizzle-kit generate`, `drizzle-kit migrate` (or `push` for dev) |
| Go | **golang-migrate/migrate** or **goose** | `migrations/<ts>_<name>.up.sql` + `.down.sql` | `migrate -path ./migrations -database $URL up`; `goose up` |
| Rust + Diesel | **diesel** | `migrations/<ts>_<name>/{up,down}.sql` | `diesel migration generate <name>`, `diesel migration run` |
| Ruby on Rails | **ActiveRecord::Migration** | `db/migrate/<ts>_<name>.rb` | `rails g migration`, `rails db:migrate` |
| Polyglot / standalone DB | **Flyway** or **Liquibase** | tool-native | versioned SQL or changesets |

Canonical docs: flywaydb.org, liquibase.org, alembic.sqlalchemy.org, prisma.io/docs, typeorm.io, orm.drizzle.team, golang-migrate.github.io, diesel.rs, guides.rubyonrails.org.

## Versioned vs repeatable

- **Versioned** (Flyway `V*`, Alembic, Prisma, Drizzle, golang-migrate): runs once, recorded in `schema_migrations`. Editing a deployed file = checksum mismatch.
- **Repeatable** (Flyway `R*`, Liquibase `runOnChange:true`): re-runs when file changes. Use for views, stored procs, seed data — never DDL.

## Online schema-change tools (when DDL locks)

When a plain `ALTER TABLE` would lock the table beyond your write-budget window:

- **pt-online-schema-change** (Percona, MySQL) — trigger-based shadow table, atomic rename. FKs are tricky.
- **gh-ost** (GitHub, MySQL) — binlog-based, no triggers, throttled. Preferred over pt-osc on busy primaries.
- **pg_repack** (Postgres) — rebuild tables/indexes without long locks. Good for bloat and column-order changes.
- **pg_squeeze** (Postgres) — similar, background extension.

## Schema diffing tools

- **Atlas** (atlasgo.io) — declarative HCL/SQL, `atlas migrate diff` emits versioned files, lint rule "destructive change requires expand-contract."
- **sqitch** (sqitch.org) — change-based, no framework lock-in, plain SQL.
- **`pg_dump --schema-only`** + **migra** (djrobstep/migra) — diff baseline → migration SQL.
- **dbmate** (amacneil/dbmate) — minimal, multi-DB, plain SQL up/down.

## Postgres gotchas

- `CREATE INDEX CONCURRENTLY` avoids `ACCESS EXCLUSIVE`. Cannot run in a transaction → migration tool needs a `-- noTransaction` directive (Flyway: separate file; Alembic: `with op.get_context().autocommit_block():`).
- `SET lock_timeout = '2s'; SET statement_timeout = '30s';` per session before DDL → fail fast instead of stalling the DB.
- `ALTER TABLE ADD COLUMN ... DEFAULT <const>` rewrites the whole table on **PG <11**. PG 11+ stores non-volatile defaults in the catalog (no rewrite). Volatile defaults like `now()` still rewrite.
- `SET NOT NULL` requires a full scan. Mitigate: `CHECK (col IS NOT NULL) NOT VALID` → `VALIDATE CONSTRAINT` → promote to `NOT NULL` (PG 12+ skips the scan).
- `pg_advisory_lock` — serialize migration runners across replicas.
- `VACUUM FULL` / `CLUSTER` rewrite + lock — use `pg_repack` in production.

## MySQL gotchas

- **DDL is NOT transactional.** A failed `ALTER TABLE` leaves partial state — test on a replica; have a forward-fix ready, not a rollback assumption.
- **Implicit commit** — every DDL commits the current transaction. Don't mix DDL and DML expecting atomicity.
- **Online DDL algorithm** — specify explicitly: `ALGORITHM=INPLACE, LOCK=NONE`. Fall back to `COPY` only when InnoDB can't do inplace (some type changes, FK changes). Operations like adding `NOT NULL` may force `COPY` and lock.
- Use `pt-osc` / `gh-ost` when inplace isn't an option.
- Pin `utf8mb4` + `utf8mb4_0900_ai_ci` on new tables; collation mismatches break joins silently.

## Decision flow

1. Read project manifest → identify stack → pick row from the table above.
2. Check `CLAUDE.md` / `AGENTS.md` for a project override (some teams pick Liquibase over Flyway).
3. If the migration is destructive → route through `references/expand-contract.md` and emit one migration file per phase.
4. If the DDL would lock production → switch to the online schema-change tool for the affected step.
5. Add `lock_timeout` / explicit `ALGORITHM=` clauses to defend against runaway locks.
