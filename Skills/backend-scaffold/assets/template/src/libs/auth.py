"""
Authentication dependencies (guards). Routers import the type aliases at the bottom.
"""
import logging
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError

from src.apps.users.models.admin_models import AdminModel
from src.apps.users.models.user_enum import AdminRole
from src.services.auth import JWTService, token_denylist

logger = logging.getLogger(__name__)

security = HTTPBearer(auto_error=False)


class AuthContext:
    """Current-user context populated by the auth dependency."""
    def __init__(self, user_id: UUID, user_type: str | None = None,
                 email: str | None = None, jti: str | None = None):
        self.user_id = user_id
        self.user_type = user_type
        self.email = email
        self.jti = jti

    @property
    def id(self) -> UUID:
        return self.user_id


async def get_current_user(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
) -> AuthContext:
    if not credentials:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Missing authorization header",
                            headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = JWTService.verify_token(credentials.credentials, token_type="access")
        user_id = UUID(payload["sub"])
        jti = payload.get("jti")
        if jti and await token_denylist.is_denied(jti):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Token has been revoked",
                                headers={"WWW-Authenticate": "Bearer"})
        if await token_denylist.is_user_denied(user_id):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Session invalidated",
                                headers={"WWW-Authenticate": "Bearer"})
        return AuthContext(
            user_id=user_id,
            user_type=payload.get("user_type"),
            email=payload.get("email"),
            jti=jti,
        )
    except JWTError as e:
        logger.warning(f"JWT verification failed: {e}")
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token",
                            headers={"WWW-Authenticate": "Bearer"})


async def get_current_client_user(
    auth: Annotated[AuthContext, Depends(get_current_user)],
) -> AuthContext:
    if auth.user_type != "client":
        raise HTTPException(status.HTTP_403_FORBIDDEN,
                            detail="Invalid user type. Expected 'client'.")
    return auth


async def get_current_admin_user(
    auth: Annotated[AuthContext, Depends(get_current_user)],
) -> AuthContext:
    if auth.user_type != "admin":
        raise HTTPException(status.HTTP_403_FORBIDDEN,
                            detail="Invalid user type. Expected 'admin'.")
    return auth


async def get_current_super_admin_user(
    auth: Annotated[AuthContext, Depends(get_current_admin_user)],
) -> AuthContext:
    user = await AdminModel.get_or_none(id=auth.user_id).only("id", "role")
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")
    if user.role != AdminRole.SUPER_ADMIN:
        raise HTTPException(status.HTTP_403_FORBIDDEN,
                            detail="User does not have super admin privileges.")
    return auth


# Type aliases — routers import these
CurrentUser = Annotated[AuthContext, Depends(get_current_user)]
CurrentClientUser = Annotated[AuthContext, Depends(get_current_client_user)]
CurrentAdminUser = Annotated[AuthContext, Depends(get_current_admin_user)]
CurrentSuperAdminUser = Annotated[AuthContext, Depends(get_current_super_admin_user)]
