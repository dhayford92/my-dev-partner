"""
Client auth router. Final paths: /users/api/v1/client/auth/...
"""
from fastapi import APIRouter, Request

from configs.rate_limiting import limiter, RateLimitConfig
from src.libs.auth import CurrentClientUser
from src.schemas.shared.token import RefreshRequest, TokenResponse
from src.schemas.users.auth_schemas import RegisterSchema, LoginSchema, AuthResponse
from src.apps.users.controllers.client_auth_controller import ClientAuthController

router = APIRouter(prefix="/client/auth", tags=["Client Auth"])


@router.post("/register", response_model=AuthResponse, status_code=201)
@limiter.limit(RateLimitConfig.REGISTER)
async def register(request: Request, body: RegisterSchema):
    """Register a new client and return tokens."""
    return await ClientAuthController.register(body)


@router.post("/login", response_model=AuthResponse)
@limiter.limit(RateLimitConfig.LOGIN)
async def login(request: Request, body: LoginSchema):
    """Authenticate a client and return tokens."""
    return await ClientAuthController.login(body)


@router.post("/refresh", response_model=TokenResponse)
@limiter.limit(RateLimitConfig.REFRESH_TOKEN)
async def refresh_token(request: Request, body: RefreshRequest):
    """Refresh an access token."""
    return await ClientAuthController.refresh_token(body)


@router.post("/logout")
async def logout(auth: CurrentClientUser):
    """Invalidate the current access token."""
    return await ClientAuthController.logout(auth.jti)
