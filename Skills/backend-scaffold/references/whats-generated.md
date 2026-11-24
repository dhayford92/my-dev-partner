# What's generated — file-by-file map

The template lives in `assets/template/`. `scaffold.ps1` / `scaffold.py` copy it into the
target directory, replacing `APP_NAME` (and the README `{{APP_NAME}}` token).

```
<project>-api/
├── main.py                         # factory, middleware, mounts, /health
├── requirements.txt                # pinned deps (see ../../_shared-backend/stack-and-deps.md)
├── pyproject.toml                  # [tool.aerich] only
├── .env.example / .gitignore
├── docker-compose.dev.yml          # Postgres + Redis (dev infra only)
├── README.md
├── configs/
│   ├── __init__.py                 # re-exports settings, lifespan
│   ├── settings.py                 # pydantic-settings, UPPER_CASE fields
│   ├── database.py                 # tortoise_config + ORM_MODELS
│   ├── lifespan.py                 # db + redis + APScheduler + optional Sentry
│   └── rate_limiting.py            # SlowAPI limiter + RateLimitConfig
├── scripts/
│   └── seed.py                     # default roles + super admin (idempotent)
└── src/
    ├── libs/
    │   ├── auth.py                 # HTTPBearer → AuthContext → persona guards
    │   ├── generators.py           # code/reference/referral generators
    │   ├── redaction.py            # PII redaction (NEW addition)
    │   └── request_id.py           # X-Request-ID middleware + logging filter (NEW)
    ├── schemas/
    │   ├── shared/
    │   │   ├── base.py             # BaseSchema, PaginatedResponse, PaginationParams, ErrorCodes
    │   │   ├── responses.py        # SuccessResponse, DownloadResponse
    │   │   └── token.py            # TokenResponse, RefreshRequest
    │   ├── users/auth_schemas.py   # Register/Login/Auth/User schemas
    │   └── core/example_schemas.py # example naming taxonomy (delete)
    ├── services/
    │   ├── auth/                   # jwt_service, password_service, token_denylist (+ __init__ exports)
    │   ├── email/email_service.py  # Resend + Jinja2
    │   ├── storage/storage_service.py  # boto3 → DO Spaces
    │   └── activity/activity_service.py # audit trail + redaction
    ├── apps/
    │   ├── users/
    │   │   ├── models/             # admin_models, client_model, role_model, user_enum
    │   │   ├── controllers/        # client_auth_controller, admin_auth_controller
    │   │   └── routers/            # client_auth_router, admin_auth_router
    │   ├── core/
    │   │   ├── models/example_model.py
    │   │   ├── controllers/example_controller.py
    │   │   └── routers/example_router.py
    │   └── utils/
    │       ├── models/             # activity_model, notification_model
    │       └── routers/platform_router.py
    ├── templates/                  # welcome.html, email_verification.html
    └── views/                      # users.py, core.py, utils.py (sub-app assembly)
```

## Endpoints that exist immediately

| Method | Path | Auth |
|--------|------|------|
| GET | `/health` | public |
| POST | `/users/api/v1/client/auth/register` | public |
| POST | `/users/api/v1/client/auth/login` | public |
| POST | `/users/api/v1/client/auth/refresh` | public |
| POST | `/users/api/v1/client/auth/logout` | client |
| POST | `/users/api/v1/admin/auth/login` | public |
| POST | `/users/api/v1/admin/auth/refresh` | public |
| POST | `/users/api/v1/admin/auth/logout` | admin |
| GET/POST/PATCH/DELETE | `/core/api/v1/admin/examples[/{id}]` | admin |
| GET | `/utils/api/v1/platform/ping` | public |

Docs per sub-app: `/users/docs`, `/core/docs`, `/utils/docs` (when `DEBUG=true`).

## The `example` resource is a teaching artefact
`ExampleModel` + its schema/controller/router demonstrate the full stack (pagination,
soft-delete, activity logging, admin guard, naming taxonomy). Delete all of it plus the
`ORM_MODELS` entry and the `views/core.py` include once real domains exist.
