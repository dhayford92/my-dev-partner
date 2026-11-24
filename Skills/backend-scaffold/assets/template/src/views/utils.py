"""
Utils sub-app — mounted at /utils. Routers included with the /api/v1 prefix.
"""
from fastapi import FastAPI

from configs.settings import settings

app = FastAPI(
    title=f"{settings.APP_NAME} | Utils",
    version=settings.APP_VERSION,
    description="Notifications, activity log, platform settings",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/",
    openapi_url="/openapi.json" if settings.DEBUG else None,
)

API_V1 = settings.API_PREFIX

from src.apps.utils.routers.platform_router import router as platform_router

app.include_router(platform_router, prefix=API_V1)
