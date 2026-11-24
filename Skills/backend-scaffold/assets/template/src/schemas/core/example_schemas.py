"""
Example resource schemas — the naming taxonomy in practice.
Delete alongside the example model once you add real domains.
"""
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field

from src.schemas.shared.base import BaseSchema, PaginatedResponse


class CreateExampleSchema(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None


class UpdateExampleSchema(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None


class ExampleTableSchema(BaseSchema):
    id: UUID
    name: str
    created_at: datetime


class ExampleDetailSchema(ExampleTableSchema):
    description: str | None = None
    updated_at: datetime


class ExampleListSchema(PaginatedResponse[ExampleTableSchema]):
    pass
