"""
Admin portal access control (opt-in). Drop into src/libs/ alongside auth.py.

The admin portal is a SEPARATE auth surface from the platform. Portal JWTs carry a
`portal: true` claim plus a `role` (admin | finance | user). Portal routes have NO tenant/team
scope. This is the portal-token model.

Issue a portal token with:
    JWTService.create_access_token(
        user_id=portal_user.id, type="access",
        additional_claims={"portal": True, "email": ..., "role": portal_user.role})

Requires a PortalUserModel (portal_users) with a `role` field.
"""
import logging
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError

from src.services.auth import JWTService, token_denylist

logger = logging.getLogger(__name__)

portal_security = HTTPBearer(auto_error=False)


class PortalAuthContext:
    def __init__(self, user_id: UUID, email: str | None, role: str | None, jti: str | None):
        self.user_id = user_id
        self.email = email
        self.role = role
        self.jti = jti

    @property
    def id(self) -> UUID:
        return self.user_id


async def get_portal_user(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(portal_security)],
) -> PortalAuthContext:
    if not credentials:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Missing authorization header",
                            headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = JWTService.verify_token(credentials.credentials, token_type="access")
        if not payload.get("portal"):
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Not a portal token")
        user_id = UUID(payload["sub"])
        jti = payload.get("jti")
        if jti and await token_denylist.is_denied(jti):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Token has been revoked")
        return PortalAuthContext(user_id, payload.get("email"), payload.get("role"), jti)
    except JWTError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token",
                            headers={"WWW-Authenticate": "Bearer"})


async def get_portal_admin(auth: Annotated[PortalAuthContext, Depends(get_portal_user)]) -> PortalAuthContext:
    if auth.role != "admin":
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Portal admin role required")
    return auth


async def get_portal_finance_or_admin(
    auth: Annotated[PortalAuthContext, Depends(get_portal_user)],
) -> PortalAuthContext:
    if auth.role not in ("finance", "admin"):
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Portal finance or admin role required")
    return auth


# Type aliases
PortalUser = Annotated[PortalAuthContext, Depends(get_portal_user)]
PortalAdmin = Annotated[PortalAuthContext, Depends(get_portal_admin)]
PortalFinanceOrAdmin = Annotated[PortalAuthContext, Depends(get_portal_finance_or_admin)]
