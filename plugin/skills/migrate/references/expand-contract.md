# Expand–Contract (Parallel Change) — 6-Phase Pattern

Non-blocking schema migrations. Each phase is independently deployable and rollback-safe to the previous phase. Canonical reference: Sam Newman, *Building Microservices*, 2nd ed., Ch. 4; Fowler, "ParallelChange" (martinfowler.com/bliki/ParallelChange.html).

Rule: **never combine two phases in a single deploy.** One phase per release window.

---

## Phase 1 — Expand (additive only)

Add the new shape next to the old. Old code keeps working.

```sql
-- Postgres: nullable column
ALTER TABLE users ADD COLUMN email_normalized TEXT;
-- Postgres: index without table lock
CREATE INDEX CONCURRENTLY idx_users_email_norm ON users (email_normalized);

-- MySQL 8+: same shape, but DDL is NOT transactional
ALTER TABLE users ADD COLUMN email_normalized VARCHAR(320) NULL,
                  ALGORITHM=INPLACE, LOCK=NONE;
```

Rollback: `DROP COLUMN email_normalized` (still safe — nothing reads it).

---

## Phase 2 — Backfill

Populate the new shape from the old. Idempotent batches; verify counts.

```sql
-- Idempotent batch (Postgres + MySQL)
UPDATE users
   SET email_normalized = LOWER(TRIM(email))
 WHERE email_normalized IS NULL
   AND id BETWEEN :lo AND :hi;
```

```python
# Python batch driver — re-runnable
while True:
    n = db.execute(SQL, lo=cursor, hi=cursor + 10_000).rowcount
    if n == 0: break
    cursor += 10_000
```

Verify:
```sql
SELECT COUNT(*) FILTER (WHERE email_normalized IS NULL) AS missing,
       COUNT(*)                                          AS total
FROM users;
-- missing must be 0 (or only rows that legitimately lack email)
```

Rollback: re-run is harmless. If column was added wrong → revert to Phase 1, fix, re-backfill.

---

## Phase 3 — Dual-write

Application writes BOTH locations. Reads still hit the old column.

```java
// Java / Spring Data — dual-write in service layer
public void save(User u) {
    u.setEmail(input);
    u.setEmailNormalized(input == null ? null : input.trim().toLowerCase());
    repo.save(u);
}
```

```typescript
// TypeScript / Prisma
await prisma.user.update({
  where: { id },
  data: { email, emailNormalized: email?.trim().toLowerCase() ?? null },
});
```

Verify (drift check):
```sql
SELECT COUNT(*) FROM users
 WHERE email_normalized IS DISTINCT FROM LOWER(TRIM(email));
-- must trend to 0; alert if non-zero after deploy
```

Rollback: revert the application code; revert to Phase 2.

---

## Phase 4 — Switch reads

Application reads from the new column. Old still being written.

```python
# SQLAlchemy / Python — flip the read site
q = session.query(User).filter(User.email_normalized == norm)  # was: User.email == raw
```

This is the **safest rollback boundary**. If anything breaks (perf, missing index, wrong cast), revert the deploy → reads return to old column instantly.

Verify: shadow-read for one release (read both, log diffs) before promoting; baseline P95 query latency before vs after.

Rollback: redeploy previous image → reads return to old. Phases 1–3 stay intact.

---

## Phase 5 — Stop writes to old

New is the single writer. Old column is now stale but still present.

```java
public void save(User u) {
    u.setEmailNormalized(input == null ? null : input.trim().toLowerCase());
    // u.setEmail(...)  ← removed
    repo.save(u);
}
```

Run for one full release cycle to confirm no other reader is hitting the old column (logs, slow-query log, `pg_stat_statements`).

Rollback: revert app to Phase 3 (dual-write). Old column data is stale by N hours but recoverable from backfill.

---

## Phase 6 — Contract (final, destructive)

Drop old column / table. **No rollback**, only forward.

```sql
ALTER TABLE users DROP COLUMN email;          -- Postgres + MySQL
-- Optional: rename for ergonomics
ALTER TABLE users RENAME COLUMN email_normalized TO email;
```

Pre-flight: snapshot/backup, confirm zero references in code (`grep -r 'old_col_name'`), confirm zero references in stored procs / views / materialized views.

---

## Operation → 6-phase mapping

| Goal | Expand | Backfill | Dual-write | Switch | Stop | Contract |
|---|---|---|---|---|---|---|
| Add NOT NULL column | `ADD COLUMN nullable` | `UPDATE … SET col=…` | dual-write | reads from new | stop writes to old | `ALTER … SET NOT NULL` (drop default) |
| Rename column | `ADD newcol` | `UPDATE newcol=oldcol` | dual-write | switch | stop | `DROP COLUMN oldcol` |
| Split table | `CREATE` new tables | `INSERT … FROM` original | dual-write to both | switch readers | stop writes to old | `DROP TABLE` original |
| Change column type | `ADD newcol new_type` | `UPDATE newcol = CAST(oldcol AS new_type)` | dual-write | switch | stop | `DROP oldcol`, optionally rename |
| Move column to another table | `ADD col` on target | `INSERT/UPDATE` from source | dual-write to both | switch readers | stop writes to source col | `DROP` from source |
| Replace enum with lookup table | `CREATE` lookup + FK col | `UPDATE` FK from enum | dual-write both | reads via JOIN | stop writes to enum col | `DROP` enum column |

Cross-refs: `references/migration-tools-by-stack.md` (per-phase file in your stack's tool); Atlas docs (atlasgo.io) for declarative diff that respects expand-contract; Liquibase changesets — one changeset per phase, `runOnChange:false`, never edit a deployed changeset.
