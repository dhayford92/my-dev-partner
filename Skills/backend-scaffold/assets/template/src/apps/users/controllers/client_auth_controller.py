"""
Client auth controller — register, login, refresh, logout (email + password).
"""
import logging
import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status

from src.apps.users.models.client_model import ClientModel
from src.apps.users.models.user_enum import UserType, AccountStatus
from src.schemas.shared.base import ErrorCodes
from src.schemas.shared.responses import SuccessResponse
from src.schemas.shared.token import RefreshRequest, TokenResponse
from src.schemas.users.auth_schemas import RegisterSchema, LoginSchema, AuthResponse, UserResponse
from src.services.auth import JWTService, PasswordService, token_denylist

logger = logging.getLogger(__name__)


class ClientAuthController:
    @staticmethod
    async def register(body: RegisterSchema) -> AuthResponse:
        try:
            ok, msg = PasswordService.is_password_strong(body.password)
            if not ok:
                raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=msg,
                                    headers={"X-Error-Code": ErrorCodes.WEAK_PASSWORD})

            if await ClientModel.get_or_none(email=body.email).only("id"):
                raise HTTPException(status.HTTP_409_CONFLICT, detail="Email already in use",
                                    headers={"X-Error-Code": ErrorCodes.EMAIL_IN_USE})

            user = await ClientModel.create(
                full_name=body.full_name,
                email=body.email,
                password_hashed=PasswordService.hash_password(body.password),
                status=AccountStatus.ACTIVE,
            )
            return ClientAuthController._issue(user)
        except HTTPException:
            raise
        except Exception as e:  # noqa: BLE001
            logger.error(f"Client register error: {e}")
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Registration failed")

    @staticmethod
    async def login(body: LoginSchema) -> AuthResponse:
        try:
            user = await ClientModel.get_or_none(email=body.email)
            if not user or not PasswordService.verify_password(body.password, user.password_hashed):
                raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials",
                                    headers={"X-Error-Code": ErrorCodes.AUTH_INVALID_CREDENTIALS})
            if user.status != AccountStatus.ACTIVE or user.deleted_at:
                raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Account is not active",
                                    headers={"X-Error-Code": ErrorCodes.ACCOUNT_BLOCKED})

            user.last_login_at = datetime.now(timezone.utc)
            await user.save(update_fields=["last_login_at"])
            return ClientAuthController._issue(user)
        except HTTPException:
            raise
        except Exception as e:  # noqa: BLE001
            logger.error(f"Client login error: {e}")
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Login failed")

    @staticmethod
    async def refresh_token(body: RefreshRequest) -> TokenResponse:
        try:
            payload = JWTService.verify_token(body.refresh_token, token_type="refresh")
            user_id = uuid.UUID(payload["sub"])
            if await token_denylist.is_denied(payload.get("jti")):
                raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Token has been revoked")

            user = await ClientModel.get_or_none(id=user_id)
            if not user or user.deleted_at or user.status != AccountStatus.ACTIVE:
                raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")

            access, _, exp = JWTService.create_access_token(
                user_id=user.id, user_type=UserType.CLIENT,
                additional_claims={"email": user.email},
            )
            return TokenResponse(access_token=access, refresh_token=None,
                                 expires_in=int((exp - datetime.now(timezone.utc)).total_seconds()))
        except HTTPException:
            raise
        except Exception as e:  # noqa: BLE001
            logger.error(f"Client refresh error: {e}")
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Failed to refresh token")

    @staticmethod
    async def logout(jti: str) -> SuccessResponse:
        try:
            await token_denylist.add_to_denylist(jti)
            return SuccessResponse(message="Logged out successfully")
        except Exception as e:  # noqa: BLE001
            logger.error(f"Client logout error: {e}")
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Logout failed")

    # ── helpers ──────────────────────────────────────────────────────────────
    @staticmethod
    def _issue(user: ClientModel) -> AuthResponse:
        access, _, exp = JWTService.create_access_token(
            user_id=user.id, user_type=UserType.CLIENT, additional_claims={"email": user.email})
        refresh, _, _ = JWTService.create_refresh_token(user_id=user.id, user_type=UserType.CLIENT)
        return AuthResponse(
            access_token=access, refresh_token=refresh,
            expires_in=int((exp - datetime.now(timezone.utc)).total_seconds()),
            user=UserResponse(id=user.id, full_name=user.full_name,
                              email=user.email, is_verified=user.is_verified),
        )
