"""
JWT service — token issuance and verification (python-jose, HS256).
"""
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt

from configs.settings import settings


class JWTService:
    ALGORITHM = "HS256"

    @staticmethod
    def create_access_token(
        user_id: uuid.UUID,
        user_type: str | None = None,
        type: str = "access",
        additional_claims: dict[str, Any] | None = None,
    ) -> tuple[str, str, datetime]:
        """Return (token, jti, expires_at)."""
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        jti = str(uuid.uuid4())
        payload: dict[str, Any] = {
            "sub": str(user_id), "jti": jti, "iat": now, "exp": expires_at,
            "iss": settings.JWT_ISSUER, "aud": settings.JWT_AUDIENCE, "type": type,
        }
        if user_type:
            payload["user_type"] = user_type
        if additional_claims:
            payload.update(additional_claims)
        token = jwt.encode(payload, settings.API_SECRET_KEY, algorithm=JWTService.ALGORITHM)
        return token, jti, expires_at

    @staticmethod
    def create_refresh_token(
        user_id: uuid.UUID,
        session_id: uuid.UUID | None = None,
        user_type: str | None = None,
    ) -> tuple[str, str, datetime]:
        """Return (token, jti, expires_at)."""
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        jti = str(uuid.uuid4())
        payload: dict[str, Any] = {
            "sub": str(user_id), "jti": jti, "iat": now, "exp": expires_at,
            "iss": settings.JWT_ISSUER, "aud": settings.JWT_AUDIENCE, "type": "refresh",
        }
        if session_id:
            payload["session_id"] = str(session_id)
        if user_type:
            payload["user_type"] = user_type
        token = jwt.encode(payload, settings.API_SECRET_KEY, algorithm=JWTService.ALGORITHM)
        return token, jti, expires_at

    @staticmethod
    def verify_token(token: str, token_type: str = "access") -> dict[str, Any]:
        """Decode + validate a token. Raises JWTError on failure."""
        payload = jwt.decode(
            token, settings.API_SECRET_KEY, algorithms=[JWTService.ALGORITHM],
            audience=settings.JWT_AUDIENCE, issuer=settings.JWT_ISSUER,
        )
        if payload.get("type") != token_type:
            raise JWTError(f"Invalid token type. Expected {token_type}")
        return payload

    @staticmethod
    def decode_token_unsafe(token: str) -> dict[str, Any]:
        """Decode WITHOUT verification — only for reading claims off expired tokens."""
        try:
            return jwt.decode(
                token, settings.API_SECRET_KEY, algorithms=[JWTService.ALGORITHM],
                options={"verify_signature": False, "verify_exp": False, "verify_aud": False},
            )
        except JWTError:
            return {}
