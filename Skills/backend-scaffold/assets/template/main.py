"""
FastAPI application entry point.
Builds the app via a factory, wires middleware, mounts the three sub-apps
(/users, /core, /utils), and exposes /health.
"""
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from configs import lifespan
from configs.settings import settings
from configs.rate_limiting import limiter
from src.libs.request_id import RequestIDMiddleware, install_request_id_logging


# Configure logging (stdlib logger everywhere; print() is banned)
install_request_id_logging(settings.LOG_LEVEL)
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=f"{settings.APP_NAME} — FastAPI + Tortoise ORM backend.",
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        openapi_url="/openapi.json" if settings.DEBUG else None,
        lifespan=lifespan,
    )

    # ── Middleware (add order matters; executes in reverse) ──────────────────
    cors_origins = [settings.FRONTEND_BASE_URL, "http://localhost:3000"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID", "X-RateLimit-Limit", "X-RateLimit-Remaining"],
    )
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    app.add_middleware(RequestIDMiddleware)  # outermost — tags every request

    # ── Rate limiting ────────────────────────────────────────────────────────
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # ── Routers (mounted sub-apps) ───────────────────────────────────────────
    register_routers(app)

    # ── Health check (first-run smoke test) ──────────────────────────────────
    @app.get("/health", tags=["Health"])
    async def health_check():
        checks = {}
        try:
            from tortoise import connections
            await connections.get("default").execute_query("SELECT 1")
            checks["database"] = "ok"
        except Exception as e:  # noqa: BLE001
            checks["database"] = f"error: {e}"

        try:
            import configs.lifespan as lifespan_mod  # read the LIVE client
            if lifespan_mod.redis_client:
                await lifespan_mod.redis_client.ping()
                checks["redis"] = "ok"
            else:
                checks["redis"] = "not initialized"
        except Exception as e:  # noqa: BLE001
            checks["redis"] = f"error: {e}"

        healthy = all(v == "ok" for v in checks.values())
        return {
            "status": "healthy" if healthy else "degraded",
            "version": settings.APP_VERSION,
            "checks": checks,
        }

    return app


def register_routers(app: FastAPI) -> None:
    from src.views.users import app as users_app
    from src.views.core import app as core_app
    from src.views.utils import app as utils_app

    app.mount("/users", users_app)
    app.mount("/core", core_app)
    app.mount("/utils", utils_app)


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.RELOAD,
        log_level=settings.LOG_LEVEL.lower(),
    )
