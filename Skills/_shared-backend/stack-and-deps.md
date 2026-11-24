# Stack & Dependencies

## Runtime

- **Language:** Python **3.12** (3.11 acceptable). Type hints everywhere; `str | None`
  union syntax (PEP 604).
- **Framework:** FastAPI (async). Uvicorn ASGI server. Starlette under the hood.
- **Package manager:** `pip` + `requirements.txt`. **Pin every dependency with `==`.**
  No Poetry, no uv, no Pipenv. `pyproject.toml` exists **only** to hold `[tool.aerich]`.
- **Everything is async** — Tortoise ORM is async, all route handlers and controller
  methods are `async def`.

## Always-installed core set

Every new project starts with this dependency set (versions are the current pinned floor;
bump together, keep FastAPI/Tortoise/pydantic compatible):

```
# Web
fastapi
uvicorn
starlette
python-multipart          # form/file uploads
gunicorn                  # optional prod process manager (bare-metal uvicorn is default)

# ORM + DB
tortoise-orm
aerich                    # migrations
pypika-tortoise
asyncpg
psycopg[binary,pool]

# Config / validation
pydantic
pydantic-settings
python-dotenv

# Cache / rate limit / jobs
redis
slowapi
limits
APScheduler               # background jobs (NOT Celery)

# Auth
bcrypt
python-jose               # JWT — the ONLY jwt lib. Do NOT add PyJWT.

# Email / templates / storage
resend
Jinja2
boto3                     # DigitalOcean Spaces (S3-compatible)

# Utility
httpx
requests
pandas
numpy
reportlab                 # PDF generation
sentry-sdk                # error monitoring (init only when SENTRY_DSN set)
```

## Project-specific dependencies (add only when the product needs them)

| Dependency | When |
|------------|------|
| `exponent_server_sdk` | Expo push notifications (mobile apps) |
| SMS provider SDK (e.g. Moolre HTTP) | SMS/OTP delivery |
| `stripe` | card payments |
| `pyotp`, `qrcode` | TOTP 2FA |
| `langchain*`, `openai` | AI / RAG features |
| `supabase`, `realtime` | Supabase integration |
| `aiomysql`, `pyodbc`, `PyMySQL`, `openpyxl` | multi-DB data connectors / spreadsheets |
| SumSub / KYC SDKs | identity verification (fintech) |

## Rule

> When adding a dependency, pin it in `requirements.txt` and confirm it's compatible with
> the FastAPI / Tortoise / pydantic majors already present. Never import a JWT library
> other than `python-jose`; never import a scheduler other than APScheduler.
