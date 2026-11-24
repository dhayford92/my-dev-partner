---
name: backend-database
description: >-
  Design and evolve the database in Denzel's canonical Tortoise ORM + PostgreSQL + Aerich
  conventions — UUID PKs, snake_case plural tables, UTC timestamps, soft delete via nullable
  deleted_at, CharEnumField enums, JSON columns, foreign keys with unique related_names,
  indexing strategy, unique constraints, auditing columns, transactions with in_transaction(),
  N+1 avoidance (prefetch_related / .only), query optimisation, seeders, and SAFE migrations
  on live production data. Generates model stubs + seeders and wraps the Aerich workflow. USE
  THIS whenever creating or changing a database model/table/schema, adding columns/relations/
  indexes, writing or reviewing a migration, designing a data model, adding a seeder, fixing
  an N+1 or slow query, or planning a schema change against live data. Use backend-scaffold
  for a new project; backend-api-design for the endpoint over the table.
---

# backend-database

Design and evolve schema to the canonical conventions safely. **The model/migration/soft-
delete/relation rules live in [../_shared-backend/database.md](../_shared-backend/database.md)** — read it;
this skill adds depth on performance and safe live-data migrations, plus generators.

## When to use
- Creating or changing a model/table.
- Adding columns, relations, indexes, or constraints.
- Writing or reviewing an Aerich migration (especially against live data).
- Diagnosing an N+1 or a slow query; adding a seeder.

## The rules in one screen
- **UUID PK**, `class Meta: table="<snake_plural>"`, `ordering=["-created_at"]`.
- Timestamps `created_at=auto_now_add`, `updated_at=auto_now` (UTC/`TIMESTAMPTZ`).
- **Soft delete** = nullable `deleted_at` + `is_deleted` property; queries exclude with
  `.filter(deleted_at=None)` (no global filter).
- Enums via `CharEnumField(StrEnum, max_length=50, default=...)`.
- FKs use string refs; **each FK to the same target needs a unique `related_name`**.
- Index hot filter columns (`index=True`), `unique`/`unique_together` per the domain,
  composite `indexes` in `Meta`.
- Register every model module in `configs/database.py` `ORM_MODELS`.
- Migrations: Aerich raw-SQL, `aerich migrate --name` → **review SQL** → `aerich upgrade`.
- Transactions: `async with in_transaction():` for multi-write.
- Full detail + code: [../_shared-backend/database.md](../_shared-backend/database.md).

## Generate a model + seeder
```powershell
# Windows
python .\scripts\new_model.py --project "D:\...\my-api" --domain core --resource invoice --seeder
```
Emits `src/apps/<domain>/models/<resource>_model.py` (with commented relation/index/enum
examples), registers it in `ORM_MODELS`, and optionally `scripts/seed_<resource>.py`. It does
**not** migrate — you edit fields, then migrate.

## Migration workflow
```powershell
.\scripts\db.ps1 -Action init      -Project <ROOT>   # first time only
.\scripts\db.ps1 -Action migrate   -Name "add_invoice_table" -Project <ROOT>
#   >> REVIEW migrations/models/*.py SQL <<
.\scripts\db.ps1 -Action upgrade   -Project <ROOT>
```
Cross-platform: run the `aerich` commands directly (see
[references/migrations.md](references/migrations.md)).

## Deep references
- [references/model-conventions.md](references/model-conventions.md) — field types, relations,
  the unique-`related_name` rule, auditing, the optional abstract base.
- [references/migrations.md](references/migrations.md) — Aerich workflow + config.
- [references/safe-migrations.md](references/safe-migrations.md) — **read before touching live
  data**: additive-first, expand/contract, backfills, zero-downtime column changes.
- [references/performance.md](references/performance.md) — indexing strategy, N+1 avoidance,
  `.only()`/`prefetch_related`, transactions, counting.
- [references/seeders.md](references/seeders.md) — idempotent seeders, default reference data.

## The optional abstract base
`assets/base_model.py` provides a `TimestampedModel` that removes the repeated
id/timestamps/deleted_at. The repos DON'T use one (fields are inline). Introduce it only when
the owner opts in for a project — see [../_shared-backend/database.md](../_shared-backend/database.md).

## Don't
- Don't hard-delete where soft delete is the pattern; don't drop/rename columns in the same
  deploy that stops writing them (see safe-migrations).
- Don't apply a migration to production without reading the generated SQL.
- Don't add a model file without registering it in `ORM_MODELS`.
