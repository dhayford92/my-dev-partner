"""
Example router — full CRUD. Final paths: /core/api/v1/admin/examples/...
Delete once you add real domains; copy its shape for new resources.
"""
from uuid import UUID

from fastapi import APIRouter, Depends, Request

from configs.rate_limiting import limiter, RateLimitConfig
from src.libs.auth import CurrentAdminUser
from src.schemas.shared.base import PaginationParams
from src.schemas.shared.responses import SuccessResponse
from src.schemas.core.example_schemas import (
    CreateExampleSchema, UpdateExampleSchema, ExampleDetailSchema, ExampleListSchema,
)
from src.apps.core.controllers.example_controller import ExampleController

router = APIRouter(prefix="/admin/examples", tags=["Examples"])


@router.get("", response_model=ExampleListSchema)
async def list_examples(auth: CurrentAdminUser, params: PaginationParams = Depends()):
    """List examples (paginated)."""
    return await ExampleController.list(params)


@router.get("/{example_id}", response_model=ExampleDetailSchema)
async def get_example(auth: CurrentAdminUser, example_id: UUID):
    """Get a single example."""
    return await ExampleController.get(example_id)


@router.post("", response_model=ExampleDetailSchema, status_code=201)
@limiter.limit(RateLimitConfig.CREATE_RESOURCE)
async def create_example(request: Request, auth: CurrentAdminUser, body: CreateExampleSchema):
    """Create an example."""
    return await ExampleController.create(body, auth.user_id, request)


@router.patch("/{example_id}", response_model=ExampleDetailSchema)
async def update_example(request: Request, auth: CurrentAdminUser, example_id: UUID,
                         body: UpdateExampleSchema):
    """Update an example."""
    return await ExampleController.update(example_id, body, auth.user_id, request)


@router.delete("/{example_id}", response_model=SuccessResponse)
async def delete_example(request: Request, auth: CurrentAdminUser, example_id: UUID):
    """Soft-delete an example."""
    return await ExampleController.delete(example_id, auth.user_id, request)
