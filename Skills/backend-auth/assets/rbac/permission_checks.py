"""
RBAC permission checks (opt-in). Drop into src/services/auth/ (or src/libs/).

Controllers call `UserPermissionChecks.has_client_user_permission(email, module, action)`
which returns {"user_id", "organization_id"} when allowed, else None. Then scope every query
by the returned organization_id. This is the org-scoped check: authorization happens
INSIDE the controller (not only in a route dependency), because permissions are data-driven.

Adjust ClientUserModel / role relation names to your project.
"""
import logging

from src.apps.users.models.client_models import ClientUserModel

logger = logging.getLogger(__name__)


class UserPermissionChecks:
    @staticmethod
    async def has_client_user_permission(email: str, module: str, action: str) -> dict | None:
        """Return {user_id, organization_id} if the user has (module, action), else None."""
        user = await ClientUserModel.get_or_none(email=email).prefetch_related("roles")
        if not user or getattr(user, "deleted_at", None):
            return None
        for role in user.roles:
            if role.is_active and role.has_permission(module, action):
                return {"user_id": str(user.id), "organization_id": str(user.organization_id)}
        return None
