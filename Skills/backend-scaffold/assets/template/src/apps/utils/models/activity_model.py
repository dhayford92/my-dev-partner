"""
Activity log — audit trail for mutations.
"""
from tortoise import fields
from tortoise.models import Model

from src.apps.users.models.user_enum import ActivityAction


class ActivityLog(Model):
    id = fields.UUIDField(pk=True)
    user_id = fields.UUIDField(index=True)
    user_type = fields.CharField(max_length=20, default="admin")

    action = fields.CharEnumField(ActivityAction, max_length=50)
    resource_type = fields.CharField(max_length=100)
    resource_id = fields.UUIDField(null=True)
    resource_name = fields.CharField(max_length=255, null=True)

    metadata = fields.JSONField(default=dict)
    ip_address = fields.CharField(max_length=50, null=True)
    user_agent = fields.TextField(null=True)

    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "activity_logs"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Activity({self.action}, {self.resource_type})"
