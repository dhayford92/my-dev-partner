"""
Users sub-app — mounted at /users. Routers included with the /api/v1 prefix.
"""
from fastapi import FastAPI

from configs.settings import settings

app = FastAPI(
    title=f"{settings.APP_NAME} | Users",
    version=settings.APP_VERSION,
    description="Authentication & user management",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/",
    openapi_url="/openapi.json" if settings.DEBUG else None,
)

API_V1 = settings.API_PREFIX  # "/api/v1"

from src.apps.users.routers.client_auth_router import router as client_auth_router
from src.apps.users.routers.admin_auth_router import router as admin_auth_router

app.include_router(client_auth_router, prefix=API_V1)
app.include_router(admin_auth_router, prefix=API_V1)
