"""
Roles & permissions (RBAC) — optional module, seeded by scripts/seed.py.

Default authorization is persona guards (user_type). This relational Role/permission model
is provided for admin projects that need configurable, fine-grained access. Permissions are
stored as a JSON map: {"<module>": {"read": bool, "write": bool, "delete": bool}}.
"""
from tortoise import fields
from tortoise.models import Model


class RoleModel(Model):
    id = fields.UUIDField(pk=True)
    name = fields.CharField(max_length=100, unique=True)
    description = fields.TextField(null=True)

    # {"users": {"read": true, "write": true, "delete": false}, ...}
    permissions = fields.JSONField(default=dict)

    is_active = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "roles"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def has_permission(self, module: str, action: str) -> bool:
        if not self.is_active:
            return False
        return bool(self.permissions.get(module, {}).get(action, False))
