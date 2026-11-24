"""
Application Settings using Pydantic Settings.
All configuration is loaded from environment variables with .env support.
UPPER_CASE field names double as the env var names (case_sensitive=False).
"""
from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ──────────────────────────────────────────────────────────
    APP_NAME: str = Field(default="App API", description="Application name")
    APP_VERSION: str = Field(default="1.0.0", description="Application version")
    DEBUG: bool = Field(default=False, description="Debug mode (enables docs)")
    RELOAD: bool = Field(default=False, description="Auto-reload for development")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    API_PREFIX: str = Field(default="/api/v1", description="Version prefix")

    # ── Database (PostgreSQL) ────────────────────────────────────────────────
    DATABASE_URL: str = Field(
        default="postgres://app:app_password@localhost:5432/app_dev",
        description="Database connection string",
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
    JWT_ISSUER: str = Field(default="app-api")
    JWT_AUDIENCE: str = Field(default="app-frontend")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60, description="Access token TTL (min)")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=30, description="Refresh token TTL (days)")

    # ── Frontend ─────────────────────────────────────────────────────────────
    FRONTEND_BASE_URL: str = Field(default="http://localhost:3000")

    # ── Email (Resend) ───────────────────────────────────────────────────────
    MAIL_API_KEY: str = Field(default="", description="Resend API key")
    MAIL_FROM: str = Field(default="noreply@example.com")
    MAIL_FROM_NAME: str = Field(default="App")

    # ── Cloud Storage (DigitalOcean Spaces) ──────────────────────────────────
    BUCKET_URL: str = Field(default="")
    BUCKET_KEY: str = Field(default="")
    BUCKET_SECRET: str = Field(default="")
    BUCKET_NAME: str = Field(default="")
    BUCKET_REGION_ENDPOINT: str = Field(default="https://lon1.digitaloceanspaces.com")

    # ── Rate limiting ────────────────────────────────────────────────────────
    RATE_LIMIT_ENABLED: bool = Field(default=True)
    RATE_LIMIT_DEFAULT: str = Field(default="100/minute")

    # ── Monitoring ───────────────────────────────────────────────────────────
    SENTRY_DSN: Optional[str] = Field(default=None, description="Sentry DSN (init only if set)")

    # ── Seeder ───────────────────────────────────────────────────────────────
    SEED_ADMIN_EMAIL: str = Field(default="admin@example.com")
    SEED_ADMIN_PASSWORD: str = Field(default="ChangeMe123")

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
