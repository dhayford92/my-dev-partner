"""
Example controller — full CRUD with the canonical pagination envelope + activity logging.
Delete once you add real domains; copy its shape for new resources.
"""
import logging
from uuid import UUID
from datetime import datetime, timezone

from fastapi import HTTPException, status, Request

from src.apps.core.models.example_model import ExampleModel
from src.schemas.shared.base import ErrorCodes, PaginationParams, create_paginated_response
from src.schemas.shared.responses import SuccessResponse
from src.schemas.core.example_schemas import (
    CreateExampleSchema, UpdateExampleSchema, ExampleDetailSchema,
    ExampleTableSchema, ExampleListSchema,
)
from src.services.activity.activity_service import ActivityService

logger = logging.getLogger(__name__)


class ExampleController:
    @staticmethod
    async def list(params: PaginationParams) -> ExampleListSchema:
        qs = ExampleModel.filter(deleted_at=None)
        total = await qs.count()
        rows = await qs.order_by("-created_at").offset(params.offset).limit(params.limit)
        return create_paginated_response(
            [ExampleTableSchema.model_validate(r) for r in rows],
            params.page, params.limit, total,
        )

    @staticmethod
    async def get(example_id: UUID) -> ExampleDetailSchema:
        row = await ExampleModel.get_or_none(id=example_id, deleted_at=None)
        if not row:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Example not found",
                                headers={"X-Error-Code": ErrorCodes.RESOURCE_NOT_FOUND})
        return ExampleDetailSchema.model_validate(row)

    @staticmethod
    async def create(body: CreateExampleSchema, actor_id: UUID, request: Request) -> ExampleDetailSchema:
        try:
            row = await ExampleModel.create(name=body.name, description=body.description)
            await ActivityService.log_create(actor_id, "example", row.id, row.name, request=request)
            return ExampleDetailSchema.model_validate(row)
        except HTTPException:
            raise
        except Exception as e:  # noqa: BLE001
            logger.error(f"Example create error: {e}")
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create example")

    @staticmethod
    async def update(example_id: UUID, body: UpdateExampleSchema, actor_id: UUID,
                     request: Request) -> ExampleDetailSchema:
        row = await ExampleModel.get_or_none(id=example_id, deleted_at=None)
        if not row:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Example not found",
                                headers={"X-Error-Code": ErrorCodes.RESOURCE_NOT_FOUND})
        changes = body.model_dump(exclude_none=True)
        for field, value in changes.items():
            setattr(row, field, value)
        await row.save()
        await ActivityService.log_update(actor_id, "example", row.id, row.name,
                                         changes=changes, request=request)
        return ExampleDetailSchema.model_validate(row)

    @staticmethod
    async def delete(example_id: UUID, actor_id: UUID, request: Request) -> SuccessResponse:
        row = await ExampleModel.get_or_none(id=example_id, deleted_at=None)
        if not row:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Example not found",
                                headers={"X-Error-Code": ErrorCodes.RESOURCE_NOT_FOUND})
        row.deleted_at = datetime.now(timezone.utc)
        await row.save(update_fields=["deleted_at"])
        await ActivityService.log_delete(actor_id, "example", row.id, row.name, request=request)
        return SuccessResponse(message="Example deleted successfully")
