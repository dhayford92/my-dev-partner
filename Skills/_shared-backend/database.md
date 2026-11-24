# Database Layer

**Engine:** PostgreSQL. **ORM:** Tortoise (async). **Migrations:** Aerich.

## Model conventions

Real example (`src/apps/users/models/client_model.py`):

```python
from tortoise.models import Model
from tortoise import fields
from src.apps.users.models.user_enum import ClientStatus


class ClientModel(Model):
    id = fields.UUIDField(pk=True)                              # UUID primary key, always

    # Basic info
    full_name = fields.CharField(max_length=250, null=True)
    email = fields.CharField(max_length=250, null=True, unique=True)
    phone = fields.CharField(max_length=20, unique=True, index=True)
    profile_picture = fields.TextField(null=True)

    wallet_balance = fields.FloatField(default=0.0)

    # Status — enum via CharEnumField
    status = fields.CharEnumField(ClientStatus, max_length=50, default=ClientStatus.VERIFICATION)
    is_phone_verified = fields.BooleanField(default=False)

    # Timestamps (UTC) + soft delete
    last_login_at = fields.DatetimeField(null=True)
    deleted_at = fields.DatetimeField(null=True)               # soft delete marker
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "client_users"                                 # snake_case, plural
        ordering = ["-created_at"]

    def __str__(self):
        return f"Client({self.phone})"

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None
```

### Rules

1. **UUID PK** on every model: `id = fields.UUIDField(pk=True)`.
2. **`class Meta`** with explicit **snake_case plural `table`** and `ordering = ["-created_at"]`.
3. **Timestamps:** `created_at = fields.DatetimeField(auto_now_add=True)`,
   `updated_at = fields.DatetimeField(auto_now=True)`. All datetimes are UTC / `TIMESTAMPTZ`.
4. **Soft delete:** nullable `deleted_at` + an `is_deleted` property. There is **no global
   soft-delete filter** — queries that must exclude deleted rows do so explicitly
   (`.filter(deleted_at=None)`). Deletes set `deleted_at = datetime.now(timezone.utc)`.
5. **Enums:** define `StrEnum` in a `user_enum.py` / `<domain>_enum.py`; store with
   `fields.CharEnumField(TheEnum, max_length=50, default=...)`.
6. **Foreign keys** use string model refs to dodge circular imports, and **every FK to the
   same target needs a unique `related_name`** (a real bug the owner hit):

   ```python
   # ❌ duplicate related_name → "backward relation duplicates" error at init
   department = fields.ForeignKeyField("models.MasterModel", related_name="compliances")
   region     = fields.ForeignKeyField("models.MasterModel", related_name="compliances")
   # ✅
   department = fields.ForeignKeyField("models.MasterModel", related_name="department_compliances")
   region     = fields.ForeignKeyField("models.MasterModel", related_name="region_compliances")
   ```
7. **Indexes:** `index=True` on frequently-filtered columns (e.g. `phone`, `email`,
   `user_id`), `unique=True` where the domain requires it. Add composite indexes / 
   `unique_together` in `Meta` for multi-column lookups.
8. **JSON columns:** `fields.JSONField(default=dict)` / `default=list` for flexible metadata.
9. **Auditing columns** beyond timestamps: `created_by_id` (UUID, nullable) where a record
   is created on behalf of another user.

## No shared abstract base model

The repos repeat `id` / timestamps / `deleted_at` inline in every model (there is no
`BaseModel`). This is a known duplication (see the Phase 4 report). **When scaffolding a new
project you MAY introduce a `TimestampedModel(Model)` abstract base** to remove the
repetition — but only if the owner opts in; the default reproduction keeps fields inline to
match existing style. If introduced:

```python
class TimestampedModel(Model):
    id = fields.UUIDField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    deleted_at = fields.DatetimeField(null=True)
    class Meta:
        abstract = True
    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None
```

## Tortoise config — `configs/database.py`

```python
from configs.settings import settings

ORM_MODELS = [
    "src.apps.users.models.client_model",
    "src.apps.users.models.admin_models",
    "src.apps.core.models.order_model",
    "src.apps.utils.models.activity_model",
    "src.apps.utils.models.notification_model",
    "aerich.models",                                # REQUIRED for migrations
]

tortoise_config = {
    "connections": {"default": settings.DATABASE_URL},
    "apps": {"models": {"models": ORM_MODELS, "default_connection": "default"}},
}

async def init_db() -> None:
    from tortoise import Tortoise
    await Tortoise.init(config=tortoise_config)

async def close_db() -> None:
    from tortoise import Tortoise
    await Tortoise.close_connections()
```

> **Every new model file must be added to `ORM_MODELS`** or its table is never created and
> Aerich won't see it.

## Migrations (Aerich)

`pyproject.toml`:

```toml
[tool.aerich]
tortoise_orm = "configs.database.tortoise_config"
location = "./migrations"
src_folder = "./."
```

Aerich generates **raw-SQL** migrations in `migrations/models/NN_<timestamp>_<name>.py`,
each with `RUN_IN_TRANSACTION = True` and `async def upgrade/downgrade(db) -> str`.

Workflow:

```powershell
aerich init -t configs.database.tortoise_config   # once, per project
aerich init-db                                     # first migration (creates tables)
aerich migrate --name "add_orders_table"           # after model changes
aerich upgrade                                      # apply
aerich downgrade                                    # roll back one
```

## Transactions

Multi-statement writes wrap in a transaction:

```python
from tortoise.transactions import in_transaction

async with in_transaction():
    order = await OrderModel.create(...)
    await WalletModel.filter(id=wallet_id).update(balance=new_balance)
    await ActivityLog.create(...)
```

## N+1 avoidance

- Use `.prefetch_related("relation")` for reverse/M2M and `.select_related("fk")` (Tortoise:
  fetch related via `prefetch_related` / `.<fk>` awaited) when iterating.
- Narrow columns with `.only("id", "status")` on hot reads.
- Never loop `await model.related.all()` inside a `for` over a queryset — prefetch first.

## Safe migrations on live data

- Additive first: add nullable columns / new tables, backfill, then tighten constraints in a
  later migration.
- Never drop/rename a column in the same deploy that stops writing to it.
- Review the generated SQL before `aerich upgrade` on production; migrations run in a
  transaction (`RUN_IN_TRANSACTION = True`) so a failure rolls back.
- Take a DB snapshot before destructive migrations.
