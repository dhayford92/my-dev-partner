"""
Core sub-app — mounted at /core. Routers included with the /api/v1 prefix.
"""
from fastapi import FastAPI

from configs.settings import settings

app = FastAPI(
    title=f"{settings.APP_NAME} | Core",
    version=settings.APP_VERSION,
    description="Core domain resources",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/",
    openapi_url="/openapi.json" if settings.DEBUG else None,
)

API_V1 = settings.API_PREFIX

# Example resource — delete once you add real domains.
from src.apps.core.routers.example_router import router as example_router

app.include_router(example_router, prefix=API_V1)
