# Model conventions

Base rules and a full model example are in [../../_shared-backend/database.md](../../_shared-backend/database.md).
This adds field-type guidance, relations, and auditing detail.

## Field types (Tortoise → Postgres)

| Use | Field |
|-----|-------|
| Primary key | `fields.UUIDField(pk=True)` |
| Short text | `fields.CharField(max_length=N)` |
| Long text | `fields.TextField()` |
| Money | `fields.DecimalField(max_digits=12, decimal_places=2)` (prefer over Float for currency) |
| Integer | `fields.IntField()` / `fields.BigIntField()` |
| Boolean | `fields.BooleanField(default=False)` |
| Enum | `fields.CharEnumField(TheStrEnum, max_length=50, default=...)` |
| Timestamp | `fields.DatetimeField(...)` (UTC) |
| Flexible data | `fields.JSONField(default=dict)` / `default=list` |
| FK id only (no relation) | `fields.UUIDField(null=True)` (e.g. `referred_by_id`) |

> The repos use `FloatField` for wallet/amount in places. For **new** money columns prefer
> `DecimalField` (note it as an improvement, don't silently change existing tables).

## Relations

```python
# Foreign key — string ref avoids circular imports
owner = fields.ForeignKeyField("models.ClientModel", related_name="orders")

# CRITICAL: two FKs to the SAME model need DIFFERENT related_names
department = fields.ForeignKeyField("models.MasterModel", related_name="department_items")
region     = fields.ForeignKeyField("models.MasterModel", related_name="region_items")

# Many-to-many with explicit through table name
tags = fields.ManyToManyField("models.TagModel", related_name="orders", through="order_tags")
```

- Access FK: `await order.owner` (awaitable) or prefetch (see performance.md).
- M2M assignment: `await order.tags.add(*tag_list)`; `await order.tags.clear()` before
  re-assigning.
- A plain `<name>_id` UUID column (no `ForeignKeyField`) is used when you want the id without
  a DB-level FK/relation (e.g. cross-service or soft references) — matches the repos.

## Auditing columns

- `created_by_id = fields.UUIDField(null=True)` — who created the row on behalf of others.
- Timestamps are the baseline audit. For a full change trail, that's the **ActivityLog**
  (see [../../_shared-backend/logging.md](../../_shared-backend/logging.md)), not per-table columns.

## Indexes & constraints

```python
email = fields.CharField(max_length=250, unique=True, index=True)   # single-column
class Meta:
    table = "orders"
    ordering = ["-created_at"]
    indexes = [("status", "created_at")]          # composite index
    unique_together = [("owner", "reference")]     # composite unique
```

Index columns you filter/sort by frequently (foreign keys, `status`, `email`, `phone`,
`user_id`). Don't over-index write-heavy tables.

## Enums

Define `StrEnum` in `<domain>_enum.py`, store with `CharEnumField`. In responses, `use_enum_values=True`
on the schema (or `obj.status.value`) yields the string.

## The optional abstract base
See `assets/base_model.py`. Default = inline fields (matches repos). Opt-in = `class
Foo(TimestampedModel)`.
