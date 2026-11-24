# Configuration

## Canonical: `pydantic-settings` machinery + UPPER_CASE field names

This is a deliberate blend of the two repo clusters: the **validated `pydantic-settings`
machinery** (`pydantic-settings`, app factory), with the **UPPER_CASE naming** (the
owner's most-correct repos). `case_sensitive=False` makes each UPPER_CASE field read the
identically-named env var.

`configs/settings.py`:

```python
"""
Application Settings using Pydantic Settings.
All configuration is loaded from environment variables with .env support.
"""
from functools import lru_cache
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,     # API_SECRET_KEY field <-> API_SECRET_KEY env var
        extra="ignore",
    )

    # ── Application ──────────────────────────────────────────────────────────
    APP_NAME: str = Field(default="Example API", description="Application name")
    APP_VERSION: str = Field(default="1.0.0", description="Application version")
    DEBUG: bool = Field(default=False, description="Debug mode (enables docs)")
    RELOAD: bool = Field(default=False, description="Auto-reload for development")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    API_PREFIX: str = Field(default="/api/v1", description="Version prefix")

    # ── Database (PostgreSQL) ────────────────────────────────────────────────
    DATABASE_URL: str = Field(
        default="postgres://user:pass@localhost:5432/app_dev",
        description="PostgreSQL connection string",
    )
    DATABASE_POOL_SIZE: int = Field(default=20)
    DATABASE_POOL_MAX_OVERFLOW: int = Field(default=10)

    # ── Redis ────────────────────────────────────────────────────────────────
    REDIS_URL: str = Field(default="redis://localhost:6379/0")
    REDIS_MAX_CONNECTIONS: int = Field(default=50)

    # ── JWT ──────────────────────────────────────────────────────────────────
    API_SECRET_KEY: str = Field(default="change-me-in-production",
                                description="JWT signing secret (256-bit hex)")
    API_ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    JWT_ISSUER: str = Field(default="example-api")
    JWT_AUDIENCE: str = Field(default="example-frontend")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60, description="Access token TTL (min)")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=30, description="Refresh token TTL (days)")

    # ── Frontend ─────────────────────────────────────────────────────────────
    FRONTEND_BASE_URL: str = Field(default="http://localhost:3000")

    # ── Email (Resend) ───────────────────────────────────────────────────────
    MAIL_API_KEY: str = Field(default="", description="Resend API key")
    MAIL_FROM: str = Field(default="noreply@example.com")
    MAIL_FROM_NAME: str = Field(default="Example")

    # ── Cloud Storage (DigitalOcean Spaces) ──────────────────────────────────
    BUCKET_URL: str = Field(default="")
    BUCKET_KEY: str = Field(default="")
    BUCKET_SECRET: str = Field(default="")
    BUCKET_NAME: str = Field(default="")

    # ── Rate limiting ────────────────────────────────────────────────────────
    RATE_LIMIT_ENABLED: bool = Field(default=True)
    RATE_LIMIT_DEFAULT: str = Field(default="100/minute")

    # ── Monitoring ───────────────────────────────────────────────────────────
    SENTRY_DSN: Optional[str] = Field(default=None, description="Sentry DSN (init only if set)")

    # ── Computed properties ──────────────────────────────────────────────────
    @property
    def access_token_ttl_seconds(self) -> int:
        return self.ACCESS_TOKEN_EXPIRE_MINUTES * 60

    @property
    def refresh_token_ttl_seconds(self) -> int:
        return self.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60


@lru_cache()
def get_settings() -> Settings:
    """Cached settings — loaded once per process."""
    return Settings()


settings = get_settings()
```

## Rules

1. **All config lives in `settings.py`.** Reference `settings.X` everywhere — never scatter
   `os.getenv(...)` through the codebase.
2. **Add new config as a typed `Field` with a `description`.** The description is the
   documentation; there is no separate config doc.
3. **UPPER_CASE field names.** They double as the env var names.
4. **Secrets come from `.env`** (gitignored). Commit a `.env.example` with empty/placeholder
   values and every key present. Never commit real secrets.
5. **One `.env` per environment** — no per-env override files. The deployment supplies the
   right `.env`.
6. `Optional[...]` + `default=None` for anything that legitimately may be absent (e.g.
   `SENTRY_DSN`); everything else gets a safe default so boot never crashes on a missing var.

## ❌ Not this

```python
# OLD style — do not generate. No validation, no types, crashes late on missing vars.
class Settings:
    load_dotenv()
    API_SECRET_KEY = os.environ.get("API_SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", 15))
settings = Settings()
```

## `.env.example` shape

```dotenv
APP_NAME=Example API
DEBUG=false
DATABASE_URL=postgres://user:pass@localhost:5432/app_dev
REDIS_URL=redis://localhost:6379/0
API_SECRET_KEY=
API_ALGORITHM=HS256
JWT_ISSUER=example-api
JWT_AUDIENCE=example-frontend
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=30
MAIL_API_KEY=
MAIL_FROM=noreply@example.com
BUCKET_URL=
BUCKET_KEY=
BUCKET_SECRET=
BUCKET_NAME=
SENTRY_DSN=
```
