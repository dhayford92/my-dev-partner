# Query performance

## N+1 avoidance
The classic trap — a query per row while iterating:

```python
# ❌ N+1: one query per order to load its owner
orders = await OrderModel.all()
for o in orders:
    owner = await o.owner            # a query each iteration

# ✅ prefetch the relation once
orders = await OrderModel.all().prefetch_related("owner")
for o in orders:
    owner = o.owner                  # already loaded
```

- `prefetch_related("relation")` for FK reverse / M2M relations you'll access in a loop.
- For forward FKs, `prefetch_related("owner")` also works; access as `o.owner` after.
- Never `await model.related.all()` inside a `for` over a queryset — prefetch first.

## Narrow reads
```python
# only fetch what you need on hot paths
rows = await OrderModel.filter(status="active").only("id", "reference", "status")
user = await ClientModel.get_or_none(id=uid).only("id", "status", "deleted_at")
```

## Counting + pagination
```python
qs = OrderModel.filter(deleted_at=None, **filters)
total = await qs.count()                                   # count before slicing
rows = await qs.order_by("-created_at").offset(params.offset).limit(params.limit)
```
`count()` runs a `SELECT COUNT(*)` — index the filtered columns so it stays cheap on big
tables.

## Indexing for reads
- Index every column used in `.filter(...)` / `.order_by(...)` on hot paths.
- Composite index (`Meta.indexes = [("status", "created_at")]`) when you filter+sort together.
- Foreign key columns: index them (Tortoise indexes FKs by default, but verify for query
  patterns).

## Transactions
Wrap multi-write operations so they commit or roll back together:
```python
from tortoise.transactions import in_transaction
async with in_transaction():
    order = await OrderModel.create(...)
    await WalletModel.filter(id=wid).update(balance=new_balance)
    await ActivityLog.create(...)
```
Keep transactions short — don't do network calls (email, HTTP) inside them; queue those as
background tasks after commit.

## Bulk operations
```python
await OrderModel.bulk_create([OrderModel(...) for _ in batch])     # many inserts
await OrderModel.filter(status="pending").update(status="expired") # set-based update, one query
```
Prefer a single `.update(...)`/`.delete()` over looping `save()` when changing many rows.

## When a query is slow
1. Identify the query (log it, or Tortoise's `.sql()` on a queryset).
2. Check for a missing index on the filtered/sorted columns.
3. Check for an N+1 (loop with awaited relations).
4. Consider a `.only()` to cut column bloat, or a caching layer (Redis) for hot read-through
   data with a clear invalidation trigger.
