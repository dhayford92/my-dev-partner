# `./` — Canonical Backend Conventions (Single Source of Truth)

This folder is the **one place** where the conventions for Denzel's FastAPI + Tortoise
backend stack are written down. Every skill under `D:\Main\Desktop\Skills\` points here
instead of restating conventions. When a convention changes, edit it **here** and every
skill inherits the change.

> These conventions were extracted from several production backends and reconciled by the
> owner. Where they disagreed, the owner picked one canonical variant; the losing variants are recorded as
> "❌ not this" so skills never regenerate them.

## Files

| File | Covers |
|------|--------|
| [stack-and-deps.md](stack-and-deps.md) | Runtime, framework, package manager, always-installed dependency set |
| [structure.md](structure.md) | Folder tree, sub-app assembly, what goes where |
| [config.md](config.md) | `pydantic-settings`, UPPER_CASE fields, `.env`, boot validation |
| [routing.md](routing.md) | Route organisation, `/api/v1` + persona prefixes, versioning, thin routers |
| [controllers-services.md](controllers-services.md) | Controller/service split, static-method classes, transactions, error ladder |
| [database.md](database.md) | Tortoise models, UUID PK, timestamps, soft delete, enums, Aerich migrations |
| [auth.md](auth.md) | JWT (python-jose), bcrypt, denylist, guards, persona/RBAC/team authz |
| [response-contract.md](response-contract.md) | Success/error/pagination envelopes, status codes, validation, `ErrorCodes` |
| [logging.md](logging.md) | Dev logging (`logger`, Sentry) + admin activity logging + PII redaction + `X-Request-ID` |
| [email-jobs-storage.md](email-jobs-storage.md) | Resend email, Jinja2 templates, APScheduler jobs, DigitalOcean Spaces storage |
| [code-style.md](code-style.md) | Naming, schema taxonomy, imports, helper placement, general style |

## Two generations (historical context, not a convention)

The source backends fell into a newer and an older generation. The canonical set below follows
the **newer architecture with UPPER_CASE setting names**:

- **Newer:** `pydantic-settings`, `create_app()` factory, `logger` discipline.
- **Older:** `os.environ` settings, module-level `app`, more `print()`.

## Canonical decisions at a glance

| Area | Canonical | ❌ Not this |
|------|-----------|-------------|
| Config | `pydantic-settings` + **UPPER_CASE** typed `Field`s + `lru_cache` | plain `os.environ` class; snake_case fields |
| Controllers dir | `controllers/` (plural) | `controller/` |
| Schemas | subfolder `schemas/{domain}/` | flat `schemas/{resource}_schema.py` |
| Route path | `/{domain}` mount → `/api/v1/{persona}/{feature}` | omitting `/api/v1` |
| Access token | 60 min, HS256, **python-jose** | 15 min; PyJWT |
| Refresh | stateless + Redis denylist | DB session table (unless project needs it) |
| Authz default | `user_type` persona guards | (RBAC / team-RLS are opt-in modules) |
| Pagination | `{data, current_page, page_limit, total_count}` | `{items,...}`; `{data,total,limit,page}` |
| Errors | raise `HTTPException(status_code, detail, headers?)` → default `{detail}`; machine codes via `X-Error-Code` header | global handlers + `{error:{...}}` envelope |
| Jobs | APScheduler | Celery |
| Logging | stdlib `logger` everywhere; `print()` banned | `print("[ERROR] ...")` |
| Email | Resend + Jinja2 via `BackgroundTasks` | — |
| Storage | boto3 → DigitalOcean Spaces | — |
| Deploy | bare-metal `uvicorn` | (Docker/CI optional add-ons) |

## Additions the owner requested (not in the repos yet)

These two are **new** — they don't exist in the four repos and skills should introduce
them as improvements, not "reproductions":

1. **PII redaction** in logs and activity metadata (phones, emails, tokens). See
   [logging.md](logging.md).
2. **Real `X-Request-ID`** correlation IDs (middleware that generates + logs them). Today
   the header is only CORS-exposed but never populated. See [logging.md](logging.md).
