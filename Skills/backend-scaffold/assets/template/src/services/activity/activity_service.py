"""
Activity service — admin audit trail. Log every mutation in the same controller method
that made the change. Free-form metadata is redacted before storage.
"""
import logging
from uuid import UUID

from starlette.requests import Request

from src.apps.utils.models.activity_model import ActivityLog
from src.apps.users.models.user_enum import ActivityAction
from src.libs.redaction import redact

logger = logging.getLogger(__name__)


class ActivityService:
    @staticmethod
    async def log(
        user_id: UUID,
        action: ActivityAction,
        resource_type: str,
        resource_id: UUID | None = None,
        resource_name: str | None = None,
        user_type: str = "admin",
        metadata: dict | None = None,
        request: Request | None = None,
    ) -> ActivityLog:
        ip_address = None
        user_agent = None
        if request:
            fwd = request.headers.get("x-forwarded-for")
            ip_address = fwd.split(",")[0].strip() if fwd else (request.client.host if request.client else None)
            user_agent = request.headers.get("user-agent")
        try:
            return await ActivityLog.create(
                user_id=user_id,
                user_type=user_type,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                resource_name=resource_name,
                metadata=redact(metadata or {}),
                ip_address=ip_address,
                user_agent=user_agent,
            )
        except Exception as e:  # noqa: BLE001
            logger.error(f"Failed to log activity: {e}")
            raise

    @staticmethod
    async def log_create(user_id, resource_type, resource_id, resource_name,
                         user_type="admin", metadata=None, request=None):
        return await ActivityService.log(user_id, ActivityAction.CREATE, resource_type,
                                         resource_id, resource_name, user_type, metadata, request)

    @staticmethod
    async def log_update(user_id, resource_type, resource_id, resource_name,
                         user_type="admin", changes=None, request=None):
        return await ActivityService.log(user_id, ActivityAction.UPDATE, resource_type,
                                         resource_id, resource_name, user_type,
                                         {"changes": changes} if changes else None, request)

    @staticmethod
    async def log_delete(user_id, resource_type, resource_id, resource_name,
                         user_type="admin", request=None):
        return await ActivityService.log(user_id, ActivityAction.DELETE, resource_type,
                                         resource_id, resource_name, user_type, None, request)


activity_service = ActivityService()
