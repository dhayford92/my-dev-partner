# Migrations (Aerich)

## Config
`pyproject.toml`:
```toml
[tool.aerich]
tortoise_orm = "configs.database.tortoise_config"
location = "./migrations"
src_folder = "./."
```
Migrations are raw-SQL files in `migrations/models/NN_<timestamp>_<name>.py`, each with
`RUN_IN_TRANSACTION = True` and `async def upgrade(db)/downgrade(db) -> str`.

## Workflow
```bash
aerich init -t configs.database.tortoise_config   # once per project
aerich init-db                                     # first migration (creates all tables)

# after every model change:
aerich migrate --name "add_invoice_table"          # generate
#   >> open migrations/models/*.py and READ the SQL <<
aerich upgrade                                      # apply
aerich downgrade                                    # roll back last
aerich history                                      # list
```

The `db.ps1` helper wraps these on Windows and prints the review reminders.

## Rules
1. **Register the model in `ORM_MODELS` first** — Aerich only sees registered models.
2. **Always read the generated SQL** before `upgrade`, especially column drops/renames and
   `NOT NULL` additions.
3. One logical change per migration; name it descriptively.
4. Commit the migration files — they're the source of truth for the schema across
   environments. Never edit an already-applied migration; make a new one.
5. `RUN_IN_TRANSACTION = True` means a failed migration rolls back cleanly on Postgres.

## Resetting a dev database
```sql
DROP SCHEMA public CASCADE; CREATE SCHEMA public;
```
then `aerich init-db`. **Dev only** — never on shared/live data.

## Multi-environment
Same migration files run in dev/staging/prod. Apply with `aerich upgrade` on deploy (bare-metal:
part of the deploy script). For live data, see [safe-migrations.md](safe-migrations.md).
