"""
Auth request/response schemas for admin + client users.
"""
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from src.schemas.shared.base import BaseSchema


# ── Requests ─────────────────────────────────────────────────────────────────
class RegisterSchema(BaseModel):
    full_name: str = Field(min_length=1, max_length=250)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginSchema(BaseModel):
    email: EmailStr
    password: str


# ── Responses ────────────────────────────────────────────────────────────────
class UserResponse(BaseSchema):
    id: UUID
    full_name: str | None = None
    email: str
    is_verified: bool = False


class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int
    user: UserResponse
