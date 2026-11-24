"""
Utils/platform router. Final paths: /utils/api/v1/platform/...
"""
from fastapi import APIRouter

router = APIRouter(prefix="/platform", tags=["Platform"])


@router.get("/ping")
async def ping():
    """Liveness ping for the utils sub-app."""
    return {"message": "pong"}
