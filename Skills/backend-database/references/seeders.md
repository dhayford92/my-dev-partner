# Seeders

There is no seeder framework — seeders are plain idempotent scripts under `scripts/` that init
Tortoise and upsert reference data. `scaffold` ships `scripts/seed.py` (roles + super admin);
`new_model.py --seeder` emits `scripts/seed_<resource>.py`.

## Shape
```python
import asyncio
from tortoise import Tortoise
from configs.database import tortoise_config
from src.apps.core.models.plan_model import PlanModel

DATA = [
    {"name": "Free",  "price": 0},
    {"name": "Pro",   "price": 2900},
]

async def seed():
    for row in DATA:
        obj, created = await PlanModel.get_or_create(name=row["name"], defaults=row)
        if not created:                      # keep existing rows in sync
            for k, v in row.items():
                setattr(obj, k, v)
            await obj.save()
        print(f"  plan: {row['name']} {'(created)' if created else '(updated)'}")

async def main():
    await Tortoise.init(config=tortoise_config)
    await seed()
    await Tortoise.close_connections()

if __name__ == "__main__":
    asyncio.run(main())
```

Run: `python -m scripts.seed_plan` (from the project root, venv active).

## Rules
1. **Idempotent** — safe to run repeatedly. Use `get_or_create` keyed on a natural unique
   field, then update-in-place. Never blind-`create` (creates duplicates on re-run).
2. **Deterministic keys** — key on `name`/`slug`/`email`, not on generated ids.
3. **Reference data only** — roles, permissions, plans, categories, a bootstrap admin. Not
   test/fixture data (that belongs in tests).
4. **Secrets from settings** — e.g. the seeded admin password comes from
   `settings.SEED_ADMIN_PASSWORD`, never hard-coded.
5. Large datasets (CSV import such as a `plans.csv`): read the file, upsert per row, report
   created/updated/errors counts.

## When to run
- After `aerich upgrade` on first deploy (roles/permissions/admin bootstrap).
- After adding new reference data (re-run the seeder; idempotency makes it safe).
