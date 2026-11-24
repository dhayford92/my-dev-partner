"""
Token request/response schemas.
"""
from pydantic import BaseModel


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str | None = None
    expires_in: int


class RefreshRequest(BaseModel):
    refresh_token: str
