# Using map_codebase.py

`scripts/map_codebase.py` is the fact-finder. Read-only; run it first, every time.

```powershell
python .\scripts\map_codebase.py --project "D:\...\some-api"          # human report
python .\scripts\map_codebase.py --project "D:\...\some-api" --json   # for further processing
```

## What it reports
**Inventory:** sub-apps, model files, table names, routers, routes (method + reconstructed
`<prefix><path>` + file), controllers, services, and the `ORM_MODELS` registration list.

**Drift checks (WHAT IS vs the canonical target):**

| Check | Flags when |
|-------|-----------|
| CONFIG | plain `os.environ` class (not pydantic-settings); or snake_case fields (canonical is UPPER_CASE) |
| LOGGING | `print(` used anywhere (canonical: stdlib `logger`) |
| RESPONSE | pagination shape isn't `{data,current_page,page_limit,total_count}` |
| ERRORS | a global `{error:{...}}` exception handler exists (canonical: raise `HTTPException`) |
| ROUTING | a `views/*.py` includes routers without `/api/v1` |
| DB (money) | a money-like column (`amount/price/balance/total/fee`) uses `FloatField` |
| DB (soft delete) | a model file has no `deleted_at` |
| DB (related_name) | two FK/M2M to the **same target** share a `related_name` (clash) |
| DB (ORM_MODELS) | a file defining a `Meta.table` isn't registered |

## Interpreting the output
- The drift list is a **starting point**, not the whole audit — it catches mechanical
  deviations. Semantic problems (wrong logic, auth bypass, N+1) need reading the code.
- Drift ≠ bug. Some drift is deliberate (an older repo, a product-specific choice). Confirm
  intent before recommending a change; note deliberate deviations in report §8.
- **Money-as-Float** and **missing soft delete** are common in the reference repos — treat as
  discussion items (potential Phase-4 improvements), not automatic defects.

## Limitations (read the code for these)
- Regex-based: won't catch routes built dynamically, decorators via variables, or models defined
  unusually. Cross-check counts against `/docs`.
- Doesn't judge logic, security, or performance — only mechanical structure/drift.
- "Not in ORM_MODELS" can be a false positive for a model registered via a package `__init__`
  re-export; verify before reporting.

## Feeding the report
Drop the drift list into report §5 (drift) and the unregistered-model / commented-endpoint
findings into §6 (dead code). Cross-check the money/soft-delete findings against
[../../_shared-backend/database.md](../../_shared-backend/database.md) before recommending.
