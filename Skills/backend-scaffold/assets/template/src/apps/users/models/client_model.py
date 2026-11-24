"""
Client (end-user) model.
"""
from tortoise import fields
from tortoise.models import Model

from src.apps.users.models.user_enum import AccountStatus


class ClientModel(Model):
    id = fields.UUIDField(pk=True)

    full_name = fields.CharField(max_length=250, null=True)
    email = fields.CharField(max_length=250, unique=True, index=True)
    phone = fields.CharField(max_length=20, null=True, unique=True, index=True)
    password_hashed = fields.TextField()
    profile_picture = fields.TextField(null=True)

    status = fields.CharEnumField(AccountStatus, max_length=50, default=AccountStatus.ACTIVE)
    is_verified = fields.BooleanField(default=False)

    last_login_at = fields.DatetimeField(null=True)
    deleted_at = fields.DatetimeField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "client_users"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Client({self.email})"

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None
