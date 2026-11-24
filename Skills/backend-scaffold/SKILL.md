---
name: backend-scaffold
description: >-
  Bootstrap a brand-new backend project in Denzel's canonical FastAPI + Tortoise ORM +
  PostgreSQL stack — full folder tree, pinned dependencies, pydantic-settings config, CORS +
  gzip + rate-limiting + request-id middleware, JWT/bcrypt auth module, admin & client user
  models, roles & permissions tables with a seeder, activity logging, Resend email, DO Spaces
  storage, APScheduler, Docker dev infra, and .env files. Ships as runnable scripts +
  asset templates that produce a project which BOOTS and passes /health on first run. USE
  THIS whenever starting a new API/service/backend from scratch, creating a new repo,
  "spinning up", "bootstrapping", "scaffolding", or "setting up" a new FastAPI/Tortoise
  project, or when an empty/near-empty project needs the standard skeleton. Do NOT use it to
  add a feature to an existing project (use backend-api-design / backend-database instead).
---

# backend-scaffold

Bootstrap a new project that matches the canonical conventions exactly and boots on first
run. **All conventions live in `../_shared-backend/`** — this skill is the runnable delivery of them.

## When to use
- Starting a new backend/API/service from scratch.
- Creating a new repo that should match the same structure and conventions as your other services.
- Turning an empty directory into a bootable FastAPI + Tortoise skeleton.

Not for adding endpoints/models to an existing project — that's `backend-api-design` and
`backend-database`.

## What you produce
A complete project (see [references/whats-generated.md](references/whats-generated.md) for the
file-by-file map) that includes:

- `configs/` — `settings.py` (pydantic-settings, UPPER_CASE), `database.py`, `lifespan.py`
  (db + Redis + APScheduler + optional Sentry), `rate_limiting.py`.
- `main.py` — app factory, CORS + GZip + **RequestID** middleware, SlowAPI, mounts
  `/users` `/core` `/utils`, `/health`.
- Auth module — `JWTService`, `PasswordService`, `token_denylist`, guards in `libs/auth.py`,
  working **client register/login/refresh/logout** and **admin login/refresh/logout**.
- Models — `AdminModel`, `ClientModel`, `RoleModel` (RBAC, seeded), `ActivityLog`,
  `Notification`, and a deletable `ExampleModel` demonstrating the full CRUD stack.
- Services — email (Resend + Jinja2), storage (DO Spaces), activity logging (with PII
  redaction).
- `libs/` — `redaction.py` (PII) and `request_id.py` (real `X-Request-ID`).
- `scripts/seed.py` — default roles + super admin (idempotent).
- `.env.example`, `.gitignore`, `docker-compose.dev.yml` (Postgres + Redis), `README.md`.

## How to run it

**Windows (native, fully automated — recommended):**
```powershell
# from the skill's scripts/ folder
.\scaffold.ps1 -Name "My API" -Path "D:\Main\Desktop\API Systems\my-api"
```
`scaffold.ps1` copies the template, sets `APP_NAME`, creates the venv, installs deps, starts
Postgres+Redis via Docker (if present), runs `aerich init` + `init-db`, seeds, boots uvicorn,
and asserts `/health` returns `{"status":"healthy"}`. It fails loudly if health isn't green.

**Cross-platform (copy + guided steps):**
```bash
python scaffold.py --name "My API" --path /abs/target/my-api
```
`scaffold.py` copies + configures, then prints the venv/install/migrate/seed/run steps
(equivalent manual flow). Use `scaffold.ps1` for the automated verification on Windows.

## First-run contract (must be green)
After scaffolding, `GET http://localhost:8000/health` returns:
```json
{ "status": "healthy", "version": "1.0.0", "checks": { "database": "ok", "redis": "ok" } }
```
If it's `degraded`, see [references/first-run-troubleshooting.md](references/first-run-troubleshooting.md)
— it's almost always Postgres/Redis not reachable or `.env` not filled.

## After scaffolding
1. Confirm `/docs` renders for each sub-app (`/users/docs`, `/core/docs`, `/utils/docs`).
2. Try the example flow: register a client, log in, hit `/core/api/v1/admin/examples`.
3. **Delete the `example` resource** and add real domains with `backend-api-design` +
   `backend-database`. See [references/adding-a-domain.md](references/adding-a-domain.md).

## Conventions this skill encodes
Every generated file follows `../_shared-backend/`. Do not diverge; if a convention needs changing,
edit `../_shared-backend/` and re-generate. Key references:
- Structure & sub-app assembly → [../_shared-backend/structure.md](../_shared-backend/structure.md)
- Config → [../_shared-backend/config.md](../_shared-backend/config.md)
- Auth → [../_shared-backend/auth.md](../_shared-backend/auth.md)
- Response/errors → [../_shared-backend/response-contract.md](../_shared-backend/response-contract.md)
- Logging (redaction, request-id) → [../_shared-backend/logging.md](../_shared-backend/logging.md)
- Email/jobs/storage → [../_shared-backend/email-jobs-storage.md](../_shared-backend/email-jobs-storage.md)

## Customisation knobs
- **Authz model** — the template ships persona guards + a seeded relational RBAC. For JSON
  framework/action RBAC or team+RLS multi-tenancy, layer on `backend-auth` after scaffolding
  (those are opt-in per project). See [../_shared-backend/auth.md](../_shared-backend/auth.md).
- **Abstract base model** — template uses inline timestamps (matches existing repos). To
  switch to a `TimestampedModel` base, see [../_shared-backend/database.md](../_shared-backend/database.md).
- **SQLite first boot** — set `DATABASE_URL=sqlite://db.sqlite3` in `.env` to boot with zero
  DB infra (redis still needed for auth; health will show redis status).
