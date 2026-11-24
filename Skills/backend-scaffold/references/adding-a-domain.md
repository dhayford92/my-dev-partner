# Adding a domain after scaffolding

Once the project boots, replace the `example` teaching resource with real domains. Each
domain follows model → schema → controller → router → view-include → migration. Use the
`backend-database` skill for the model/migration and `backend-api-design` for the
route/controller/validator stubs — this file is the quick checklist.

## 1. Model — `src/apps/<domain>/models/<resource>_model.py`
UUID PK, snake_case plural table, timestamps, `deleted_at` + `is_deleted`. Register it in
`configs/database.py` `ORM_MODELS`. See [../../_shared-backend/database.md](../../_shared-backend/database.md).

## 2. Schema — `src/schemas/<domain>/<resource>_schemas.py`
Follow the taxonomy: `Create*Schema`, `Update*Schema`, `*TableSchema`, `*DetailSchema`,
`*ListSchema(PaginatedResponse[...])`, `Select*Schema`. See
[../../_shared-backend/code-style.md](../../_shared-backend/code-style.md).

## 3. Controller — `src/apps/<domain>/controllers/<resource>_controller.py`
Static-method class, try/except ladder, `in_transaction()` for multi-write, activity logging
on every mutation, canonical pagination on list. Copy `example_controller.py`.

## 4. Router — `src/apps/<domain>/routers/<persona>_<feature>_router.py`
Thin, `APIRouter(prefix="/<persona>/<feature>")`, `response_model=` per route, persona guard
dependency, rate-limit decorators on writes. Copy `example_router.py`.

## 5. Wire it — `src/views/<domain>.py`
`app.include_router(<your>_router, prefix=API_V1)`.

## 6. Migrate
```powershell
aerich migrate --name "add_<resource>_table"
aerich upgrade
```

## 7. Delete the example
Remove `example_model.py`, `example_schemas.py`, `example_controller.py`,
`example_router.py`, the `ORM_MODELS` entry for it, and its include in `views/core.py`. Then
`aerich migrate --name "drop_example"` + `aerich upgrade`.

## Auth model upgrades
The scaffold ships persona guards + seeded relational RBAC. To adopt JSON framework/action
RBAC or team+RLS multi-tenancy, use the `backend-auth` skill — it layers those on and updates
`libs/auth.py`, the token claims, and the seeder accordingly.
