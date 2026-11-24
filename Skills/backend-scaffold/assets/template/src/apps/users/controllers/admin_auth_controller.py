"""
Admin auth controller — login, refresh, logout (email + password).
Admin accounts are created by the seeder / by a super admin, not by open registration.
"""
import logging
import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status

from src.apps.users.models.admin_models import AdminModel
from src.apps.users.models.user_enum import UserType, AccountStatus
from src.schemas.shared.base import ErrorCodes
from src.schemas.shared.responses import SuccessResponse
from src.schemas.shared.token import RefreshRequest, TokenResponse
from src.schemas.users.auth_schemas import LoginSchema, AuthResponse, UserResponse
from src.services.auth import JWTService, PasswordService, token_denylist

logger = logging.getLogger(__name__)


class AdminAuthController:
    @staticmethod
    async def login(body: LoginSchema) -> AuthResponse:
        try:
            admin = await AdminModel.get_or_none(email=body.email)
            if not admin or not PasswordService.verify_password(body.password, admin.password_hashed):
                raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials",
                                    headers={"X-Error-Code": ErrorCodes.AUTH_INVALID_CREDENTIALS})
            if admin.status != AccountStatus.ACTIVE or admin.deleted_at:
                raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Account is not active",
                                    headers={"X-Error-Code": ErrorCodes.ACCOUNT_BLOCKED})

            admin.last_login_at = datetime.now(timezone.utc)
            await admin.save(update_fields=["last_login_at"])

            access, _, exp = JWTService.create_access_token(
                user_id=admin.id, user_type=UserType.ADMIN,
                additional_claims={"email": admin.email, "role": admin.role.value})
            refresh, _, _ = JWTService.create_refresh_token(user_id=admin.id, user_type=UserType.ADMIN)
            return AuthResponse(
                access_token=access, refresh_token=refresh,
                expires_in=int((exp - datetime.now(timezone.utc)).total_seconds()),
                user=UserResponse(id=admin.id, full_name=admin.full_name,
                                  email=admin.email, is_verified=admin.is_verified),
            )
        except HTTPException:
            raise
        except Exception as e:  # noqa: BLE001
            logger.error(f"Admin login error: {e}")
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Login failed")

    @staticmethod
    async def refresh_token(body: RefreshRequest) -> TokenResponse:
        try:
            payload = JWTService.verify_token(body.refresh_token, token_type="refresh")
            admin_id = uuid.UUID(payload["sub"])
            if await token_denylist.is_denied(payload.get("jti")):
                raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Token has been revoked")
            admin = await AdminModel.get_or_none(id=admin_id)
            if not admin or admin.deleted_at or admin.status != AccountStatus.ACTIVE:
                raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")
            access, _, exp = JWTService.create_access_token(
                user_id=admin.id, user_type=UserType.ADMIN,
                additional_claims={"email": admin.email, "role": admin.role.value})
            return TokenResponse(access_token=access, refresh_token=None,
                                 expires_in=int((exp - datetime.now(timezone.utc)).total_seconds()))
        except HTTPException:
            raise
        except Exception as e:  # noqa: BLE001
            logger.error(f"Admin refresh error: {e}")
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Failed to refresh token")

    @staticmethod
    async def logout(jti: str) -> SuccessResponse:
        try:
            await token_denylist.add_to_denylist(jti)
            return SuccessResponse(message="Logged out successfully")
        except Exception as e:  # noqa: BLE001
            logger.error(f"Admin logout error: {e}")
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Logout failed")
