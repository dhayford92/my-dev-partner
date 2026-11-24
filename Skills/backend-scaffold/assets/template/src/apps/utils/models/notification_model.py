"""
Notification model.
"""
from tortoise import fields
from tortoise.models import Model


class Notification(Model):
    id = fields.UUIDField(pk=True)
    user_id = fields.UUIDField(index=True)
    user_type = fields.CharField(max_length=20, default="client")

    title = fields.CharField(max_length=255)
    body = fields.TextField(null=True)
    data = fields.JSONField(default=dict)

    is_read = fields.BooleanField(default=False)
    read_at = fields.DatetimeField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "notifications"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Notification({self.title})"
