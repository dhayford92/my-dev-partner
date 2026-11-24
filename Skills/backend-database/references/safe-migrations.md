# Safe migrations on live data

Read this before applying any migration to a database with real data. The goal: no data loss,
no downtime, no failed deploy from a locking or NOT-NULL surprise.

## Golden rule: expand → migrate → contract

Never change a column's shape in one step. Split across deploys:

1. **Expand** — add the new (nullable) column / new table. Deploy. Backward compatible.
2. **Backfill** — copy/transform data into the new column (batched). Deploy code that writes
   BOTH old and new.
3. **Switch** — deploy code that reads the new column.
4. **Contract** — once nothing reads the old column, drop it in a later migration.

## Specific hazards

| Change | Safe way |
|--------|----------|
| Add column | Add as **nullable** (or with a default). Adding `NOT NULL` without a default on a big table rewrites/locks it — add nullable, backfill, then set NOT NULL. |
| Drop column | Stop writing it (deploy) → wait → drop in a later migration. Never in the same deploy that removes the code. |
| Rename column | Expand/contract: add new, backfill, switch reads, drop old. A direct rename breaks running instances mid-deploy. |
| Change type | Add new column of new type, backfill with a cast, switch, drop old. |
| Add index on a big table | Postgres: create `CONCURRENTLY` (outside a transaction) to avoid a long write lock. Aerich runs in a transaction, so for large tables run the `CREATE INDEX CONCURRENTLY` manually / in a separate non-transactional migration. |
| Add unique constraint | Backfill/clean duplicates first, add a normal index, then the unique constraint. |
| `NOT NULL` on existing column | Backfill all NULLs first, then add the constraint. |

## Before applying to prod
1. **Back up / snapshot** the database.
2. Read the generated SQL end to end.
3. Estimate lock scope: `ALTER TABLE ... ADD COLUMN` nullable is fast; anything rewriting rows
   or adding a non-`CONCURRENTLY` index on a large table locks writes.
4. Apply during a low-traffic window for anything non-trivial.
5. Have the `downgrade` path verified (or a manual rollback plan).

## Backfills
- Batch large backfills (e.g. 1–5k rows per loop) to avoid one giant transaction / long lock.
- Run backfills as a **script** (`scripts/backfill_*.py` using `in_transaction()` per batch),
  not inside the migration, for tables of any size.

## Data-loss red flags (stop and confirm)
- Any `DROP TABLE` / `DROP COLUMN` in the generated SQL you didn't intend.
- A migration Aerich generated that recreates a table (`DROP` + `CREATE`) instead of altering.
- `TRUNCATE` anywhere.

If the generated SQL contains any of these unexpectedly, do not `upgrade` — investigate the
model diff (often a changed `table` name, a removed field, or a type change Aerich couldn't
alter in place).
