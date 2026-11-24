# Folder Structure

## Canonical tree

```
<project>-api/
├── main.py                     # FastAPI factory + mounts sub-apps at /users /core /utils
├── requirements.txt            # pinned deps
├── pyproject.toml              # ONLY [tool.aerich]
├── .env                        # gitignored secrets
├── .env.example                # committed template
├── configs/
│   ├── __init__.py             # re-exports settings, lifespan, redis_client
│   ├── settings.py             # pydantic-settings (see config.md)
│   ├── database.py             # Tortoise config + ORM_MODELS list
│   ├── lifespan.py             # startup/shutdown: db, redis, APScheduler
│   ├── rate_limiting.py        # SlowAPI limiter + RateLimitConfig constants
│   └── redis_configs.py        # (optional) redis client module
├── migrations/
│   └── models/                 # aerich raw-SQL migrations: NN_timestamp_name.py
└── src/
    ├── apps/
    │   ├── core/               # main domain resources
    │   │   ├── models/         # Tortoise models: <resource>_model.py
    │   │   ├── controllers/    # business logic: <resource>_controller.py  (PLURAL dir)
    │   │   └── routers/        # APIRouters: <persona>_<feature>_router.py
    │   ├── users/              # auth, profiles, admin/portal users
    │   │   ├── models/
    │   │   ├── controllers/
    │   │   └── routers/
    │   └── utils/              # notifications, activity log, platform settings
    │       ├── models/
    │       ├── controllers/
    │       └── routers/
    ├── schemas/                # pydantic — SUBFOLDER per domain
    │   ├── core/
    │   ├── users/
    │   ├── utils/
    │   └── shared/             # responses.py, token.py, base schemas
    ├── services/               # reusable domain capabilities (see below)
    ├── libs/                   # cross-cutting: auth.py, generators.py, redaction.py, request_id.py, formatters.py
    ├── templates/              # Jinja2 email HTML + logo.png
    └── views/                  # one sub-FastAPI app per domain: users.py, core.py, utils.py
```

## The three-tier app split

Every project mounts exactly three sub-apps in `main.py`:

- `/users` — authentication, profiles, admin/portal user management.
- `/core` — the product's primary domain resources.
- `/utils` — notifications, activity log, platform settings, health-ish extras.

## Sub-app assembly — `src/views/<domain>.py`

Each `views/<domain>.py` builds a standalone `FastAPI` sub-app and includes that domain's
routers **with the `/api/v1` prefix applied at include time**. This is where versioning is
injected. Real example (`src/views/users.py`):

```python
from fastapi import FastAPI
from configs.settings import settings

app = FastAPI(
    title=f"{settings.APP_NAME} | Users Management",
    version=settings.APP_VERSION,
    description="Users Management",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/",
    openapi_url="/openapi.json" if settings.DEBUG else None,
)

# API version prefix — injected here
API_V1 = "/api/v1"

from src.apps.users.routers.client_auth_router import router as client_auth_router
from src.apps.users.routers.client_auth_router import profile_router as client_profile_router
from src.apps.users.routers.admin_auth_router import router as admin_auth_router

app.include_router(client_auth_router, prefix=API_V1)
app.include_router(client_profile_router, prefix=API_V1)
app.include_router(admin_auth_router, prefix=API_V1)
```

`main.py` then mounts each sub-app:

```python
app.mount("/users", users_app)
app.mount("/core", core_app)
app.mount("/utils", utils_app)
```

Final URL = mount + include-prefix + router-prefix. See [routing.md](routing.md).

## What belongs where

| Directory | Holds | Never holds |
|-----------|-------|-------------|
| `apps/<domain>/models/` | Tortoise ORM models, one resource per file | business logic |
| `apps/<domain>/controllers/` | static-method classes, all business logic | route decorators |
| `apps/<domain>/routers/` | thin `APIRouter`s delegating to controllers | DB queries, logic |
| `schemas/<domain>/` | pydantic request/response models | ORM models |
| `services/` | reusable capabilities used by many controllers | route/HTTP concerns (mostly) |
| `libs/` | cross-cutting: auth guards, generators, exception handlers, formatters | domain logic |
| `templates/` | Jinja2 email HTML | code |
| `views/` | sub-app assembly only | logic |
| `configs/` | settings, db, lifespan, rate limiting | domain code |

## `services/` layout

Services are grouped by capability, each as a package:

```
services/
├── auth/          jwt_service.py, password_service.py, token_denylist.py, otp_service.py
├── email/         email_service.py
├── storage/       storage_service.py
├── activity/      activity_service.py
├── notification/  notification_service.py
└── <domain>/      <name>_service.py   # e.g. payment/, referral/, subscription/, sms/, sse/
```

A service is either a class of `@staticmethod`s (`JWTService`) or a module-level singleton
instance (`storage_service = StorageService()`, `token_denylist = TokenDenylistService()`,
`activity_service = ActivityService()`).

## Naming

- Model files: `<resource>_model.py` → class `<Resource>Model`.
- Controller files: `<resource>_controller.py` → class `<Resource>Controller`.
- Router files: `<persona>_<feature>_router.py` (e.g. `client_auth_router.py`).
- Service files: `<name>_service.py` → class `<Name>Service`.
- Absolute imports from the `src.` prefix everywhere.
