"""
Org-scoped RBAC role model (opt-in). Drop into src/apps/users/models/ and register in
ORM_MODELS. Permissions are a JSON map {module: {read, write, delete}}. Roles are scoped to
an organization and assigned to users via M2M.

Requires an OrganizationModel and the user model you attach roles to (here ClientUserModel).
Adjust the model refs to your project.
"""
from enum import StrEnum

from tortoise import fields
from tortoise.models import Model


class PermissionModule(StrEnum):
    DASHBOARD = "dashboard"
    USERS = "users"
    RISK = "risk"
    GOVERNANCE = "governance"
    COMPLIANCE = "compliance"
    IAM = "iam"


class PermissionAction(StrEnum):
    READ = "read"
    WRITE = "write"
    DELETE = "delete"


class UserRoleModel(Model):
    id = fields.UUIDField(pk=True)
    organization = fields.ForeignKeyField("models.OrganizationModel", related_name="user_roles")
    name = fields.CharField(max_length=100)
    description = fields.TextField(null=True)

    # {"dashboard": {"read": true, "write": false, "delete": false}, ...}
    permissions = fields.JSONField(default=dict)

    users = fields.ManyToManyField("models.ClientUserModel", related_name="roles",
                                   through="userrole_users")
    is_active = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "user_roles"
        ordering = ["-created_at"]
        unique_together = [("organization", "name")]

    def __str__(self):
        return self.name

    def has_permission(self, module: str, action: str) -> bool:
        if not self.is_active:
            return False
        return bool(self.permissions.get(module, {}).get(action, False))


# Default roles seeded per organization. Permissions shaped as {module: {read/write/delete}}.
def _perm(read=False, write=False, delete=False) -> dict:
    return {"read": read, "write": write, "delete": delete}


DEFAULT_ROLE_LIST = [
    {"name": "Super Admin", "description": "Full control.",
     "permissions": {m.value: _perm(True, True, True) for m in PermissionModule}},
    {"name": "Manager", "description": "Manage all modules; read-only IAM.",
     "permissions": {**{m.value: _perm(True, True, True) for m in PermissionModule},
                     "iam": _perm(read=True)}},
    {"name": "Officer", "description": "Operate risk & compliance.",
     "permissions": {"dashboard": _perm(True, True), "iam": _perm(read=True),
                     "compliance": _perm(True, True, True), "risk": _perm(True, True, True),
                     "governance": _perm(read=True), "users": _perm(read=True)}},
    {"name": "Auditor", "description": "Read-only everywhere.",
     "permissions": {m.value: _perm(read=True) for m in PermissionModule}},
]
