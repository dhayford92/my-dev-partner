# {{APP_NAME}}

FastAPI + Tortoise ORM backend. Bootstrapped by the `backend-scaffold` skill.

## Stack
FastAPI · Tortoise ORM + Aerich · PostgreSQL · Redis · APScheduler · SlowAPI · python-jose ·
bcrypt · Resend · boto3 (DigitalOcean Spaces).

## First run (Windows / PowerShell)

```powershell
# 1. Virtualenv + deps
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 2. Config
Copy-Item .env.example .env      # then edit secrets

# 3. Infra (Postgres + Redis) — via Docker, or point .env at your own
docker compose -f docker-compose.dev.yml up -d

# 4. Migrations
aerich init -t configs.database.tortoise_config
aerich init-db

# 5. Seed default roles + super admin
python -m scripts.seed

# 6. Run
uvicorn main:app --reload
```

Then check **http://localhost:8000/health** → `{"status":"healthy", ...}`.

## URL shape
`/{domain}/api/v1/{persona}/{feature}` — e.g. `POST /users/api/v1/client/auth/login`,
`GET /core/api/v1/admin/examples`.

## Layout
- `configs/` — settings, database, lifespan, rate limiting
- `src/apps/{users,core,utils}/` — models, controllers, routers
- `src/schemas/` — pydantic (per-domain subfolders)
- `src/services/` — auth, email, storage, activity
- `src/libs/` — auth guards, generators, redaction, request-id
- `src/views/` — the three mounted sub-apps

## Next steps
Delete the `example` resource (`src/apps/core/models/example_model.py`,
`src/schemas/core/example_schemas.py`, `example_controller.py`, `example_router.py`, its
`ORM_MODELS` entry and its include in `src/views/core.py`) and add your real domains — use the
`backend-api-design` and `backend-database` skills.
