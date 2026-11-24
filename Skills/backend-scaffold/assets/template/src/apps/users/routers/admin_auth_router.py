"""
Admin auth router. Final paths: /users/api/v1/admin/auth/...
"""
from fastapi import APIRouter, Request

from configs.rate_limiting import limiter, RateLimitConfig
from src.libs.auth import CurrentAdminUser
from src.schemas.shared.token import RefreshRequest, TokenResponse
from src.schemas.users.auth_schemas import LoginSchema, AuthResponse
from src.apps.users.controllers.admin_auth_controller import AdminAuthController

router = APIRouter(prefix="/admin/auth", tags=["Admin Auth"])


@router.post("/login", response_model=AuthResponse)
@limiter.limit(RateLimitConfig.LOGIN)
async def login(request: Request, body: LoginSchema):
    """Authenticate an admin and return tokens."""
    return await AdminAuthController.login(body)


@router.post("/refresh", response_model=TokenResponse)
@limiter.limit(RateLimitConfig.REFRESH_TOKEN)
async def refresh_token(request: Request, body: RefreshRequest):
    """Refresh an admin access token."""
    return await AdminAuthController.refresh_token(body)


@router.post("/logout")
async def logout(auth: CurrentAdminUser):
    """Invalidate the current admin access token."""
    return await AdminAuthController.logout(auth.jti)
