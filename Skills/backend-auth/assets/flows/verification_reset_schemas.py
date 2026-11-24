"""
Email-verification + password-reset schemas. Drop into src/schemas/users/.
"""
from pydantic import BaseModel, EmailStr, Field


class RequestVerificationSchema(BaseModel):
    email: EmailStr


class VerifyEmailSchema(BaseModel):
    token: str


class ForgotPasswordSchema(BaseModel):
    email: EmailStr


class ResetPasswordSchema(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)
