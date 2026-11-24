"""
Email verification + password reset flows (email + password auth).

Drop into src/apps/users/controllers/. These use PURPOSE-TYPED JWTs
(type="email_verification" / type="password_reset") so a token minted for one purpose can't
be replayed for another. Emails are sent via BackgroundTasks. Wire the routes in your
client_auth_router (add `background_tasks: BackgroundTasks` to those handlers).

Replace ClientModel with the target user model if verifying a different persona.
"""
import logging
from datetime import datetime, timezone

from fastapi import HTTPException, status, BackgroundTasks
from jose import JWTError

from configs.settings import settings
from src.apps.users.models.client_model import ClientModel
from src.schemas.shared.base import ErrorCodes
from src.schemas.shared.responses import SuccessResponse
from src.schemas.users.verification_reset_schemas import (
    RequestVerificationSchema, VerifyEmailSchema, ForgotPasswordSchema, ResetPasswordSchema,
)
from src.services.auth import JWTService, PasswordService, token_denylist
from src.services.email.email_service import email_service

logger = logging.getLogger(__name__)


class AccountFlowController:
    # ── Email verification ───────────────────────────────────────────────────
    @staticmethod
    async def request_verification(body: RequestVerificationSchema,
                                   background_tasks: BackgroundTasks) -> SuccessResponse:
        user = await ClientModel.get_or_none(email=body.email)
        # Do not leak whether the email exists.
        if user and not user.is_verified:
            token, _, _ = JWTService.create_access_token(
                user_id=user.id, type="email_verification",
                additional_claims={"email": user.email})
            verify_url = f"{settings.FRONTEND_BASE_URL}/verify-email?token={token}"
            background_tasks.add_task(
                email_service.send_email, to=user.email, subject="Verify your email",
                template_name="email_verification.html",
                body={"full_name": user.full_name or "there", "verify_url": verify_url})
        return SuccessResponse(message="If that email exists, a verification link was sent.")

    @staticmethod
    async def verify_email(body: VerifyEmailSchema) -> SuccessResponse:
        try:
            payload = JWTService.verify_token(body.token, token_type="email_verification")
        except JWTError:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token",
                                headers={"X-Error-Code": ErrorCodes.AUTH_INVALID_TOKEN})
        user = await ClientModel.get_or_none(id=payload["sub"])
        if not user:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")
        if not user.is_verified:
            user.is_verified = True
            await user.save(update_fields=["is_verified"])
        return SuccessResponse(message="Email verified successfully")

    # ── Password reset ─────────────────────────────────────────────────────────
    @staticmethod
    async def forgot_password(body: ForgotPasswordSchema,
                              background_tasks: BackgroundTasks) -> SuccessResponse:
        user = await ClientModel.get_or_none(email=body.email)
        if user and not user.deleted_at:
            token, _, _ = JWTService.create_access_token(
                user_id=user.id, type="password_reset",
                additional_claims={"email": user.email})
            reset_url = f"{settings.FRONTEND_BASE_URL}/reset-password?token={token}"
            background_tasks.add_task(
                email_service.send_email, to=user.email, subject="Reset your password",
                template_name="reset_password.html",
                body={"full_name": user.full_name or "there", "reset_url": reset_url})
        return SuccessResponse(message="If that email exists, a reset link was sent.")

    @staticmethod
    async def reset_password(body: ResetPasswordSchema) -> SuccessResponse:
        ok, msg = PasswordService.is_password_strong(body.new_password)
        if not ok:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=msg,
                                headers={"X-Error-Code": ErrorCodes.WEAK_PASSWORD})
        try:
            payload = JWTService.verify_token(body.token, token_type="password_reset")
        except JWTError:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token",
                                headers={"X-Error-Code": ErrorCodes.AUTH_INVALID_TOKEN})
        user = await ClientModel.get_or_none(id=payload["sub"])
        if not user:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")
        user.password_hashed = PasswordService.hash_password(body.new_password)
        user.last_login_at = datetime.now(timezone.utc)
        await user.save(update_fields=["password_hashed", "last_login_at"])
        # Force logout everywhere after a password change.
        await token_denylist.deny_all_for_user(user.id, ttl_seconds=settings.refresh_token_ttl_seconds)
        return SuccessResponse(message="Password reset successfully. Please log in again.")
