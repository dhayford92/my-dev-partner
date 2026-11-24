# Verify mode

`scripts/verify_context.py` audits the context against the codebase. Read-only; exit 0 by
default (report), non-zero with `--strict` (for CI).

## What it checks
1. **Context files present** — all six exist.
2. **Tables** — extracts every `class Meta: table = "..."` from `src/apps/**/models/*.py` and
   flags any table name not mentioned in `SCHEMA.md`.
3. **Routes** — extracts `APIRouter(prefix=...)` + `@<router>.<method>("...")` from
   `src/apps/**/routers/*.py`, builds `<prefix><path>` fragments, and flags any not mentioned
   in `API.md`.
4. **CHANGELOG staleness** — compares the newest `src/` file mtime to the newest date in
   `CHANGELOG.md`; warns if code changed after the last entry.

## What it CANNOT catch (still needs a human/AI eye)
- Whether the documented *columns/contracts* are correct — it only checks that the table/route
  is *mentioned*, not that its details match.
- Semantic drift in `OVERVIEW.md` / `ARCHITECTURE.md` (purpose, flows, integrations).
- Removed tables/routes still documented (it reports code→docs gaps, not docs→code; skim for
  stale entries during handoff).
- ADR correctness.

So: a clean `verify` means "nothing is undocumented," not "everything documented is right."
Pair it with a skim of OVERVIEW/ARCHITECTURE.

## Typical usage
```powershell
# after a batch of changes / before a handoff
python .\scripts\verify_context.py --project "D:\...\my-api"

# in CI (fail the build on drift)
python .\scripts\verify_context.py --project . --strict
```

## Reading the output
- `NOT documented in SCHEMA.md` → add a table block for each.
- `NOT documented in API.md` → add a row for each route.
- `code changed after the last CHANGELOG entry` → add a changelog entry (or confirm the change
  was trivial/non-notable).
