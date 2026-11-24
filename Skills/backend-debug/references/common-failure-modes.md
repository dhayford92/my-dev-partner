# Common failure modes (FastAPI + Tortoise stack)

A hypothesis catalogue — match the symptom to a likely cause to trace faster. **A matching
pattern is a hypothesis, not a diagnosis**: still do the causal trace and verify the specific
case.

## Async / await
- **Coroutine never awaited** → a coroutine object where you expected a value; "was never
  awaited" warning. Cause: missing `await` on an async call (ORM query, service method).
- **Blocking call in async path** → event loop stalls / timeouts. Cause: a sync network/CPU call
  (requests, boto3, heavy loop) not offloaded. `resend.Emails.send` is sync — that's why email
  goes through BackgroundTasks.
- **Sync function calling async** → `RuntimeError: no running event loop`.

## Tortoise ORM
- **N+1** → slow endpoint, many identical queries. Cause: awaiting a relation inside a loop over
  a queryset. Fix: `prefetch_related`. See `../../_shared-backend/database.md` performance.
- **`backward relation ... duplicates`** at startup → two FKs to the same model share a
  `related_name`. Fix: unique related_names.
- **`ConfigurationError` / table missing** → model not in `ORM_MODELS`, or migration not applied.
- **Transaction not rolling back** → writes outside `in_transaction()`, or an `await` network
  call inside the transaction that failed after a partial commit.
- **`.only()` field access** → attribute error when you access a column you didn't select.
- **Enum stored/compared wrong** → comparing a `CharEnumField` value to a raw string vs the enum;
  `use_enum_values` on the schema affects the serialized form.

## Auth / JWT
- **`Invalid audience` / `Invalid issuer`** → mint and verify use different `aud`/`iss`. Centralise
  the values.
- **Token "valid" but rejected** → it's in the Redis denylist (logout/reset denied it), or the
  per-user deny key is set.
- **Everyone gets 401 after a Redis blip** → denylist/`is_denied` check can't reach Redis; auth
  hard-depends on it. Distinguish "Redis down" from "token bad."
- **Wrong persona passes** → guard checks `user_type` but the token was minted without it, so the
  comparison is against `None`/`"None"`.
- **OTP/reset token replay** → the purpose `type` claim wasn't checked (`verify_token(token_type=…)`).

## Config / lifespan / jobs
- **Missing env var → `None` at runtime** (older os.environ style) instead of failing at boot →
  move to validated settings (`../../_shared-backend/config.md`).
- **Scheduler double-runs / duplicate jobs** → multiple workers each start the scheduler; run it
  in exactly one process. Or missing `replace_existing=True`.
- **`redis_client` is None in a handler** → captured the import-time value instead of the live
  one; read `configs.lifespan.redis_client` at call time.

## Requests / responses
- **422 you didn't expect** → pydantic validation; read the `detail` list (`loc`) for the field.
- **Rate-limit decorator error** → the handler is missing `request: Request` (SlowAPI needs it).
- **CORS failure in browser** → origin not in `cors_origins`; note the middleware add-order.
- **Wrong error shape** → someone put a machine code in `detail` instead of the `X-Error-Code`
  header, or added a global handler (canonical is plain `HTTPException`).

## Migrations
- **Aerich generated a DROP/CREATE instead of ALTER** → a changed `Meta.table` name or a removed
  field; do NOT `upgrade` on live data — see `../../_shared-backend/database.md` + backend-database
  safe-migrations.
- **Migration applies in dev, fails in prod** → data that violates a new NOT NULL/unique; backfill
  first.

## Background tasks / email
- **Email "sent" but never arrives** → `send_email` swallows failures and returns False; check the
  return + logs; verify `MAIL_API_KEY`.
- **BackgroundTask ran but side effect missing** → exception inside the task (tasks run after the
  response; their errors don't surface to the client) — check logs.
