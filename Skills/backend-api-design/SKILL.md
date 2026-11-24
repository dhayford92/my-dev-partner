---
name: backend-api-design
description: >-
  Design and generate API endpoints in Denzel's canonical FastAPI style — route organisation,
  the /{domain}/api/v1/{persona}/{feature} URL shape, versioning, naming, request validation,
  the snake_case response envelopes ({message,data}, pagination {data,current_page,page_limit,
  total_count}), plain-HTTPException errors with X-Error-Code headers, status codes,
  pagination/filtering/sorting, idempotency, rate limiting, and how persona/permission
  middleware attaches. Generates matching route + controller + validator(schema) + optional
  service/model stubs via a script. USE THIS whenever adding endpoints, designing or building
  an API surface, creating a new resource/route/controller, wiring routers, deciding URL
  structure or status codes, shaping request/response bodies, or adding pagination/filtering
  to an existing FastAPI + Tortoise project. Use backend-scaffold instead when starting a
  whole new project; use backend-database for the model/migration behind the endpoint.
---

# backend-api-design

Design and generate endpoints that match the conventions exactly. **Routing, envelopes, and
status codes are defined in `../_shared-backend/routing.md` and `../_shared-backend/response-contract.md`** —
read those; this skill applies them and generates stubs.

## When to use
- Adding endpoints / a new resource to an existing project.
- Deciding URL structure, versioning, status codes, or request/response shapes.
- Adding pagination, filtering, sorting, or rate limits to routes.

Starting a whole project? Use `backend-scaffold`. Designing the table behind the endpoint?
Use `backend-database`.

## The rules in one screen
- **URL:** `/{domain}/api/v1/{persona}/{feature}` — domain mount (`/users`,`/core`,`/utils`)
  + `/api/v1` (added in `views/<domain>.py`) + router prefix `/<persona>/<feature>`.
- **Routers are thin** — `return await <Controller>.<method>(...)`, `response_model=` on every
  route, persona guard dependency, rate-limit decorator on writes (handler needs
  `request: Request`).
- **Success:** `{message, data?}`. **List:** `{data, current_page, page_limit, total_count}`
  (via `create_paginated_response`). **Errors:** `raise HTTPException(status_code, detail,
  headers={"X-Error-Code": ...})` — no custom envelope.
- **Validation:** pydantic schemas per domain, taxonomy `Create/Update/*Table/*Detail/*List/
  Select`. See [../_shared-backend/code-style.md](../_shared-backend/code-style.md).
- Full detail: [../_shared-backend/routing.md](../_shared-backend/routing.md),
  [../_shared-backend/response-contract.md](../_shared-backend/response-contract.md),
  [../_shared-backend/controllers-services.md](../_shared-backend/controllers-services.md).

## Generate a resource

**Windows:**
```powershell
.\scripts\new_resource.ps1 -Project "D:\...\my-api" -Domain core -Persona admin `
    -Resource order -WithModel -WithService -Wire
```
**Cross-platform:**
```bash
python scripts/new_resource.py --project /abs/my-api --domain core --persona admin \
    --resource order --with-model --with-service --wire
```

This emits, matching style exactly:
- `src/schemas/<domain>/<resource>_schemas.py` — the validator taxonomy.
- `src/apps/<domain>/controllers/<resource>_controller.py` — CRUD with pagination + activity
  logging + the try/except ladder.
- `src/apps/<domain>/routers/<persona>_<resource>_router.py` — thin routes, guards, rate limits.
- `--with-model` → `models/<resource>_model.py`; `--with-service` → `services/<resource>/…`.
- `--wire` → inserts the model into `ORM_MODELS` and the router include into `views/<domain>.py`.

Then: `aerich migrate --name "add_<resource>_table" && aerich upgrade`. See
[references/generating-resources.md](references/generating-resources.md) for flags and the
manual (no-script) path.

## Designing before generating
For anything beyond CRUD (filtering, sorting, custom actions, idempotency, bulk ops,
sub-resources), design the surface first — see
[references/designing-endpoints.md](references/designing-endpoints.md) — then generate the
CRUD skeleton and extend it. Don't invent a URL shape or envelope; if a case isn't covered by
`../_shared-backend/`, raise it (per `dev-partner`) rather than guessing.

## After generating
1. Fill the schema fields (replace the `TODO`s) and the model fields.
2. Add any non-CRUD routes/controller methods.
3. Confirm the routes appear in `/<domain>/docs` and the list endpoint returns the canonical
   pagination envelope.
