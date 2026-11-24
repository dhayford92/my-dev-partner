# Designing endpoints (beyond CRUD)

The generator gives you CRUD. Everything else is a design decision — make it deliberately and
consistently with `../../_shared-backend/`.

## Persona & guard
Decide which persona owns the endpoint and pick the guard: `CurrentClientUser`,
`CurrentAdminUser`, `CurrentVendorUser`, `CurrentSuperAdminUser`, or `CurrentUser` (any
authenticated). The persona is also the first path segment (`/client/...`, `/admin/...`).
Public endpoints take no guard. For fine-grained RBAC (org-scoped), the permission check
happens **inside the controller** — see [../../_shared-backend/auth.md](../../_shared-backend/auth.md).

## Naming actions
- CRUD maps to REST: `GET /` (list), `GET /{id}`, `POST /`, `PATCH /{id}`, `DELETE /{id}`.
- Non-CRUD actions are sub-paths with a verb: `POST /{id}/approve`, `POST /{id}/cancel`,
  `POST /{id}/resend`. Keep them under the resource prefix.
- Bulk: `POST /bulk-approve` with a list body; return a per-item result summary.

## Filtering / sorting / pagination
- **Pagination** is mandatory on lists: `page`/`limit` query params → the
  `{data, current_page, page_limit, total_count}` envelope via `create_paginated_response`.
- **Filtering**: explicit typed query params mapped to `.filter(...)`. Don't accept arbitrary
  filter expressions from the client.
- **Sorting**: a `sort` param mapped through an allow-list to `.order_by(...)`; default
  `-created_at`. Never pass a raw client string into `order_by`.

```python
@router.get("", response_model=OrderListSchema)
async def list_orders(auth: CurrentAdminUser, params: PaginationParams = Depends(),
                      status: str | None = None, sort: str = "-created_at"):
    return await OrderController.list(params, status=status, sort=sort)
```

## Status codes (canonical)
`201` create, `200` read/update/action, `204`-style deletes still return `{message}` at 200,
`400` domain error, `401` unauth, `403` wrong persona/permission, `404` missing, `409`
conflict, `422` validation, `429` rate limited. See
[../../_shared-backend/response-contract.md](../../_shared-backend/response-contract.md).

## Idempotency
Not in the repos by default. For payment/create endpoints where a double-submit is dangerous,
accept an `Idempotency-Key` header and dedupe via Redis before executing:
```python
key = f"idem:{idempotency_key}"
if not await redis_client.set(key, "1", nx=True, ex=86400):
    raise HTTPException(status.HTTP_409_CONFLICT, detail="Duplicate request")
```
Flag this explicitly when designing such an endpoint — don't add it silently everywhere.

## Rate limiting
Decorate sensitive/write endpoints with `@limiter.limit(RateLimitConfig.X)` (handler must take
`request: Request`). Auth/OTP/register/reset get the tighter named limits; general writes get
`CREATE_RESOURCE`/`UPDATE_RESOURCE`/`DELETE_RESOURCE`. See
[../../_shared-backend/routing.md](../../_shared-backend/routing.md).

## Request/response bodies
- Requests: `Create*Schema` / `Update*Schema` with `Field(...)` constraints and `EmailStr`
  where relevant. `Update*` fields are all optional; apply with `model_dump(exclude_none=True)`.
- Responses: `*TableSchema` for list rows, `*DetailSchema` for single reads (usually extends
  Table). Never return ORM objects or raw dicts — always a schema with `response_model=`.
- snake_case keys throughout; ISO-8601 UTC datetimes.

## When a case isn't covered
If a design need isn't answered by `../../_shared-backend/` (a new envelope, a cross-cutting header, a
non-standard auth pattern), surface it and get a decision rather than inventing — then encode
the answer back into `../../_shared-backend/` so it's canonical everywhere.
