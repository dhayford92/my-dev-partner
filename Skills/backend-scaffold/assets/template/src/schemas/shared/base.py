"""
Base schema + pagination helpers + the ErrorCodes catalog.
ErrorCodes values are used as X-Error-Code header values (not a response envelope).
"""
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class BaseSchema(BaseModel):
    """Base for response schemas — enables ORM attribute reads + enum-to-value."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True, use_enum_values=True)


class PaginationParams(BaseModel):
    page: int = Field(ge=1, default=1)
    limit: int = Field(ge=1, le=100, default=50)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.limit


class PaginatedResponse(BaseModel, Generic[T]):
    """Mandatory list envelope: {data, current_page, page_limit, total_count}."""
    data: list[T]
    current_page: int = Field(ge=1, default=1)
    page_limit: int = Field(ge=1, le=100, default=50)
    total_count: int = Field(ge=0, default=0)

    @property
    def total_pages(self) -> int:
        if self.total_count == 0:
            return 0
        return (self.total_count + self.page_limit - 1) // self.page_limit

    @property
    def has_next(self) -> bool:
        return self.current_page < self.total_pages


def create_paginated_response(data: list, page: int, limit: int, total_count: int) -> PaginatedResponse:
    return PaginatedResponse(data=data, current_page=page, page_limit=limit, total_count=total_count)


class ErrorCodes:
    """Stable machine codes — sent via the X-Error-Code response header when the
    frontend needs to branch on an error. Extend per project."""
    # Auth
    AUTH_INVALID_CREDENTIALS = "AUTH_INVALID_CREDENTIALS"
    AUTH_INVALID_TOKEN = "AUTH_INVALID_TOKEN"
    AUTH_TOKEN_EXPIRED = "AUTH_TOKEN_EXPIRED"
    AUTH_UNAUTHORIZED = "AUTH_UNAUTHORIZED"
    AUTH_FORBIDDEN = "AUTH_FORBIDDEN"
    ACCOUNT_BLOCKED = "ACCOUNT_BLOCKED"
    EMAIL_IN_USE = "EMAIL_IN_USE"
    WEAK_PASSWORD = "WEAK_PASSWORD"
    OTP_EXPIRED = "OTP_EXPIRED"
    OTP_INVALID = "OTP_INVALID"
    # Resource
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    RESOURCE_ALREADY_EXISTS = "RESOURCE_ALREADY_EXISTS"
    RESOURCE_CONFLICT = "RESOURCE_CONFLICT"
    # Validation
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_INPUT = "INVALID_INPUT"
    # Server
    INTERNAL_ERROR = "INTERNAL_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
