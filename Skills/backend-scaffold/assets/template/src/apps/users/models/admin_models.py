"""
Admin (portal) user model.
"""
from tortoise import fields
from tortoise.models import Model

from src.apps.users.models.user_enum import AdminRole, AccountStatus


class AdminModel(Model):
    id = fields.UUIDField(pk=True)

    full_name = fields.CharField(max_length=250)
    email = fields.CharField(max_length=250, unique=True, index=True)
    password_hashed = fields.TextField()

    role = fields.CharEnumField(AdminRole, max_length=50, default=AdminRole.ADMIN)
    status = fields.CharEnumField(AccountStatus, max_length=50, default=AccountStatus.ACTIVE)
    is_verified = fields.BooleanField(default=False)

    created_by_id = fields.UUIDField(null=True)
    last_login_at = fields.DatetimeField(null=True)
    deleted_at = fields.DatetimeField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    # Roles (RBAC) — optional, seeded. See role_model.py
    roles = fields.ManyToManyField("models.RoleModel", related_name="admins", through="admin_roles")

    class Meta:
        table = "admin_users"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Admin({self.email})"

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None
