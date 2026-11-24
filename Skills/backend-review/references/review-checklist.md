# Review checklist (by category)

The script covers the mechanical items (marked ⚙). The rest need reading. Work the categories;
cite `file:line`; group findings (see [grouping.md](grouping.md)).

## 1. Correctness
- [ ] Does it do what the task asked? Trace the real path.
- [ ] Edge cases: null/empty/missing, first-run, duplicate, concurrent, large, timezone.
- [ ] Right status code, right persona scope, right resource ownership check.
- [ ] Partial-update uses `model_dump(exclude_none=True)`; not clobbering fields.
- [ ] Multi-write wrapped in `in_transaction()`; no partial commits on failure.
- [ ] No race: check-then-act on shared state (wallet, stock, unique code) inside a transaction.

## 2. Conventions (vs `../../_shared-backend/`)
- [ ] Structure/naming: files in the right place, `controllers/` plural, `<resource>_x.py`.
- [ ] Routing: `/{domain}/api/v1/{persona}/{feature}`, thin router → controller. ⚙(response_model)
- [ ] Config: `settings.X`, UPPER_CASE, no scattered `os.getenv`. ⚙
- [ ] Response envelopes + snake_case + ISO-8601 UTC.
- [ ] Error style: `HTTPException(detail, headers X-Error-Code)`, no global handler. ⚙

## 3. Security  (deep dive → backend-security)
- [ ] Every mutating/reading-private route has the correct persona guard.
- [ ] Ownership/tenant scope enforced (`organization_id`/`team_id`/`user_id`), not just persona.
- [ ] Input validated by a schema; no raw client string into `order_by`/`filter`/SQL. ⚙(secrets)
- [ ] No secret/token/PII in responses or logs; PII redacted.
- [ ] Auth/OTP/reset endpoints rate-limited. ⚙

## 4. Performance
- [ ] No N+1 (relations awaited in a loop) — `prefetch_related`.
- [ ] Filtered/sorted columns are indexed.
- [ ] List endpoints paginate; no unbounded `.all()` returned.
- [ ] No sync/blocking call (requests, boto3, heavy CPU) on the async request path.
- [ ] `count()` + slice, not fetch-all-then-len.

## 5. Error handling
- [ ] Try/except ladder: `HTTPException` re-raised, `ValueError`→4xx, `Exception`→log+500. ⚙(swallow)
- [ ] No bare `except: pass`; no swallowed exception without logging.
- [ ] Client messages are safe (no stack trace / internal id); machine code in `X-Error-Code`.

## 6. Logging coverage
- [ ] `logger`, never `print`. ⚙
- [ ] Every audited create/update/delete calls `ActivityService`. ⚙(heuristic)
- [ ] PII redacted in logs + activity metadata (`redact(...)`).
- [ ] Errors logged before returning 500.

## 7. Test coverage
- [ ] Critical/new logic has *some* exercise (test, or a documented manual verification).
- [ ] Don't demand a suite the project never had — flag only genuinely risky untested paths
      (auth, money, migrations).

## 8. Migration safety
- [ ] New/changed model → a migration exists and is registered in `ORM_MODELS`. ⚙(soft-delete)
- [ ] Generated SQL reviewed; no unexpected DROP/rename; NOT NULL/unique adds are backfilled.
- [ ] Live-data changes follow expand→contract (`../../_shared-backend/database.md`).

## 9. Context sync
- [ ] `SCHEMA.md`/`API.md`/`CHANGELOG.md` updated in the same change (`project-context`).

## Money & soft-delete note
The script flags `FloatField` on money-like columns and models without `deleted_at`. In the
reference repos these are common and sometimes intentional — treat as SHOULD-FIX/NITPICK and
confirm intent, not automatic BLOCKING.
